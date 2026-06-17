import copy
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from . import config
from .frame_extractor import (
    DEFAULT_FRAME_RATE,
    DEFAULT_JPEG_QUALITY,
    estimate_disk_usage_bytes,
    estimate_frame_count,
    is_video_path,
    normalize_frame_extraction_settings,
    normalize_frame_rate,
    normalize_jpeg_quality,
    read_video_metadata,
)
from .transcript_store import safe_filename_part, source_stem_for
from .utils import audio_duration_seconds, timestamp_for_filename, write_json_file_atomic


logger = logging.getLogger(__name__)

TERMINAL_STATUSES = {"completed", "error", "failed", "cancelled"}
ACTIVE_STATUSES = {"downloading", "downloaded", "analyzing", "extracting_audio", "transcribing", "extracting_frames"}


@dataclass(frozen=True)
class QueueFile:
    source_path: Path
    source_filename: str
    source_type: str = "local_file"
    operations: dict | None = None
    frame_extraction: dict | None = None


@dataclass(frozen=True)
class QueueUrl:
    source_url: str


class QueueManager:
    def __init__(
        self,
        *,
        jobs_dir: Path,
        processor: Callable[[dict, str, str], dict],
        error_recorder: Callable[[dict, str, str, Exception], dict] | None = None,
        duration_reader: Callable[[Path], float | None] = audio_duration_seconds,
        media_validator: Callable[[Path], None] | None = None,
        downloader: Callable[[str], dict] | None = None,
        video_downloader: Callable[[str], dict] | None = None,
        frame_processor: Callable[[dict, threading.Event, Callable[[dict], None]], dict] | None = None,
        video_metadata_reader: Callable[[Path], dict] | None = read_video_metadata,
    ) -> None:
        self.jobs_dir = jobs_dir
        self.processor = processor
        self.error_recorder = error_recorder
        self.duration_reader = duration_reader
        self.media_validator = media_validator or (lambda _path: None)
        self.downloader = downloader
        self.video_downloader = video_downloader
        self.frame_processor = frame_processor
        self.video_metadata_reader = video_metadata_reader

        self._lock = threading.RLock()
        self._items: list[dict] = []
        self._job_id: str | None = None
        self._job_path: Path | None = None
        self._created_at: str | None = None
        self._started_at: str | None = None
        self._finished_at: str | None = None
        self._model: str | None = None
        self._device_preference: str | None = None
        self._status = "empty"
        self._current_index: int | None = None
        self._stop_after_current = False
        self._worker: threading.Thread | None = None
        self._cancel_events: dict[int, threading.Event] = {}

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._is_running_locked()

    def add_files(self, files: list[QueueFile]) -> dict:
        if not files:
            raise RuntimeError("Выберите хотя бы один файл для очереди.")

        with self._lock:
            self._ensure_inactive_locked("Нельзя добавлять файлы во время обработки очереди.")
            if self._job_id is None:
                self._create_job_locked()

            start_index = len(self._items) + 1
            for offset, queue_file in enumerate(files):
                item = self._new_file_item_locked(start_index + offset, queue_file)
                self._items.append(item)

            self._status = "pending"
            self._finished_at = None
            self._persist_locked()
            logger.info(
                "Queue files added: job_id=%s added=%s total=%s job_json=%s",
                self._job_id,
                len(files),
                len(self._items),
                self._job_path,
            )
            return self._status_snapshot_locked()

    def add_urls(self, urls: list[QueueUrl]) -> dict:
        if not urls:
            raise RuntimeError("Добавьте хотя бы одну ссылку для очереди.")

        with self._lock:
            self._ensure_inactive_locked("Нельзя добавлять ссылки во время обработки очереди.")
            if self._job_id is None:
                self._create_job_locked()

            start_index = len(self._items) + 1
            for offset, queue_url in enumerate(urls):
                source_url = queue_url.source_url.strip()
                if not source_url:
                    raise RuntimeError("Пустые ссылки нельзя добавить в очередь.")
                index = start_index + offset
                item = {
                    "index": index,
                    "source_type": "url",
                    "media_kind": "url",
                    "source_url": source_url,
                    "source_title": None,
                    "source_platform": "unknown",
                    "source_path": None,
                    "source_filename": f"url_{index:03d}",
                    "downloaded_audio_path": None,
                    "downloaded_media_path": None,
                    "downloaded_video_path": None,
                    "status": "pending",
                    "operations": self._default_operations("url"),
                    "frame_extraction": None,
                    "video_metadata": None,
                    "video_metadata_error": None,
                    "audio_duration_sec": None,
                    "processing_time_sec": None,
                    "realtime_factor": None,
                    "transcript_path": None,
                    "json_path": None,
                    "frames_dir": None,
                    "frames_path": None,
                    "frames_index_path": None,
                    "extracted_frame_count": None,
                    "frame_extraction_result": None,
                    "output_base": None,
                    "error_message": None,
                    "technical_details": None,
                }
                item["frame_extraction"] = self._frame_extraction_payload(item, normalize_frame_extraction_settings(None))
                self._refresh_frame_estimate_locked(item)
                self._items.append(item)

            self._status = "pending"
            self._finished_at = None
            self._persist_locked()
            logger.info("Queue URLs added: job_id=%s added=%s total=%s", self._job_id, len(urls), len(self._items))
            return self._status_snapshot_locked()

    def start(self, model: str, device_preference: str = "auto") -> dict:
        with self._lock:
            self._ensure_inactive_locked("Очередь уже выполняется.")
            if not any(item["status"] == "pending" for item in self._items):
                raise RuntimeError("В очереди нет ожидающих задач.")

            self._validate_pending_operations_locked()
            self._model = model
            self._device_preference = device_preference
            self._started_at = self._started_at or self._now()
            self._finished_at = None
            self._stop_after_current = False
            self._status = "running"
            self._persist_locked()
            self._worker = threading.Thread(
                target=self._worker_loop,
                name="local-file-queue",
                daemon=True,
            )
            self._worker.start()
            logger.info(
                "Queue started: job_id=%s model=%s device=%s items=%s",
                self._job_id,
                model,
                device_preference,
                len(self._items),
            )
            return self._status_snapshot_locked()

    def stop_after_current(self) -> dict:
        with self._lock:
            if not self._is_running_locked():
                raise RuntimeError("Очередь сейчас не выполняется.")
            self._stop_after_current = True
            self._persist_locked()
            logger.info("Queue stop-after-current requested: job_id=%s", self._job_id)
            return self._status_snapshot_locked()

    def clear(self) -> dict:
        with self._lock:
            self._ensure_inactive_locked("Нельзя очистить очередь во время обработки.")
            logger.info("Queue cleared: job_id=%s items=%s", self._job_id, len(self._items))
            self._items = []
            self._job_id = None
            self._job_path = None
            self._created_at = None
            self._started_at = None
            self._finished_at = None
            self._model = None
            self._device_preference = None
            self._status = "empty"
            self._current_index = None
            self._stop_after_current = False
            self._worker = None
            return self._status_snapshot_locked()

    def retry_errors(self) -> dict:
        with self._lock:
            self._ensure_inactive_locked("Нельзя повторить задачи во время обработки очереди.")
            failed_items = [item for item in self._items if item["status"] in {"error", "failed"}]
            if not failed_items:
                raise RuntimeError("В очереди нет ошибочных задач для повтора.")

            for item in failed_items:
                item.update(
                    {
                        "status": "pending",
                        "processing_time_sec": None,
                        "realtime_factor": None,
                        "transcript_path": None,
                        "json_path": None,
                        "frames_dir": None,
                        "frames_path": None,
                        "frames_index_path": None,
                        "extracted_frame_count": None,
                        "frame_extraction_result": None,
                        "error_message": None,
                        "technical_details": None,
                    }
                )
                if item.get("frame_extraction") is not None:
                    item["frame_extraction"]["result"] = None
            self._status = "pending"
            self._finished_at = None
            self._persist_locked()
            logger.info("Queue failed items prepared for retry: job_id=%s items=%s", self._job_id, len(failed_items))
            return self._status_snapshot_locked()

    def status(self) -> dict:
        with self._lock:
            return self._status_snapshot_locked()

    def update_item(
        self,
        index: int,
        *,
        operations: dict | None = None,
        frame_extraction: dict | None = None,
    ) -> dict:
        with self._lock:
            self._ensure_inactive_locked("Нельзя менять параметры задач во время обработки очереди.")
            item = self._find_item_locked(index)
            if item["status"] != "pending":
                raise RuntimeError("Можно менять только ожидающие задачи очереди.")

            media_kind = item.get("media_kind") or self._media_kind_for(item.get("source_path") or item["source_filename"])
            if operations is not None:
                item["operations"] = self._normalize_operations(operations, media_kind)
            if frame_extraction is not None:
                item["frame_extraction"] = self._frame_extraction_payload(
                    item,
                    normalize_frame_extraction_settings(frame_extraction),
                )
            self._refresh_frame_estimate_locked(item)
            self._persist_locked()
            logger.info("Queue item updated: job_id=%s index=%s", self._job_id, index)
            return self._status_snapshot_locked()

    def remove_item(self, index: int) -> dict:
        with self._lock:
            item = self._find_item_locked(index)
            if item["status"] != "pending":
                raise RuntimeError("Можно удалить только ожидающую задачу очереди.")

            self._items = [entry for entry in self._items if entry["index"] != index]
            if not self._items and not self._is_running_locked():
                self._status = "empty"
                self._job_id = None
                self._job_path = None
                self._created_at = None
                self._started_at = None
                self._finished_at = None
                self._model = None
                self._device_preference = None
                self._current_index = None
                self._stop_after_current = False
            elif not self._is_running_locked() and any(entry["status"] == "pending" for entry in self._items):
                self._status = "pending"
            self._persist_locked()
            logger.info("Queue item removed: job_id=%s index=%s", self._job_id, index)
            return self._status_snapshot_locked()

    def cancel_item(self, index: int) -> dict:
        with self._lock:
            item = self._find_item_locked(index)
            if self._current_index != index:
                if item["status"] == "pending":
                    return self.remove_item(index)
                if item["status"] in TERMINAL_STATUSES:
                    return self._status_snapshot_locked()
                raise RuntimeError("Эта задача сейчас не выполняется.")

            if item["status"] != "extracting_frames":
                raise RuntimeError("Текущую аудио-транскрибацию нельзя безопасно отменить на этом этапе.")

            cancel_event = self._cancel_events.get(index)
            if cancel_event is not None:
                cancel_event.set()
            item["cancel_requested"] = True
            self._persist_locked()
            logger.info("Queue item cancellation requested: job_id=%s index=%s", self._job_id, index)
            return self._status_snapshot_locked()

    def wait(self, timeout: float | None = None) -> None:
        with self._lock:
            worker = self._worker
        if worker is not None:
            worker.join(timeout=timeout)

    def _new_file_item_locked(self, index: int, queue_file: QueueFile) -> dict:
        media_kind = self._media_kind_for(queue_file.source_path)
        settings = normalize_frame_extraction_settings(queue_file.frame_extraction)
        item = {
            "index": index,
            "source_type": queue_file.source_type,
            "media_kind": media_kind,
            "source_path": str(queue_file.source_path),
            "source_filename": queue_file.source_filename,
            "status": "pending",
            "operations": self._normalize_operations(queue_file.operations, media_kind),
            "frame_extraction": None,
            "video_metadata": None,
            "video_metadata_error": None,
            "audio_duration_sec": None,
            "processing_time_sec": None,
            "realtime_factor": None,
            "transcript_path": None,
            "json_path": None,
            "frames_dir": None,
            "frames_path": None,
            "frames_index_path": None,
            "extracted_frame_count": None,
            "frame_extraction_result": None,
            "output_base": None,
            "error_message": None,
            "technical_details": None,
        }
        if media_kind == "video":
            item["frame_extraction"] = self._frame_extraction_payload(item, settings)
            self._refresh_video_analysis_locked(item)
        return item

    @staticmethod
    def _media_kind_for(path_or_name: Path | str) -> str:
        return "video" if is_video_path(path_or_name) else "audio"

    @staticmethod
    def _default_operations(media_kind: str) -> dict:
        return {
            "transcribe_audio": True,
            "extract_frames": False,
            "ocr": False,
            "cv": False,
        }

    def _normalize_operations(self, operations: dict | None, media_kind: str) -> dict:
        normalized = self._default_operations(media_kind)
        if operations:
            for key in normalized:
                if key in operations:
                    normalized[key] = bool(operations[key])
        if normalized.get("ocr"):
            raise RuntimeError("OCR is not implemented yet.")
        if normalized.get("cv"):
            raise RuntimeError("CV is not implemented yet.")
        if media_kind not in {"video", "url"}:
            normalized["extract_frames"] = False
            normalized["ocr"] = False
            normalized["cv"] = False
        return normalized

    def _frame_extraction_payload(self, item: dict, settings: dict) -> dict:
        payload = item.get("frame_extraction") or {}
        payload.update(
            {
                "rate": normalize_frame_rate(settings.get("rate")),
                "jpeg_quality": normalize_jpeg_quality(settings.get("jpeg_quality")),
                "estimated_frame_count": None,
                "estimated_disk_usage": None,
                "estimated_frames_warning": False,
                "result": payload.get("result"),
            }
        )
        return payload

    def _refresh_video_analysis_locked(self, item: dict) -> None:
        if not self._item_supports_frame_extraction(item):
            return
        if not item.get("source_path"):
            self._refresh_frame_estimate_locked(item)
            return
        if item.get("source_type") == "url" and not item.get("operations", {}).get("extract_frames"):
            self._refresh_frame_estimate_locked(item)
            return
        if self.video_metadata_reader is None:
            self._refresh_frame_estimate_locked(item)
            return
        try:
            metadata = self.video_metadata_reader(Path(item["source_path"]))
            item["video_metadata"] = metadata
            item["video_metadata_error"] = None
        except Exception as exc:
            item["video_metadata"] = None
            item["video_metadata_error"] = str(exc)
        self._refresh_frame_estimate_locked(item)

    def _refresh_frame_estimate_locked(self, item: dict) -> None:
        frame_settings = item.get("frame_extraction")
        if not self._item_supports_frame_extraction(item) or not frame_settings:
            return
        metadata = item.get("video_metadata") or {}
        estimated_count = estimate_frame_count(metadata.get("duration_sec"), frame_settings.get("rate"))
        frame_settings["estimated_frame_count"] = estimated_count
        frame_settings["estimated_disk_usage"] = estimate_disk_usage_bytes(
            estimated_count,
            metadata.get("width"),
            metadata.get("height"),
            frame_settings.get("jpeg_quality"),
        )
        frame_settings["estimated_frames_warning"] = bool(estimated_count and estimated_count > 1000)

    def _validate_pending_operations_locked(self) -> None:
        for item in self._items:
            if item["status"] != "pending":
                continue
            media_kind = item.get("media_kind") or self._media_kind_for(item.get("source_path") or item["source_filename"])
            operations = item.get("operations") or self._default_operations(media_kind)
            if operations.get("ocr"):
                raise RuntimeError("OCR is not implemented yet.")
            if operations.get("cv"):
                raise RuntimeError("CV is not implemented yet.")
            if item.get("source_type") == "url" and not (operations.get("transcribe_audio") or operations.get("extract_frames")):
                raise RuntimeError("Выберите хотя бы одну операцию для этой ссылки.")
            if media_kind == "video" and not (operations.get("transcribe_audio") or operations.get("extract_frames")):
                raise RuntimeError("Выберите хотя бы одну операцию для этого видео.")

    @staticmethod
    def _item_supports_frame_extraction(item: dict) -> bool:
        return item.get("media_kind") == "video" or item.get("source_type") == "url"

    def _find_item_locked(self, index: int) -> dict:
        item = next((entry for entry in self._items if entry["index"] == index), None)
        if item is None:
            raise RuntimeError("Задача очереди не найдена.")
        return item

    def _frame_progress_callback(self, index: int) -> Callable[[dict], None]:
        def update(progress: dict) -> None:
            with self._lock:
                item = next((entry for entry in self._items if entry["index"] == index), None)
                if item is None:
                    return
                item["frame_extraction_result"] = progress
                item["extracted_frame_count"] = progress.get("extracted_frame_count")
                item["frames_dir"] = progress.get("frames_dir")
                item["frames_path"] = progress.get("frames_path")
                item["frames_index_path"] = progress.get("frames_index_path")
                frame_settings = item.get("frame_extraction")
                if frame_settings is not None:
                    frame_settings["result"] = progress
                self._persist_locked()

        return update

    @staticmethod
    def _output_base_from_transcript_path(transcript_path: str | None, model: str) -> str | None:
        if not transcript_path:
            return None
        stem = Path(transcript_path).stem
        safe_model = safe_filename_part(model, max_length=32)
        suffix = f"__{safe_model}__transcript"
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
        transcript_suffix = "__transcript"
        if stem.endswith(transcript_suffix):
            return stem[: -len(transcript_suffix)]
        return None

    @staticmethod
    def _frames_only_output_base(source_filename: str) -> str:
        return f"{source_stem_for(source_filename)}_{timestamp_for_filename()}"

    def _worker_loop(self) -> None:
        while True:
            with self._lock:
                item = next((entry for entry in self._items if entry["status"] == "pending"), None)
                if item is None:
                    self._finish_locked("completed")
                    return

                self._current_index = item["index"]
                item["status"] = "downloading" if item.get("source_type") == "url" else "analyzing"
                self._persist_locked()
                item_snapshot = copy.deepcopy(item)
                model = self._model or ""
                device_preference = self._device_preference or "auto"
                logger.info(
                    "Queue task started: job_id=%s index=%s source=%s model=%s device=%s",
                    self._job_id,
                    item["index"],
                    item.get("source_path") or item.get("source_url"),
                    model,
                    device_preference,
                )

            try:
                source_path = self._prepare_source(item, item_snapshot)
                task_cancelled = False
                task_failed = False
                with self._lock:
                    item["media_kind"] = item.get("media_kind") or self._media_kind_for(source_path)
                    if item["media_kind"] == "video" and item.get("frame_extraction") is None:
                        item["frame_extraction"] = self._frame_extraction_payload(
                            item,
                            {"rate": DEFAULT_FRAME_RATE, "jpeg_quality": DEFAULT_JPEG_QUALITY},
                        )
                    self._refresh_video_analysis_locked(item)
                    item["status"] = "analyzing"
                    self._persist_locked()
                    item_snapshot = copy.deepcopy(item)
                duration = self.duration_reader(source_path)
                with self._lock:
                    item["audio_duration_sec"] = self._rounded(duration) or item.get("audio_duration_sec")
                    self._persist_locked()

                operations = item_snapshot.get("operations") or self._default_operations(item_snapshot.get("media_kind", "audio"))
                transcript_result: dict = {}
                transcript_error: Exception | None = None
                if operations.get("transcribe_audio"):
                    try:
                        self.media_validator(source_path)
                        if source_path.suffix.lower() in config.SUPPORTED_VIDEO_EXTENSIONS:
                            with self._lock:
                                item["status"] = "extracting_audio"
                                self._persist_locked()

                        with self._lock:
                            item["status"] = "transcribing"
                            self._persist_locked()
                            item_snapshot = copy.deepcopy(item)

                        transcript_result = self.processor(item_snapshot, model, device_preference)
                        with self._lock:
                            output_base = self._output_base_from_transcript_path(
                                transcript_result.get("transcript_path"),
                                model,
                            )
                            item.update(
                                {
                                    "audio_duration_sec": transcript_result.get("audio_duration_sec", item["audio_duration_sec"]),
                                    "processing_time_sec": transcript_result.get("processing_time_sec"),
                                    "realtime_factor": transcript_result.get("realtime_factor"),
                                    "transcript_path": transcript_result.get("transcript_path"),
                                    "json_path": transcript_result.get("json_path") or transcript_result.get("benchmark_path"),
                                    "output_base": output_base or item.get("output_base"),
                                    "error_message": None,
                                    "technical_details": None,
                                }
                            )
                            self._persist_locked()
                    except Exception as exc:
                        if not operations.get("extract_frames"):
                            raise
                        transcript_error = exc
                        error_metadata: dict = {}
                        if self.error_recorder is not None:
                            try:
                                error_metadata = self.error_recorder(item_snapshot, model, device_preference, exc)
                            except Exception:
                                logger.exception("Failed to save queue transcription error JSON")
                        with self._lock:
                            item.update(
                                {
                                    "json_path": error_metadata.get("json_path")
                                    or error_metadata.get("benchmark_path")
                                    or item.get("json_path"),
                                    "error_message": str(exc),
                                    "technical_details": str(getattr(exc, "technical_details", "") or exc),
                                }
                            )
                            self._persist_locked()
                            item_snapshot = copy.deepcopy(item)

                frame_result: dict = {}
                if operations.get("extract_frames"):
                    if self.frame_processor is None:
                        raise RuntimeError("Frame extraction service is not configured.")
                    with self._lock:
                        item["status"] = "extracting_frames"
                        item["cancel_requested"] = False
                        if not item.get("output_base"):
                            item["output_base"] = self._frames_only_output_base(item["source_filename"])
                        self._persist_locked()
                        item_snapshot = copy.deepcopy(item)
                        cancel_event = threading.Event()
                        self._cancel_events[item["index"]] = cancel_event
                    try:
                        frame_result = self.frame_processor(
                            item_snapshot,
                            cancel_event,
                            self._frame_progress_callback(item["index"]),
                        )
                    finally:
                        with self._lock:
                            self._cancel_events.pop(item["index"], None)

                    with self._lock:
                        item["frame_extraction_result"] = frame_result
                        item["extracted_frame_count"] = frame_result.get("extracted_frame_count")
                        item["frames_dir"] = frame_result.get("frames_dir")
                        item["frames_path"] = frame_result.get("frames_path")
                        item["frames_index_path"] = frame_result.get("frames_index_path")
                        frame_settings = item.get("frame_extraction")
                        if frame_settings is not None:
                            frame_settings["result"] = frame_result
                        self._persist_locked()

                    if frame_result.get("status") == "cancelled":
                        with self._lock:
                            item.update(
                                {
                                    "status": "cancelled",
                                    "error_message": None,
                                    "technical_details": None,
                                }
                            )
                            self._persist_locked()
                            logger.info(
                                "Queue task cancelled: job_id=%s index=%s frames=%s",
                                self._job_id,
                                item["index"],
                                item.get("extracted_frame_count"),
                            )
                        task_cancelled = True
                    elif frame_result.get("status") == "failed":
                        if transcript_result.get("transcript_path") or item.get("transcript_path") or transcript_error:
                            error_message = frame_result.get("error_message") or "Frame extraction failed."
                            with self._lock:
                                item.update(
                                    {
                                        "status": "error",
                                        "error_message": error_message,
                                        "technical_details": error_message,
                                        "processing_time_sec": transcript_result.get("processing_time_sec") or item.get("processing_time_sec"),
                                    }
                                )
                                self._persist_locked()
                                logger.error(
                                    "Queue frame extraction failed after transcription: job_id=%s index=%s frames_dir=%s",
                                    self._job_id,
                                    item["index"],
                                    item.get("frames_dir"),
                                )
                            task_failed = True
                        else:
                            raise RuntimeError(frame_result.get("error_message") or "Frame extraction failed.")

                if not task_cancelled and not task_failed:
                    with self._lock:
                        combined_processing = transcript_result.get("processing_time_sec")
                        if transcript_error:
                            item.update(
                                {
                                    "status": "error",
                                    "error_message": str(transcript_error),
                                    "technical_details": str(getattr(transcript_error, "technical_details", "") or transcript_error),
                                    "processing_time_sec": combined_processing,
                                }
                            )
                        else:
                            item.update(
                                {
                                    "status": "completed",
                                    "error_message": None,
                                    "technical_details": None,
                                    "processing_time_sec": combined_processing,
                                }
                            )
                        self._persist_locked()
                        logger.info(
                            "Queue task completed: job_id=%s index=%s transcript=%s json=%s frames=%s duration=%s processing_time=%s realtime_factor=%s",
                            self._job_id,
                            item["index"],
                            item["transcript_path"],
                            item["json_path"],
                            item.get("extracted_frame_count"),
                            item["audio_duration_sec"],
                            item["processing_time_sec"],
                            item["realtime_factor"],
                        )
            except Exception as exc:
                error_metadata: dict = {}
                if self.error_recorder is not None:
                    try:
                        error_metadata = self.error_recorder(item_snapshot, model, device_preference, exc)
                    except Exception:
                        logger.exception("Failed to save queue task error JSON")

                with self._lock:
                    item.update(
                        {
                            "status": "error",
                            "transcript_path": error_metadata.get("transcript_path") or item.get("transcript_path"),
                            "json_path": error_metadata.get("json_path") or error_metadata.get("benchmark_path") or item.get("json_path"),
                            "error_message": str(exc),
                            "technical_details": str(getattr(exc, "technical_details", "") or exc),
                        }
                    )
                    self._persist_locked()
                    logger.exception(
                        "Queue task failed: job_id=%s index=%s file=%s",
                        self._job_id,
                        item["index"],
                        item.get("source_path") or item.get("source_url"),
                    )

            with self._lock:
                self._current_index = None
                if self._stop_after_current:
                    for pending_item in self._items:
                        if pending_item["status"] == "pending":
                            pending_item["status"] = "cancelled"
                    self._finish_locked("cancelled")
                    return
                self._persist_locked()

    def _finish_locked(self, status: str) -> None:
        self._current_index = None
        self._status = status
        self._finished_at = self._now()
        self._worker = None
        self._persist_locked()
        logger.info(
            "Queue finished: job_id=%s status=%s completed=%s failed=%s cancelled=%s",
            self._job_id,
            status,
            self._count_locked("completed"),
            self._count_failed_locked(),
            self._count_locked("cancelled"),
        )

    def _create_job_locked(self) -> None:
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        base_id = timestamp_for_filename()
        job_id = base_id
        counter = 2
        while (self.jobs_dir / f"job_{job_id}.json").exists():
            job_id = f"{base_id}_{counter}"
            counter += 1

        self._job_id = job_id
        self._job_path = self.jobs_dir / f"job_{job_id}.json"
        self._created_at = self._now()
        self._status = "pending"
        logger.info("Queue created: job_id=%s job_json=%s", self._job_id, self._job_path)

    def _status_snapshot_locked(self) -> dict:
        payload = self._job_payload_locked()
        total_items = payload["total_items"]
        finished_items = payload["completed_items"] + payload["failed_items"] + payload["cancelled_items"]
        elapsed_sec = self._elapsed_seconds_locked()
        eta_sec, eta_message = self._eta_locked()
        current_item = next((item for item in self._items if item["index"] == self._current_index), None)
        return {
            **payload,
            "job_path": str(self._job_path) if self._job_path else None,
            "pending_items": self._count_locked("pending"),
            "running_items": sum(1 for item in self._items if item["status"] in ACTIVE_STATUSES),
            "current_file": current_item["source_filename"] if current_item else None,
            "current_item": copy.deepcopy(current_item),
            "elapsed_sec": elapsed_sec,
            "eta_sec": eta_sec,
            "eta_message": eta_message,
            "progress_percent": round((finished_items / total_items) * 100, 1) if total_items else 0,
            "stop_after_current": self._stop_after_current,
        }

    def _job_payload_locked(self) -> dict:
        return {
            "job_id": self._job_id,
            "created_at": self._created_at,
            "started_at": self._started_at,
            "finished_at": self._finished_at,
            "model": self._model,
            "device_preference": self._device_preference,
            "status": self._status,
            "total_items": len(self._items),
            "completed_items": self._count_locked("completed"),
            "failed_items": self._count_failed_locked(),
            "cancelled_items": self._count_locked("cancelled"),
            "items": copy.deepcopy(self._items),
        }

    def _persist_locked(self) -> None:
        if self._job_path is None:
            return
        write_json_file_atomic(self._job_path, self._job_payload_locked())

    def _eta_locked(self) -> tuple[float | None, str]:
        completed = [
            item
            for item in self._items
            if item["status"] == "completed"
            and item.get("audio_duration_sec")
            and item.get("processing_time_sec")
        ]
        remaining = [item for item in self._items if item["status"] not in TERMINAL_STATUSES]
        if not remaining:
            return 0, ""
        if not completed:
            return None, "Оценка появится после обработки первых файлов."

        total_audio = sum(float(item["audio_duration_sec"]) for item in completed)
        total_processing = sum(float(item["processing_time_sec"]) for item in completed)
        remaining_durations = [item.get("audio_duration_sec") for item in remaining]
        if total_audio <= 0 or total_processing <= 0 or any(duration is None for duration in remaining_durations):
            return None, "Оценка появится после анализа файлов."

        average_speed = total_audio / total_processing
        eta = sum(float(duration) for duration in remaining_durations) / average_speed
        return round(eta, 1), ""

    def _elapsed_seconds_locked(self) -> float:
        if not self._started_at:
            return 0
        start = datetime.fromisoformat(self._started_at)
        end = datetime.fromisoformat(self._finished_at) if self._finished_at else datetime.now().astimezone()
        return round(max(0.0, (end - start).total_seconds()), 1)

    def _prepare_source(self, item: dict, item_snapshot: dict) -> Path:
        if item_snapshot.get("source_type") != "url":
            return Path(item_snapshot["source_path"])

        operations = item_snapshot.get("operations") or self._default_operations(item_snapshot.get("media_kind", "url"))
        needs_video = bool(operations.get("extract_frames"))
        if needs_video:
            downloaded_path = item_snapshot.get("downloaded_video_path") or item_snapshot.get("downloaded_media_path")
        else:
            downloaded_path = item_snapshot.get("downloaded_audio_path")
        if downloaded_path and Path(downloaded_path).exists():
            return Path(downloaded_path)
        downloader = self.video_downloader if needs_video else self.downloader
        if downloader is None:
            raise RuntimeError("Сервис скачивания URL не настроен.")

        with self._lock:
            item["status"] = "downloading"
            self._persist_locked()
        metadata = downloader(item_snapshot["source_url"])
        source_path = Path(metadata["source_path"])
        if not source_path.exists():
            raise RuntimeError("Скачанный аудиофайл не найден.")

        with self._lock:
            media_kind = "url" if needs_video else self._media_kind_for(source_path)
            item.update(
                {
                    "source_path": str(source_path),
                    "downloaded_audio_path": str(source_path),
                    "downloaded_media_path": metadata.get("downloaded_media_path") or str(source_path),
                    "downloaded_video_path": metadata.get("downloaded_video_path") if needs_video else item.get("downloaded_video_path"),
                    "source_title": metadata.get("source_title"),
                    "source_platform": metadata.get("source_platform") or "unknown",
                    "source_filename": metadata.get("source_title") or item["source_filename"],
                    "media_kind": media_kind,
                    "audio_duration_sec": self._rounded(metadata.get("audio_duration_sec")),
                    "status": "downloaded",
                }
            )
            self._persist_locked()
        return source_path

    def _ensure_inactive_locked(self, message: str) -> None:
        if self._is_running_locked():
            raise RuntimeError(message)

    def _is_running_locked(self) -> bool:
        return self._worker is not None and self._worker.is_alive()

    def _count_locked(self, status: str) -> int:
        return sum(1 for item in self._items if item["status"] == status)

    def _count_failed_locked(self) -> int:
        return sum(1 for item in self._items if item["status"] in {"error", "failed"})

    @staticmethod
    def _rounded(value: float | None) -> float | None:
        return round(value, 3) if value is not None else None

    @staticmethod
    def _now() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
