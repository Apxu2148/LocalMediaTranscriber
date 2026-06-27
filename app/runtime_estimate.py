import hashlib
import json
import math
import random
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from . import config
from .frame_extractor import (
    estimate_frame_count,
    extraction_step_seconds,
    normalize_frame_rate,
    normalize_jpeg_quality,
    normalize_max_frame_size,
)
from .utils import audio_duration_seconds


DEFAULT_SAMPLE_DURATION_SEC = 60.0


class RuntimeEstimateError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def source_has_audio_stream(source_path: Path) -> bool | None:
    try:
        import av

        with av.open(str(source_path)) as container:
            return any(stream.type == "audio" for stream in container.streams)
    except Exception:
        return None


def looks_like_no_audio_sample_error(message: str | None) -> bool:
    normalized = (message or "").casefold()
    return any(
        marker in normalized
        for marker in (
            "does not contain any stream",
            "matches no streams",
            "no audio stream",
            "audio stream was found",
        )
    )


def prepare_audio_sample(
    source_path: Path,
    sample_duration_sec: float,
    source_duration_sec: float,
    workspace: Path,
) -> Path:
    if source_duration_sec <= sample_duration_sec + 1e-6:
        return source_path

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeEstimateError("ffmpeg_unavailable", "ffmpeg is required to prepare an estimate sample.")

    sample_path = workspace / "audio_sample.wav"
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source_path),
        "-t",
        f"{sample_duration_sec:.3f}",
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(sample_path),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeEstimateError("sample_preparation_failed", "Timed out while preparing the estimate sample.") from exc
    if completed.returncode != 0 or not sample_path.is_file():
        details = (completed.stderr or completed.stdout or "ffmpeg failed").strip()
        raise RuntimeEstimateError("sample_preparation_failed", details)
    return sample_path


def sample_ocr_frame_indices(expected_frame_count: int, seed_value: str, max_samples: int = 3) -> list[int]:
    if expected_frame_count <= 0 or max_samples <= 0:
        return []
    if expected_frame_count <= max_samples:
        return list(range(expected_frame_count))

    digest = hashlib.sha256(seed_value.encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    samples: list[int] = []
    for bucket in range(max_samples):
        start = math.floor(bucket * expected_frame_count / max_samples)
        end = math.floor((bucket + 1) * expected_frame_count / max_samples) - 1
        end = max(start, min(expected_frame_count - 1, end))
        samples.append(rng.randint(start, end))
    return sorted(set(samples))


class RuntimeEstimator:
    def __init__(
        self,
        *,
        audio_processor: Callable[[Path, str, str], dict],
        frame_processor: Callable[[Path, Path, float, dict, int, str], dict],
        ocr_processor: Callable[[list[Path], list[str]], dict] | None = None,
        ocr_frame_processor: Callable[[Path, Path, list[float], int, str], dict] | None = None,
        ocr_status_reader: Callable[[], dict] | None = None,
        duration_reader: Callable[[Path], float | None] = audio_duration_seconds,
        audio_stream_reader: Callable[[Path], bool | None] = source_has_audio_stream,
        sample_preparer: Callable[[Path, float, float, Path], Path] = prepare_audio_sample,
        temp_root: Path | None = None,
        sample_duration_sec: float = DEFAULT_SAMPLE_DURATION_SEC,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.audio_processor = audio_processor
        self.frame_processor = frame_processor
        self.ocr_processor = ocr_processor
        self.ocr_frame_processor = ocr_frame_processor
        self.ocr_status_reader = ocr_status_reader
        self.duration_reader = duration_reader
        self.audio_stream_reader = audio_stream_reader
        self.sample_preparer = sample_preparer
        self.temp_root = temp_root or config.TEMP_DIR
        self.sample_duration_sec = float(sample_duration_sec)
        self.clock = clock

    def estimate(self, item: dict) -> dict:
        plan = item.get("processing_plan") or {}
        audio_plan = plan.get("audio") or {}
        frames_plan = plan.get("frames") or {}
        ocr_plan = plan.get("ocr") or {}
        audio_enabled = bool(audio_plan.get("enabled"))
        frames_enabled = bool(frames_plan.get("enabled"))
        ocr_enabled = bool(ocr_plan.get("enabled"))
        created_at = datetime.now().astimezone().isoformat(timespec="seconds")

        if not audio_enabled and not frames_enabled and not ocr_enabled:
            return {
                "status": "complete",
                "created_at": created_at,
                "approximate": True,
                "no_enabled_operations": True,
                "audio": {"enabled": False},
                "frames": {"enabled": False},
                "ocr": {"enabled": False},
                "total_estimated_full_runtime_sec": None,
            }

        source_path = self._source_path(item)
        source_duration_sec = self._source_duration(item, source_path)
        if source_duration_sec is None or source_duration_sec <= 0:
            raise RuntimeEstimateError("duration_unavailable", "Could not determine source duration.")
        sample_duration_sec = min(self.sample_duration_sec, source_duration_sec)

        self.temp_root.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="runtime_estimate_", dir=self.temp_root) as temp_dir:
            workspace = Path(temp_dir)
            audio_result = {"enabled": False}
            frames_result = {"enabled": False}
            ocr_result = {"enabled": False}
            rate = normalize_frame_rate(frames_plan.get("rate"))
            jpeg_quality = normalize_jpeg_quality(frames_plan.get("jpeg_quality"))
            max_frame_size = normalize_max_frame_size(frames_plan.get("max_frame_size"))

            if audio_enabled:
                model = str(audio_plan.get("model") or config.WHISPER_MODEL)
                device = str(audio_plan.get("device") or config.WHISPER_DEVICE or "auto")
                has_audio = self.audio_stream_reader(source_path)
                if has_audio is False:
                    audio_result = self._audio_unavailable_result(model, device, "no_audio_stream")
                else:
                    try:
                        sample_path = self.sample_preparer(source_path, sample_duration_sec, source_duration_sec, workspace)
                    except RuntimeEstimateError as exc:
                        if exc.code == "sample_preparation_failed" and looks_like_no_audio_sample_error(str(exc)):
                            audio_result = self._audio_unavailable_result(model, device, "no_audio_stream")
                        else:
                            raise
                    else:
                        started = self.clock()
                        processor_result = self.audio_processor(sample_path, model, device) or {}
                        sample_runtime_sec = max(0.0, self.clock() - started)
                        audio_result = {
                            "enabled": True,
                            "status": "complete",
                            "model": model,
                            "device": device,
                            "effective_device": processor_result.get("device") or device,
                            "compute_type": processor_result.get("compute_type"),
                            "sample_runtime_sec": self._rounded(sample_runtime_sec),
                            "estimated_full_runtime_sec": self._rounded(
                                sample_runtime_sec * source_duration_sec / sample_duration_sec
                            ),
                            "speed_factor": self._rounded(
                                sample_duration_sec / sample_runtime_sec if sample_runtime_sec > 0 else None
                            ),
                            "included_in_total": True,
                        }

            if frames_enabled:
                frames_workspace = workspace / "frames"
                frames_workspace.mkdir(parents=True, exist_ok=True)
                started = self.clock()
                processor_result = self.frame_processor(
                    source_path,
                    frames_workspace,
                    sample_duration_sec,
                    rate,
                    jpeg_quality,
                    max_frame_size,
                ) or {}
                sample_runtime_sec = max(0.0, self.clock() - started)
                sample_frames = int(processor_result.get("sample_frames") or 0)
                estimated_total_frames = estimate_frame_count(source_duration_sec, rate) or 0
                estimated_runtime = (
                    sample_runtime_sec * estimated_total_frames / max(sample_frames, 1)
                )
                frames_result = {
                    "enabled": True,
                    "rate": rate,
                    "interval_sec": rate.get("seconds"),
                    "requested_fps": rate.get("fps"),
                    "jpeg_quality": jpeg_quality,
                    "max_frame_size": max_frame_size,
                    "sample_frames": sample_frames,
                    "estimated_total_frames": estimated_total_frames,
                    "sample_runtime_sec": self._rounded(sample_runtime_sec),
                    "estimated_full_runtime_sec": self._rounded(estimated_runtime),
                }

            if ocr_enabled:
                ocr_result = self._estimate_ocr(
                    item=item,
                    ocr_plan=ocr_plan,
                    source_path=source_path,
                    source_duration_sec=source_duration_sec,
                    rate=rate,
                    jpeg_quality=jpeg_quality,
                    max_frame_size=max_frame_size,
                    workspace=workspace,
                )

        included_runtimes = [
            float(result.get("estimated_full_runtime_sec") or 0)
            for result in (audio_result, frames_result, ocr_result)
            if result.get("enabled") and result.get("included_in_total", True)
        ]
        total_runtime = sum(included_runtimes) if included_runtimes else None
        total_excludes_audio = bool(audio_result.get("enabled")) and not bool(audio_result.get("included_in_total", True))
        total_excludes_ocr = bool(ocr_result.get("enabled")) and not bool(ocr_result.get("included_in_total"))
        return {
            "status": "complete",
            "created_at": created_at,
            "sample_duration_sec": self._rounded(sample_duration_sec),
            "source_duration_sec": self._rounded(source_duration_sec),
            "approximate": True,
            "audio": audio_result,
            "frames": frames_result,
            "ocr": ocr_result,
            "total_excludes_audio": total_excludes_audio,
            "total_excludes_ocr": total_excludes_ocr,
            "total_estimated_full_runtime_sec": self._rounded(total_runtime),
        }

    @staticmethod
    def _audio_unavailable_result(model: str, device: str, reason: str) -> dict:
        return {
            "enabled": True,
            "status": "unavailable",
            "reason": reason,
            "model": model,
            "device": device,
            "included_in_total": False,
            "estimated_full_runtime_sec": None,
        }

    def _estimate_ocr(
        self,
        *,
        item: dict,
        ocr_plan: dict,
        source_path: Path,
        source_duration_sec: float,
        rate: dict,
        jpeg_quality: int,
        max_frame_size: str,
        workspace: Path,
    ) -> dict:
        selected_backend = str(ocr_plan.get("backend") or ocr_plan.get("engine") or "").strip().lower()
        backend = selected_backend
        if backend == "auto":
            backend = str(ocr_plan.get("resolved_backend") or ocr_plan.get("engine") or "").strip().lower()
        languages = list(ocr_plan.get("languages") or ["ru", "en"])
        base = {
            "enabled": True,
            "backend": selected_backend or backend or "unknown",
            "resolved_backend": backend or "unknown",
            "engine": "EasyOCR" if backend == "easyocr" else backend or "unknown",
            "languages": languages,
            "included_in_total": False,
            "estimated_full_runtime_sec": None,
        }
        if backend != "easyocr":
            return {**base, "status": "unavailable", "reason": "ocr_backend_unsupported"}

        status = self._easyocr_status(ocr_plan)
        if not status.get("available"):
            return {
                **base,
                "status": "unavailable",
                "reason": "easyocr_unavailable",
                "engine_status": status.get("status"),
            }
        if self.ocr_processor is None or self.ocr_frame_processor is None:
            return {**base, "status": "unavailable", "reason": "ocr_estimator_unconfigured"}

        expected_total_frames = estimate_frame_count(source_duration_sec, rate) or 0
        if expected_total_frames <= 0:
            return {
                **base,
                "status": "complete",
                "expected_total_frames": 0,
                "sample_frames": 0,
                "sample_runtime_sec": 0.0,
                "average_sec_per_frame": None,
                "estimated_full_runtime_sec": 0.0,
                "included_in_total": True,
            }

        indices = sample_ocr_frame_indices(expected_total_frames, self._ocr_sample_seed(item, rate, jpeg_quality, max_frame_size))
        step = extraction_step_seconds(rate)
        timestamps = [round(min(index * step, source_duration_sec), 6) for index in indices]
        try:
            frame_result = self.ocr_frame_processor(
                source_path,
                workspace / "ocr_frames",
                timestamps,
                jpeg_quality,
                max_frame_size,
            ) or {}
            frame_paths = [Path(path) for path in (frame_result.get("frame_paths") or [])][:3]
            if not frame_paths:
                return {
                    **base,
                    "status": "unavailable",
                    "reason": "ocr_sample_frames_unavailable",
                    "expected_total_frames": expected_total_frames,
                    "sample_frame_indices": [index + 1 for index in indices],
                    "sample_timestamps_sec": timestamps,
                }
            ocr_sample = self.ocr_processor(frame_paths, languages) or {}
        except Exception as exc:
            return {
                **base,
                "status": "unavailable",
                "reason": "ocr_estimate_failed",
                "error_message": str(exc),
                "expected_total_frames": expected_total_frames,
                "sample_frame_indices": [index + 1 for index in indices],
                "sample_timestamps_sec": timestamps,
            }

        sample_frames = int(ocr_sample.get("sample_frames") or len(frame_paths))
        sample_runtime_sec = self._rounded(ocr_sample.get("sample_runtime_sec"))
        average_sec_per_frame = ocr_sample.get("average_sec_per_frame")
        if average_sec_per_frame is None and sample_runtime_sec is not None and sample_frames:
            average_sec_per_frame = sample_runtime_sec / sample_frames
        average_sec_per_frame = self._rounded(average_sec_per_frame)
        estimated_runtime = (
            float(average_sec_per_frame) * expected_total_frames
            if average_sec_per_frame is not None
            else None
        )
        if estimated_runtime is None:
            return {
                **base,
                "status": "unavailable",
                "reason": "ocr_estimate_failed",
                "expected_total_frames": expected_total_frames,
                "sample_frames": sample_frames,
                "sample_runtime_sec": sample_runtime_sec,
            }
        return {
            **base,
            "status": "complete",
            "reason": None,
            "expected_total_frames": expected_total_frames,
            "sample_frames": sample_frames,
            "sample_frame_indices": [index + 1 for index in indices],
            "sample_timestamps_sec": timestamps,
            "sample_runtime_sec": sample_runtime_sec,
            "average_sec_per_frame": average_sec_per_frame,
            "median_sec_per_frame": self._rounded(ocr_sample.get("median_sec_per_frame")),
            "estimated_full_runtime_sec": self._rounded(estimated_runtime),
            "included_in_total": True,
        }

    def _easyocr_status(self, ocr_plan: dict) -> dict:
        if self.ocr_status_reader is None:
            available = bool(ocr_plan.get("engine_available"))
            return {"available": available, "status": "available" if available else "unavailable"}
        try:
            return self.ocr_status_reader() or {}
        except Exception as exc:
            return {"available": False, "status": "check_failed", "error_message": str(exc)}

    @staticmethod
    def _ocr_sample_seed(item: dict, rate: dict, jpeg_quality: int, max_frame_size: str) -> str:
        payload = {
            "job_id": item.get("job_id"),
            "index": item.get("index"),
            "source_path": item.get("source_path"),
            "source_url": item.get("source_url"),
            "source_filename": item.get("source_filename"),
            "rate": rate,
            "jpeg_quality": jpeg_quality,
            "max_frame_size": max_frame_size,
        }
        return json.dumps(payload, sort_keys=True, default=str)

    def _source_path(self, item: dict) -> Path:
        path_value = (
            item.get("source_path")
            or item.get("downloaded_media_path")
            or item.get("downloaded_video_path")
            or item.get("downloaded_audio_path")
        )
        if not path_value and item.get("source_type") == "url":
            raise RuntimeEstimateError("url_download_required", "URL media must be downloaded before estimate.")
        if not path_value:
            raise RuntimeEstimateError("source_unavailable", "Source file is unavailable.")
        source_path = Path(path_value)
        if not source_path.is_file():
            raise RuntimeEstimateError("source_unavailable", "Source file is unavailable.")
        return source_path

    def _source_duration(self, item: dict, source_path: Path) -> float | None:
        duration = self.duration_reader(source_path)
        if duration is None:
            duration = item.get("audio_duration_sec")
        if duration is None:
            duration = (item.get("video_metadata") or {}).get("duration_sec")
        try:
            return float(duration) if duration is not None and math.isfinite(float(duration)) else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _rounded(value: float | None) -> float | None:
        return round(float(value), 3) if value is not None else None
