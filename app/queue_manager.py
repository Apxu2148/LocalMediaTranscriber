import copy
import inspect
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit, urlunsplit

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
STAGE_LABEL_KEYS = {
    "idle": "queueStageIdle",
    "adding_file": "queueStageAddingFile",
    "adding_url": "queueStageAddingUrl",
    "waiting_download": "queueStageWaitingDownload",
    "preparing_source": "queueStagePreparingSource",
    "downloading_media": "queueStageDownloadingMedia",
    "downloading_video": "queueStageDownloadingVideo",
    "cancelling_download": "queueStageCancellingDownload",
    "download_cancelled": "queueStageDownloadCancelled",
    "download_failed": "queueStageDownloadFailed",
    "transcribing_audio": "queueStageTranscribingAudio",
    "extracting_frames": "queueStageExtractingFrames",
    "cancelling_transcription": "queueStageCancellingTranscription",
    "cancelling": "queueStageCancelling",
    "completed": "queueStageCompleted",
    "failed": "queueStageFailed",
    "cancelled": "queueStageCancelled",
    "ocr_pending_future": "queueStageOcrFuture",
    "cv_pending_future": "queueStageCvFuture",
    "media_index_pending_future": "queueStageMediaIndexFuture",
}


@dataclass(frozen=True)
class QueueFile:
    source_path: Path
    source_filename: str
    source_type: str = "local_file"
    operations: dict | None = None
    frame_extraction: dict | None = None
    processing_plan: dict | None = None


@dataclass(frozen=True)
class QueueUrl:
    source_url: str
    processing_plan: dict | None = None


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
        retention_cleaner: Callable[[dict], dict] | None = None,
        estimate_processor: Callable[[dict], dict] | None = None,
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
        self.retention_cleaner = retention_cleaner
        self.estimate_processor = estimate_processor
        self._processor_accepts_cancel_event = self._callable_accepts_cancel_event(processor)

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
        self._estimating_indices: set[int] = set()
        self._progress_persisted_at: dict[int, float] = {}

    @staticmethod
    def _callable_accepts_cancel_event(callback: Callable) -> bool:
        try:
            signature = inspect.signature(callback)
        except (TypeError, ValueError):
            return False
        parameters = list(signature.parameters.values())
        if any(parameter.kind == inspect.Parameter.VAR_POSITIONAL for parameter in parameters):
            return True
        positional = [
            parameter
            for parameter in parameters
            if parameter.kind in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
        ]
        return len(positional) >= 4 or "cancel_event" in signature.parameters

    def _process_transcription(self, item: dict, model: str, device_preference: str, cancel_event: threading.Event) -> dict:
        if self._processor_accepts_cancel_event:
            return self.processor(item, model, device_preference, cancel_event)
        return self.processor(item, model, device_preference)

    @staticmethod
    def _process_download(
        downloader: Callable,
        source_url: str,
        cancel_event: threading.Event,
        progress_callback: Callable[[dict], None],
    ) -> dict:
        try:
            signature = inspect.signature(downloader)
        except (TypeError, ValueError):
            return downloader(source_url, cancel_event, progress_callback)
        parameters = signature.parameters
        if "cancel_event" in parameters or "progress_callback" in parameters:
            kwargs = {}
            if "cancel_event" in parameters:
                kwargs["cancel_event"] = cancel_event
            if "progress_callback" in parameters:
                kwargs["progress_callback"] = progress_callback
            return downloader(source_url, **kwargs)
        positional = [
            parameter
            for parameter in parameters.values()
            if parameter.kind in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
        ]
        if any(parameter.kind == inspect.Parameter.VAR_POSITIONAL for parameter in parameters.values()) or len(positional) >= 3:
            return downloader(source_url, cancel_event, progress_callback)
        if len(positional) >= 2:
            return downloader(source_url, cancel_event)
        return downloader(source_url)

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._is_running_locked()

    @property
    def is_estimating(self) -> bool:
        with self._lock:
            return bool(self._estimating_indices)

    def add_files(self, files: list[QueueFile]) -> dict:
        if not files:
            raise RuntimeError("Выберите хотя бы один файл для очереди.")

        with self._lock:
            self._ensure_inactive_locked("Нельзя добавлять файлы во время обработки очереди.")
            if self._job_id is None:
                self._create_job_locked()

            start_index = len(self._items) + 1
            active_keys = self._active_file_duplicate_keys_locked()
            seen_keys: set[str] = set()
            files_to_add: list[QueueFile] = []
            for queue_file in files:
                duplicate_key = self._file_duplicate_key(queue_file)
                if duplicate_key in active_keys or duplicate_key in seen_keys:
                    logger.info("Queue duplicate file add ignored: source=%s", queue_file.source_path)
                    continue
                seen_keys.add(duplicate_key)
                files_to_add.append(queue_file)

            for offset, queue_file in enumerate(files_to_add):
                item = self._new_file_item_locked(start_index + offset, queue_file)
                self._items.append(item)

            self._status = "pending"
            self._finished_at = None
            self._persist_locked()
            logger.info(
                "Queue files added: job_id=%s added=%s total=%s job_json=%s",
                self._job_id,
                len(files_to_add),
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
            active_keys = self._active_url_duplicate_keys_locked()
            seen_keys: set[str] = set()
            urls_to_add: list[str] = []
            for queue_url in urls:
                source_url = queue_url.source_url.strip()
                if not source_url:
                    raise RuntimeError("Пустые ссылки нельзя добавить в очередь.")
                duplicate_key = self._url_duplicate_key(source_url)
                if duplicate_key in active_keys or duplicate_key in seen_keys:
                    logger.info("Queue duplicate URL add ignored: source=%s", source_url)
                    continue
                seen_keys.add(duplicate_key)
                urls_to_add.append(source_url)

            for offset, source_url in enumerate(urls_to_add):
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
                    "stage": "waiting_download",
                    "stage_label_key": STAGE_LABEL_KEYS["waiting_download"],
                    "stage_detail": f"url_{index:03d}",
                    "stage_progress": {"mode": "none"},
                    "operations": self._default_operations("url"),
                    "frame_extraction": None,
                    "processing_plan": self._normalize_processing_plan(queue_url.processing_plan, "url"),
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
                    "partial_transcript": False,
                    "outputs": {},
                    "estimate": None,
                }
                self._sync_legacy_fields_from_processing_plan(item)
                self._refresh_frame_estimate_locked(item)
                self._items.append(item)

            self._status = "pending"
            self._finished_at = None
            self._persist_locked()
            logger.info("Queue URLs added: job_id=%s added=%s total=%s", self._job_id, len(urls_to_add), len(self._items))
            return self._status_snapshot_locked()

    def start(self, model: str, device_preference: str = "auto") -> dict:
        with self._lock:
            self._ensure_inactive_locked("Очередь уже выполняется.")
            self._ensure_no_estimate_locked()
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
            self._ensure_no_estimate_locked()
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
            self._ensure_no_estimate_locked()
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
                        "partial_transcript": False,
                        "outputs": {},
                    }
                )
                retry_stage = "waiting_download" if item.get("source_type") == "url" and not item.get("source_path") else "idle"
                self._set_item_stage_locked(item, retry_stage, status="pending")
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
        processing_plan: dict | None = None,
    ) -> dict:
        with self._lock:
            self._ensure_inactive_locked("Нельзя менять параметры задач во время обработки очереди.")
            self._ensure_no_estimate_locked()
            item = self._find_item_locked(index)
            if item["status"] != "pending":
                raise RuntimeError("Можно менять только ожидающие задачи очереди.")

            media_kind = item.get("media_kind") or self._media_kind_for(item.get("source_path") or item["source_filename"])
            legacy_operations = operations if operations is not None else (item.get("operations") if item.get("processing_plan") is None else None)
            legacy_frame_extraction = (
                frame_extraction
                if frame_extraction is not None
                else (item.get("frame_extraction") if processing_plan is None else None)
            )
            item["processing_plan"] = self._normalize_processing_plan(
                processing_plan if processing_plan is not None else item.get("processing_plan"),
                media_kind,
                operations=legacy_operations,
                frame_extraction=legacy_frame_extraction,
            )
            self._sync_legacy_fields_from_processing_plan(item)
            self._refresh_frame_estimate_locked(item)
            item["estimate"] = None
            self._persist_locked()
            logger.info("Queue item updated: job_id=%s index=%s", self._job_id, index)
            return self._status_snapshot_locked()

    def remove_item(self, index: int) -> dict:
        with self._lock:
            self._ensure_no_estimate_locked()
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

    def estimate_item(self, index: int) -> dict:
        with self._lock:
            self._ensure_inactive_locked("Нельзя запускать оценку во время обработки очереди.")
            self._ensure_no_estimate_locked()
            if self.estimate_processor is None:
                raise RuntimeError("Оценка времени не настроена.")
            item = self._find_item_locked(index)
            if item["status"] != "pending":
                raise RuntimeError("Оценка доступна только для ожидающих задач очереди.")
            self._sync_legacy_fields_from_processing_plan(item)
            item["estimate"] = {
                "status": "estimating",
                "created_at": self._now(),
            }
            self._estimating_indices.add(index)
            item_snapshot = copy.deepcopy(item)
            self._persist_locked()

        try:
            estimate = self.estimate_processor(item_snapshot)
        except Exception as exc:
            error_code = getattr(exc, "code", None) or "estimate_failed"
            estimate = {
                "status": "failed",
                "created_at": self._now(),
                "error_code": error_code,
                "error_message": str(exc),
            }
            logger.warning(
                "Queue runtime estimate failed: job_id=%s index=%s code=%s error=%s",
                self._job_id,
                index,
                error_code,
                exc,
            )
        with self._lock:
            item = self._find_item_locked(index)
            item["estimate"] = copy.deepcopy(estimate)
            self._estimating_indices.discard(index)
            self._persist_locked()
            logger.info(
                "Queue runtime estimate finished: job_id=%s index=%s status=%s",
                self._job_id,
                index,
                estimate.get("status"),
            )
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

            if item.get("cancel_requested"):
                return self._status_snapshot_locked()
            if item["status"] not in {"downloading", "extracting_audio", "transcribing", "extracting_frames"}:
                raise RuntimeError("Эту задачу нельзя отменить на текущем этапе.")

            cancel_event = self._cancel_events.get(index)
            if cancel_event is not None:
                cancel_event.set()
            item["cancel_requested"] = True
            if item["status"] == "downloading":
                self._set_item_stage_locked(item, "cancelling_download", status="downloading")
            elif item["status"] == "extracting_frames":
                self._set_item_stage_locked(item, "cancelling", status="extracting_frames")
            else:
                self._set_item_stage_locked(item, "cancelling_transcription", status="transcribing")
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
        item = {
            "index": index,
            "source_type": queue_file.source_type,
            "media_kind": media_kind,
            "source_path": str(queue_file.source_path),
            "source_filename": queue_file.source_filename,
            "status": "pending",
            "stage": "idle",
            "stage_label_key": STAGE_LABEL_KEYS["idle"],
            "stage_detail": queue_file.source_filename,
            "stage_progress": {"mode": "none"},
            "operations": self._normalize_operations(queue_file.operations, media_kind),
            "frame_extraction": None,
            "processing_plan": self._normalize_processing_plan(
                queue_file.processing_plan,
                media_kind,
                operations=queue_file.operations,
                frame_extraction=queue_file.frame_extraction,
            ),
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
            "partial_transcript": False,
            "outputs": {},
            "estimate": None,
        }
        self._sync_legacy_fields_from_processing_plan(item)
        if media_kind == "video":
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
        normalized["ocr"] = False
        normalized["cv"] = False
        if media_kind not in {"video", "url"}:
            normalized["extract_frames"] = False
            normalized["ocr"] = False
            normalized["cv"] = False
        return normalized

    def _normalize_processing_plan(
        self,
        processing_plan: dict | None,
        media_kind: str,
        *,
        operations: dict | None = None,
        frame_extraction: dict | None = None,
    ) -> dict:
        plan = copy.deepcopy(processing_plan) if isinstance(processing_plan, dict) else {}
        operation_defaults = self._normalize_operations(operations, media_kind)
        audio_plan = plan.get("audio") if isinstance(plan.get("audio"), dict) else {}
        frames_plan = plan.get("frames") if isinstance(plan.get("frames"), dict) else {}
        ocr_plan = plan.get("ocr") if isinstance(plan.get("ocr"), dict) else {}
        cv_plan = plan.get("cv") if isinstance(plan.get("cv"), dict) else {}
        supports_frames = media_kind in {"video", "url"}

        model = str(audio_plan.get("model") or config.WHISPER_MODEL or "small").strip()
        if model not in config.SUPPORTED_WHISPER_MODELS:
            model = config.WHISPER_MODEL if config.WHISPER_MODEL in config.SUPPORTED_WHISPER_MODELS else "small"

        device = str(audio_plan.get("device") or config.WHISPER_DEVICE or "auto").strip().lower()
        if device not in {"auto", "cpu", "cuda"}:
            device = "auto"

        frame_source = frame_extraction if frame_extraction is not None else frames_plan
        frame_settings = normalize_frame_extraction_settings(frame_source)
        rate = normalize_frame_rate(frame_settings.get("rate"))
        interval_sec = rate.get("seconds") if rate.get("mode") == "interval" else None

        audio_enabled = (
            operation_defaults.get("transcribe_audio", True)
            if operations is not None
            else audio_plan.get("enabled", operation_defaults.get("transcribe_audio", True))
        )
        frames_enabled = (
            operation_defaults.get("extract_frames", False)
            if operations is not None
            else frames_plan.get("enabled", operation_defaults.get("extract_frames", False))
        )
        ocr_backend = str(ocr_plan.get("backend") or ocr_plan.get("engine") or "tesseract")
        if ocr_backend not in {"tesseract", "easyocr", "paddleocr", "windows_ocr"}:
            ocr_backend = "tesseract"
        default_ocr_languages = ["rus", "eng"] if ocr_backend == "tesseract" else ["ru", "en"]

        return {
            "audio": {
                "enabled": bool(audio_enabled),
                "model": model,
                "device": device,
            },
            "frames": {
                "enabled": bool(frames_enabled) and supports_frames,
                "rate": rate,
                "interval_sec": interval_sec,
                "jpeg_quality": normalize_jpeg_quality(frame_settings.get("jpeg_quality")),
            },
            "ocr": {
                "enabled": False,
                "backend": ocr_backend,
                "engine": ocr_backend,
                "languages": list(ocr_plan.get("languages") or default_ocr_languages),
                "status": "coming_soon",
                "engine_available": bool(ocr_plan.get("engine_available", False)),
            },
            "cv": {
                "enabled": False,
                "engine": str(cv_plan.get("engine") or "basic_opencv"),
                "status": "coming_soon",
            },
        }

    def _sync_legacy_fields_from_processing_plan(self, item: dict) -> None:
        media_kind = item.get("media_kind") or self._media_kind_for(item.get("source_path") or item["source_filename"])
        existing_plan = item.get("processing_plan")
        plan = self._normalize_processing_plan(
            existing_plan,
            media_kind,
            operations=None if existing_plan is not None else item.get("operations"),
            frame_extraction=None if existing_plan is not None else item.get("frame_extraction"),
        )
        item["processing_plan"] = plan
        item["operations"] = self._normalize_operations(
            {
                "transcribe_audio": plan["audio"]["enabled"],
                "extract_frames": plan["frames"]["enabled"],
                "ocr": False,
                "cv": False,
            },
            media_kind,
        )
        if self._item_supports_frame_extraction(item):
            item["frame_extraction"] = self._frame_extraction_payload(
                item,
                {"rate": plan["frames"]["rate"], "jpeg_quality": plan["frames"]["jpeg_quality"]},
            )
        else:
            item["frame_extraction"] = None

    @staticmethod
    def _audio_plan_for(item: dict, fallback_model: str, fallback_device: str) -> tuple[str, str]:
        audio_plan = (item.get("processing_plan") or {}).get("audio") or {}
        return (
            str(audio_plan.get("model") or fallback_model or config.WHISPER_MODEL),
            str(audio_plan.get("device") or fallback_device or "auto"),
        )

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
            if item.get("source_type") == "url" and not (operations.get("transcribe_audio") or operations.get("extract_frames")):
                raise RuntimeError("Выберите хотя бы одну операцию для этой ссылки.")
            if media_kind == "video" and not (operations.get("transcribe_audio") or operations.get("extract_frames")):
                raise RuntimeError("Выберите хотя бы одну операцию для этого видео.")

    @staticmethod
    def _item_supports_frame_extraction(item: dict) -> bool:
        return item.get("media_kind") == "video" or item.get("source_type") == "url"

    @staticmethod
    def _file_duplicate_key(queue_file: QueueFile) -> str:
        return str(queue_file.source_path.resolve()).casefold()

    @staticmethod
    def _url_duplicate_key(source_url: str) -> str:
        value = source_url.strip()
        parsed = urlsplit(value)
        if not parsed.scheme or not parsed.netloc:
            return value.casefold()
        return urlunsplit(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path or "",
                parsed.query,
                "",
            )
        ).casefold()

    def _active_file_duplicate_keys_locked(self) -> set[str]:
        return {
            str(Path(item["source_path"]).resolve()).casefold()
            for item in self._items
            if item.get("source_path") and item.get("source_type") != "url" and item["status"] not in TERMINAL_STATUSES
        }

    def _active_url_duplicate_keys_locked(self) -> set[str]:
        return {
            self._url_duplicate_key(item["source_url"])
            for item in self._items
            if item.get("source_type") == "url" and item.get("source_url") and item["status"] not in TERMINAL_STATUSES
        }

    @staticmethod
    def _stage_detail_for(item: dict) -> str | None:
        return item.get("source_title") or item.get("source_filename") or item.get("source_url") or item.get("source_path")

    def _set_item_stage_locked(self, item: dict, stage: str, *, status: str | None = None, detail: str | None = None) -> None:
        previous_stage = item.get("stage")
        if status is not None:
            item["status"] = status
        item["stage"] = stage
        item["stage_label_key"] = STAGE_LABEL_KEYS.get(stage, STAGE_LABEL_KEYS["idle"])
        item["stage_detail"] = detail if detail is not None else self._stage_detail_for(item)
        if stage in {"downloading_media", "downloading_video"} and previous_stage != stage:
            item["stage_progress"] = {"mode": "indeterminate"}
        elif stage in {"preparing_source", "transcribing_audio", "cancelling_transcription", "cancelling"}:
            item["stage_progress"] = {"mode": "indeterminate"}
        elif stage == "extracting_frames" and previous_stage != stage:
            estimated = (item.get("frame_extraction") or {}).get("estimated_frame_count")
            item["stage_progress"] = {
                "mode": "determinate" if estimated else "indeterminate",
                "percent": 0.0 if estimated else None,
                "completed_units": 0,
                "total_units": estimated,
            }
        elif stage == "cancelling_download":
            item.setdefault("stage_progress", {"mode": "indeterminate"})
        elif stage in {
            "idle",
            "waiting_download",
            "completed",
            "failed",
            "cancelled",
            "download_cancelled",
            "download_failed",
        }:
            item["stage_progress"] = {"mode": "none"}

    @staticmethod
    def _path_exists(path_value: str | None) -> bool:
        if not path_value:
            return False
        try:
            return Path(path_value).exists()
        except OSError:
            return False

    @staticmethod
    def _absolute_artifact_path(path_value: str | None, *, base_dir: Path | None = None) -> str | None:
        if not path_value:
            return None
        path = Path(path_value)
        if path.is_absolute():
            return str(path)
        normalized = str(path_value).replace("\\", "/")
        if normalized.startswith("data/"):
            return str((config.BASE_DIR / path).resolve())
        if base_dir is not None:
            return str((base_dir / path).resolve())
        return str(path)

    def _output_artifacts_locked(self, item: dict, cleanup_result: dict | None = None) -> dict:
        cleanup = cleanup_result or {}
        frame_result = item.get("frame_extraction_result") or (item.get("frame_extraction") or {}).get("result") or {}
        frames_dir = self._absolute_artifact_path(
            frame_result.get("frames_path") or item.get("frames_path") or frame_result.get("frames_dir") or item.get("frames_dir"),
            base_dir=config.RECORDINGS_DIR,
        )
        frames_index_path = self._absolute_artifact_path(
            frame_result.get("frames_index_path") or item.get("frames_index_path"),
            base_dir=config.RECORDINGS_DIR,
        )
        downloaded_media_path = self._absolute_artifact_path(
            item.get("downloaded_video_path") or item.get("downloaded_media_path") or item.get("downloaded_audio_path")
        )
        uploaded_temp_path = None
        if item.get("source_type") == "local_file" and item.get("source_path"):
            source_path = Path(item["source_path"])
            try:
                resolved_source_path = source_path.resolve()
                if resolved_source_path.is_relative_to(config.UPLOADS_DIR.resolve()):
                    uploaded_temp_path = str(resolved_source_path)
            except OSError:
                uploaded_temp_path = None

        outputs = {
            "transcript_path": self._absolute_artifact_path(item.get("transcript_path")),
            "transcript_exists": self._path_exists(item.get("transcript_path")),
            "transcript_partial": bool(item.get("partial_transcript")),
            "json_path": self._absolute_artifact_path(item.get("json_path")),
            "json_exists": self._path_exists(item.get("json_path")),
            "frames_dir": frames_dir,
            "frames_dir_exists": self._path_exists(frames_dir),
            "frames_index_path": frames_index_path,
            "frames_index_exists": self._path_exists(frames_index_path),
            "downloaded_media_path": downloaded_media_path,
            "downloaded_media_exists": self._path_exists(downloaded_media_path),
            "downloaded_media_deleted": bool(cleanup.get("downloaded_media_deleted")),
            "downloaded_media_delete_error": cleanup.get("downloaded_media_delete_error"),
            "uploaded_temp_path": uploaded_temp_path,
            "uploaded_temp_exists": self._path_exists(uploaded_temp_path),
            "uploaded_temp_deleted": bool(cleanup.get("uploaded_temp_deleted")),
            "uploaded_temp_delete_error": cleanup.get("uploaded_temp_delete_error"),
            "retention_cleanup_error": cleanup.get("retention_cleanup_error"),
        }
        return outputs

    def _refresh_outputs_locked(self, item: dict, cleanup_result: dict | None = None) -> None:
        item["outputs"] = self._output_artifacts_locked(item, cleanup_result)

    def _apply_success_retention_locked(self, item: dict) -> dict:
        if self.retention_cleaner is None:
            return {}
        try:
            return self.retention_cleaner(copy.deepcopy(item))
        except Exception as exc:
            logger.exception("Queue retention cleanup failed: job_id=%s index=%s", self._job_id, item.get("index"))
            return {"retention_cleanup_error": str(exc)}

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
                estimated = progress.get("estimated_frame_count") or (frame_settings or {}).get("estimated_frame_count")
                completed = int(progress.get("extracted_frame_count") or 0)
                percent = min(100.0, completed * 100.0 / estimated) if estimated else None
                item["stage_progress"] = {
                    "mode": "determinate" if estimated else "indeterminate",
                    "percent": round(percent, 1) if percent is not None else None,
                    "completed_units": completed,
                    "total_units": estimated,
                }
                self._persist_locked()

        return update

    def _download_progress_callback(self, index: int) -> Callable[[dict], None]:
        def update(progress: dict) -> None:
            with self._lock:
                item = next((entry for entry in self._items if entry["index"] == index), None)
                if item is None or item["status"] != "downloading":
                    return
                item["stage_progress"] = self._normalize_stage_progress(progress)
                now = time.monotonic()
                last_persisted = self._progress_persisted_at.get(index, 0.0)
                if now - last_persisted >= 0.25 or item["stage_progress"].get("percent") == 100.0:
                    self._progress_persisted_at[index] = now
                    self._persist_locked()

        return update

    @staticmethod
    def _normalize_stage_progress(progress: dict | None) -> dict:
        value = progress or {}
        mode = value.get("mode") if value.get("mode") in {"determinate", "indeterminate"} else "indeterminate"

        def optional_number(key: str) -> float | int | None:
            raw = value.get(key)
            try:
                number = float(raw) if raw is not None else None
            except (TypeError, ValueError):
                return None
            if number is None or number < 0:
                return None
            return int(number) if key in {"downloaded_bytes", "total_bytes"} else round(number, 1)

        percent = optional_number("percent")
        return {
            "mode": mode,
            "percent": min(100.0, float(percent)) if percent is not None and mode == "determinate" else None,
            "downloaded_bytes": optional_number("downloaded_bytes"),
            "total_bytes": optional_number("total_bytes"),
            "speed_bytes_per_sec": optional_number("speed_bytes_per_sec"),
            "eta_sec": optional_number("eta_sec"),
            "source": str(value.get("source") or "unknown"),
        }

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
            download_cancel_event: threading.Event | None = None
            with self._lock:
                item = next((entry for entry in self._items if entry["status"] == "pending"), None)
                if item is None:
                    self._finish_locked("completed")
                    return

                self._current_index = item["index"]
                if item.get("source_type") == "url":
                    download_cancel_event = threading.Event()
                    self._cancel_events[item["index"]] = download_cancel_event
                    item["cancel_requested"] = False
                    operations = item.get("operations") or self._default_operations(item.get("media_kind", "url"))
                    self._set_item_stage_locked(
                        item,
                        "downloading_video" if operations.get("extract_frames") else "downloading_media",
                        status="downloading",
                    )
                else:
                    self._set_item_stage_locked(item, "preparing_source", status="analyzing")
                self._persist_locked()
                item_snapshot = copy.deepcopy(item)
                fallback_model = self._model or config.WHISPER_MODEL
                fallback_device = self._device_preference or "auto"
                model, device_preference = self._audio_plan_for(item_snapshot, fallback_model, fallback_device)
                logger.info(
                    "Queue task started: job_id=%s index=%s source=%s model=%s device=%s",
                    self._job_id,
                    item["index"],
                    item.get("source_path") or item.get("source_url"),
                    model,
                    device_preference,
                )

            try:
                try:
                    source_path = self._prepare_source(item, item_snapshot, download_cancel_event)
                finally:
                    if download_cancel_event is not None:
                        with self._lock:
                            self._cancel_events.pop(item["index"], None)
                            self._progress_persisted_at.pop(item["index"], None)
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
                    self._set_item_stage_locked(item, "preparing_source", status="analyzing")
                    self._persist_locked()
                    item_snapshot = copy.deepcopy(item)
                duration = self.duration_reader(source_path)
                with self._lock:
                    item["audio_duration_sec"] = self._rounded(duration) or item.get("audio_duration_sec")
                    self._persist_locked()

                operations = item_snapshot.get("operations") or self._default_operations(item_snapshot.get("media_kind", "audio"))
                model, device_preference = self._audio_plan_for(
                    item_snapshot,
                    self._model or config.WHISPER_MODEL,
                    self._device_preference or "auto",
                )
                transcript_result: dict = {}
                transcript_error: Exception | None = None
                if operations.get("transcribe_audio"):
                    cancel_event = threading.Event()
                    with self._lock:
                        item["cancel_requested"] = False
                        self._cancel_events[item["index"]] = cancel_event
                    try:
                        self.media_validator(source_path)
                        if source_path.suffix.lower() in config.SUPPORTED_VIDEO_EXTENSIONS:
                            with self._lock:
                                self._set_item_stage_locked(item, "transcribing_audio", status="extracting_audio")
                                self._persist_locked()

                        with self._lock:
                            next_stage = "cancelling_transcription" if item.get("cancel_requested") else "transcribing_audio"
                            self._set_item_stage_locked(item, next_stage, status="transcribing")
                            self._persist_locked()
                            item_snapshot = copy.deepcopy(item)

                        transcript_result = self._process_transcription(item_snapshot, model, device_preference, cancel_event)
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
                                    "partial_transcript": bool(transcript_result.get("partial")),
                                }
                            )
                            self._persist_locked()
                        if transcript_result.get("status") == "cancelled":
                            with self._lock:
                                item.update(
                                    {
                                        "status": "cancelled",
                                        "error_message": transcript_result.get("cancellation_reason"),
                                        "technical_details": transcript_result.get("cancellation_reason"),
                                        "partial_transcript": bool(transcript_result.get("partial")),
                                    }
                                )
                                self._set_item_stage_locked(item, "cancelled", status="cancelled")
                                self._refresh_outputs_locked(item)
                                self._persist_locked()
                                logger.info(
                                    "Queue transcription cancelled: job_id=%s index=%s transcript=%s",
                                    self._job_id,
                                    item["index"],
                                    item.get("transcript_path"),
                                )
                            task_cancelled = True
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
                    finally:
                        with self._lock:
                            self._cancel_events.pop(item["index"], None)

                frame_result: dict = {}
                if operations.get("extract_frames") and not task_cancelled:
                    if self.frame_processor is None:
                        raise RuntimeError("Frame extraction service is not configured.")
                    with self._lock:
                        self._set_item_stage_locked(item, "extracting_frames", status="extracting_frames")
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
                            self._set_item_stage_locked(item, "cancelled", status="cancelled")
                            self._refresh_outputs_locked(item)
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
                                self._set_item_stage_locked(item, "failed", status="error")
                                self._refresh_outputs_locked(item)
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
                            self._set_item_stage_locked(item, "failed", status="error")
                            self._refresh_outputs_locked(item)
                        else:
                            item.update(
                                {
                                    "status": "completed",
                                    "error_message": None,
                                    "technical_details": None,
                                    "processing_time_sec": combined_processing,
                                }
                            )
                            self._set_item_stage_locked(item, "completed", status="completed")
                            cleanup_result = self._apply_success_retention_locked(item)
                            self._refresh_outputs_locked(item, cleanup_result)
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
                if getattr(exc, "cancelled", False):
                    with self._lock:
                        item.update(
                            {
                                "status": "cancelled",
                                "error_message": None,
                                "technical_details": None,
                            }
                        )
                        self._set_item_stage_locked(item, "download_cancelled", status="cancelled")
                        self._refresh_outputs_locked(item)
                        self._persist_locked()
                        logger.info(
                            "Queue URL download cancelled: job_id=%s index=%s url=%s",
                            self._job_id,
                            item["index"],
                            item.get("source_url"),
                        )
                else:
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
                        download_failed = item.get("source_type") == "url" and (
                            getattr(exc, "download_error", False)
                            or item.get("stage") in {"downloading_media", "downloading_video", "cancelling_download"}
                        )
                        self._set_item_stage_locked(item, "download_failed" if download_failed else "failed", status="error")
                        self._refresh_outputs_locked(item)
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
                            self._set_item_stage_locked(pending_item, "cancelled", status="cancelled")
                            self._refresh_outputs_locked(pending_item)
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
        current_stage = current_item.get("stage") if current_item else "idle"
        return {
            **payload,
            "job_path": str(self._job_path) if self._job_path else None,
            "pending_items": self._count_locked("pending"),
            "running_items": sum(1 for item in self._items if item["status"] in ACTIVE_STATUSES),
            "current_file": current_item["source_filename"] if current_item else None,
            "current_item": copy.deepcopy(current_item),
            "current_stage": current_stage,
            "current_stage_label_key": current_item.get("stage_label_key") if current_item else STAGE_LABEL_KEYS["idle"],
            "current_stage_detail": current_item.get("stage_detail") if current_item else None,
            "elapsed_sec": elapsed_sec,
            "eta_sec": eta_sec,
            "eta_message": eta_message,
            "progress_percent": round((finished_items / total_items) * 100, 1) if total_items else 0,
            "stop_after_current": self._stop_after_current,
            "estimating_items": len(self._estimating_indices),
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

    def _prepare_source(
        self,
        item: dict,
        item_snapshot: dict,
        cancel_event: threading.Event | None = None,
    ) -> Path:
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
            self._set_item_stage_locked(
                item,
                "downloading_video" if needs_video else "downloading_media",
                status="downloading",
            )
            self._persist_locked()
        active_cancel_event = cancel_event or threading.Event()
        metadata = self._process_download(
            downloader,
            item_snapshot["source_url"],
            active_cancel_event,
            self._download_progress_callback(item["index"]),
        )
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
                }
            )
            self._set_item_stage_locked(item, "preparing_source", status="downloaded")
            self._persist_locked()
        return source_path

    def _ensure_inactive_locked(self, message: str) -> None:
        if self._is_running_locked():
            raise RuntimeError(message)

    def _ensure_no_estimate_locked(self) -> None:
        if self._estimating_indices:
            raise RuntimeError("Дождитесь завершения текущей оценки времени.")

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
