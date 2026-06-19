import math
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from . import config
from .frame_extractor import estimate_frame_count, normalize_frame_rate, normalize_jpeg_quality
from .utils import audio_duration_seconds


DEFAULT_SAMPLE_DURATION_SEC = 60.0


class RuntimeEstimateError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


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


class RuntimeEstimator:
    def __init__(
        self,
        *,
        audio_processor: Callable[[Path, str, str], dict],
        frame_processor: Callable[[Path, Path, float, dict, int], dict],
        duration_reader: Callable[[Path], float | None] = audio_duration_seconds,
        sample_preparer: Callable[[Path, float, float, Path], Path] = prepare_audio_sample,
        temp_root: Path | None = None,
        sample_duration_sec: float = DEFAULT_SAMPLE_DURATION_SEC,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.audio_processor = audio_processor
        self.frame_processor = frame_processor
        self.duration_reader = duration_reader
        self.sample_preparer = sample_preparer
        self.temp_root = temp_root or config.TEMP_DIR
        self.sample_duration_sec = float(sample_duration_sec)
        self.clock = clock

    def estimate(self, item: dict) -> dict:
        plan = item.get("processing_plan") or {}
        audio_plan = plan.get("audio") or {}
        frames_plan = plan.get("frames") or {}
        audio_enabled = bool(audio_plan.get("enabled"))
        frames_enabled = bool(frames_plan.get("enabled"))
        created_at = datetime.now().astimezone().isoformat(timespec="seconds")

        if not audio_enabled and not frames_enabled:
            return {
                "status": "complete",
                "created_at": created_at,
                "approximate": True,
                "no_enabled_operations": True,
                "audio": {"enabled": False},
                "frames": {"enabled": False},
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

            if audio_enabled:
                model = str(audio_plan.get("model") or config.WHISPER_MODEL)
                device = str(audio_plan.get("device") or config.WHISPER_DEVICE or "auto")
                sample_path = self.sample_preparer(source_path, sample_duration_sec, source_duration_sec, workspace)
                started = self.clock()
                processor_result = self.audio_processor(sample_path, model, device) or {}
                sample_runtime_sec = max(0.0, self.clock() - started)
                audio_result = {
                    "enabled": True,
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
                }

            if frames_enabled:
                rate = normalize_frame_rate(frames_plan.get("rate"))
                jpeg_quality = normalize_jpeg_quality(frames_plan.get("jpeg_quality"))
                frames_workspace = workspace / "frames"
                frames_workspace.mkdir(parents=True, exist_ok=True)
                started = self.clock()
                processor_result = self.frame_processor(
                    source_path,
                    frames_workspace,
                    sample_duration_sec,
                    rate,
                    jpeg_quality,
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
                    "sample_frames": sample_frames,
                    "estimated_total_frames": estimated_total_frames,
                    "sample_runtime_sec": self._rounded(sample_runtime_sec),
                    "estimated_full_runtime_sec": self._rounded(estimated_runtime),
                }

        total_runtime = sum(
            float(result.get("estimated_full_runtime_sec") or 0)
            for result in (audio_result, frames_result)
            if result.get("enabled")
        )
        return {
            "status": "complete",
            "created_at": created_at,
            "sample_duration_sec": self._rounded(sample_duration_sec),
            "source_duration_sec": self._rounded(source_duration_sec),
            "approximate": True,
            "audio": audio_result,
            "frames": frames_result,
            "total_estimated_full_runtime_sec": self._rounded(total_runtime),
        }

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
