import logging
import math
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

from . import config
from .transcript_store import safe_filename_part, source_stem_for
from .utils import timestamp_for_filename, write_json_file_atomic


logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = config.SUPPORTED_VIDEO_EXTENSIONS
DEFAULT_FRAME_RATE = {"mode": "interval", "seconds": 10}
DEFAULT_JPEG_QUALITY = 90
ALLOWED_INTERVAL_SECONDS = (30, 20, 15, 10, 5, 3, 2, 1)
ALLOWED_EXTRACTION_FPS = (2, 3, 5, 10, 15, 20, 30)
ALLOWED_JPEG_QUALITIES = (75, 80, 85, 90, 95, 100)


class FrameExtractionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        frame_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.frame_name = frame_name


def is_video_path(path_or_name: Path | str) -> bool:
    return Path(path_or_name).suffix.lower() in VIDEO_EXTENSIONS


def normalize_frame_rate(rate: dict | None) -> dict:
    if not rate:
        return dict(DEFAULT_FRAME_RATE)

    mode = str(rate.get("mode") or "").strip().lower()
    if mode == "interval":
        try:
            seconds = int(rate.get("seconds"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Frame extraction interval must be a number of seconds.") from exc
        if seconds not in ALLOWED_INTERVAL_SECONDS:
            allowed = ", ".join(str(item) for item in ALLOWED_INTERVAL_SECONDS)
            raise ValueError(f"Frame extraction interval must be one of: {allowed}.")
        return {"mode": "interval", "seconds": seconds}

    if mode == "fps":
        try:
            fps = int(rate.get("fps"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Frame extraction FPS must be a number.") from exc
        if fps not in ALLOWED_EXTRACTION_FPS:
            allowed = ", ".join(str(item) for item in ALLOWED_EXTRACTION_FPS)
            raise ValueError(f"Frame extraction FPS must be one of: {allowed}.")
        return {"mode": "fps", "fps": fps}

    raise ValueError("Frame extraction rate mode must be interval or fps.")


def normalize_jpeg_quality(value: int | str | None) -> int:
    if value is None or value == "":
        return DEFAULT_JPEG_QUALITY
    try:
        quality = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("JPEG quality must be a number.") from exc
    if quality < 60 or quality > 100:
        raise ValueError("JPEG quality must be between 60 and 100.")
    return quality


def normalize_frame_extraction_settings(settings: dict | None) -> dict:
    settings = settings or {}
    return {
        "rate": normalize_frame_rate(settings.get("rate")),
        "jpeg_quality": normalize_jpeg_quality(settings.get("jpeg_quality")),
    }


def extraction_step_seconds(rate: dict) -> float:
    normalized = normalize_frame_rate(rate)
    if normalized["mode"] == "interval":
        return float(normalized["seconds"])
    return 1.0 / float(normalized["fps"])


def requested_extraction_fps(rate: dict) -> float:
    normalized = normalize_frame_rate(rate)
    if normalized["mode"] == "fps":
        return float(normalized["fps"])
    return 1.0 / float(normalized["seconds"])


def estimate_frame_count(duration_sec: float | None, rate: dict | None) -> int | None:
    if duration_sec is None or duration_sec < 0:
        return None
    if duration_sec == 0:
        return 1
    step = extraction_step_seconds(rate or DEFAULT_FRAME_RATE)
    if step <= 0:
        return None
    return int(math.floor(float(duration_sec) / step)) + 1


def estimate_disk_usage_bytes(
    frame_count: int | None,
    width: int | None,
    height: int | None,
    jpeg_quality: int | None,
) -> dict | None:
    if not frame_count or not width or not height:
        return None
    quality_factor = max(0.75, min(1.2, (jpeg_quality or DEFAULT_JPEG_QUALITY) / DEFAULT_JPEG_QUALITY))
    pixels = int(width) * int(height)
    min_bytes = int(frame_count * pixels * 0.045 * quality_factor)
    max_bytes = int(frame_count * pixels * 0.18 * quality_factor)
    return {
        "min_bytes": max(1, min_bytes),
        "max_bytes": max(1, max_bytes),
    }


def read_video_metadata(video_path: Path) -> dict:
    if not video_path.exists():
        raise FrameExtractionError("Video file was not found.")

    try:
        import cv2
    except Exception as exc:
        raise FrameExtractionError(f"OpenCV is not available for frame extraction: {exc}") from exc

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise FrameExtractionError("Could not open the video file for frame extraction.")

        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0) or None
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0) or None
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0) or None
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0) or None
        duration_sec = float(frame_count / fps) if frame_count and fps and fps > 0 else None

        if not width or not height:
            ok, frame = capture.read()
            if not ok or frame is None:
                raise FrameExtractionError("Could not decode the first video frame.")
            height, width = frame.shape[:2]

        return {
            "duration_sec": round(duration_sec, 3) if duration_sec is not None else None,
            "fps": round(fps, 3) if fps is not None else None,
            "width": int(width) if width else None,
            "height": int(height) if height else None,
            "frame_count": frame_count,
        }
    except FrameExtractionError:
        raise
    except Exception as exc:
        raise FrameExtractionError(f"Could not read the video file: {exc}") from exc
    finally:
        capture.release()


def relative_project_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(config.BASE_DIR.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def frame_timestamp_label(seconds: float) -> str:
    total_ms = int(round(max(0.0, float(seconds)) * 1000))
    whole_seconds, milliseconds = divmod(total_ms, 1000)
    return f"t{whole_seconds:06d}.{milliseconds:03d}"


def frame_timestamps(duration_sec: float | None, rate: dict | None) -> list[float]:
    step = extraction_step_seconds(rate or DEFAULT_FRAME_RATE)
    if duration_sec is None:
        return [0.0]
    duration = max(0.0, float(duration_sec))
    count = estimate_frame_count(duration, rate) or 1
    return [round(index * step, 6) for index in range(count) if index * step <= duration + 1e-9]


class VideoFrameExtractor:
    def __init__(self, recordings_dir: Path | None = None) -> None:
        self.recordings_dir = recordings_dir or config.RECORDINGS_DIR

    def estimate(self, video_path: Path, settings: dict | None = None) -> dict:
        normalized = normalize_frame_extraction_settings(settings)
        metadata = read_video_metadata(video_path)
        frame_count = estimate_frame_count(metadata.get("duration_sec"), normalized["rate"])
        return {
            "video_metadata": metadata,
            "estimated_frame_count": frame_count,
            "estimated_disk_usage": estimate_disk_usage_bytes(
                frame_count,
                metadata.get("width"),
                metadata.get("height"),
                normalized["jpeg_quality"],
            ),
            "estimated_frames_warning": bool(frame_count and frame_count > 1000),
        }

    def extract_frames(
        self,
        *,
        source_path: Path,
        source_filename: str | None = None,
        output_base: str | None = None,
        rate: dict | None = None,
        jpeg_quality: int | str | None = None,
        cancel_event: threading.Event | None = None,
        progress_callback: Callable[[dict], None] | None = None,
        source_metadata: dict | None = None,
    ) -> dict:
        settings = normalize_frame_extraction_settings({"rate": rate, "jpeg_quality": jpeg_quality})
        source_name = source_filename or source_path.name
        source_stem = source_stem_for(source_name)
        base = safe_filename_part(output_base or f"{source_stem}_{timestamp_for_filename()}", max_length=72)
        frames_dir = self._reserve_frames_dir(base)
        started_at = datetime.now().astimezone().isoformat(timespec="seconds")
        index_payload = self._base_index_payload(
            source_path=source_path,
            source_filename=source_name,
            source_stem=source_stem,
            output_base=base,
            frames_dir=frames_dir,
            settings=settings,
            started_at=started_at,
            source_metadata=source_metadata,
        )
        write_json_file_atomic(frames_dir / "frames_index.json", index_payload)

        try:
            metadata = read_video_metadata(source_path)
            index_payload["video_metadata"] = metadata
            estimated_count = estimate_frame_count(metadata.get("duration_sec"), settings["rate"])
            index_payload["estimated_frame_count"] = estimated_count
            index_payload["requested_fps_exceeds_source_fps"] = self._requested_fps_exceeds_source(
                settings["rate"],
                metadata.get("fps"),
            )

            import cv2

            capture = cv2.VideoCapture(str(source_path))
            if not capture.isOpened():
                raise FrameExtractionError("Could not open the video file for frame extraction.")

            try:
                timestamps = frame_timestamps(metadata.get("duration_sec"), settings["rate"])
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), settings["jpeg_quality"]]
                for frame_index, timestamp_sec in enumerate(timestamps, start=1):
                    if cancel_event is not None and cancel_event.is_set():
                        index_payload.update(
                            {
                                "status": "cancelled",
                                "completed": False,
                                "cancelled": True,
                                "cancelled_at_t": round(timestamp_sec, 3),
                                "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                                "extracted_frame_count": len(index_payload["frames"]),
                            }
                        )
                        write_json_file_atomic(frames_dir / "frames_index.json", index_payload)
                        return self._result_payload(index_payload)

                    frame = self._read_frame_at(capture, cv2, timestamp_sec, frame_index)
                    if frame is None:
                        if frame_index == 1:
                            raise FrameExtractionError("Could not decode the first video frame.")
                        break

                    frame_name = f"frame_{frame_index:06d}__{frame_timestamp_label(timestamp_sec)}.jpg"
                    frame_path = frames_dir / frame_name
                    self._write_jpeg_frame(cv2, frame_path, frame, encode_params, frame_name)

                    height, width = frame.shape[:2]
                    index_payload["frames"].append(
                        {
                            "index": frame_index,
                            "t": round(timestamp_sec, 3),
                            "file": frame_name,
                            "width": int(width),
                            "height": int(height),
                        }
                    )
                    index_payload["extracted_frame_count"] = len(index_payload["frames"])
                    if progress_callback is not None:
                        progress_callback(self._result_payload(index_payload))
                    write_json_file_atomic(frames_dir / "frames_index.json", index_payload)
            finally:
                capture.release()

            index_payload.update(
                {
                    "status": "completed",
                    "completed": True,
                    "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "extracted_frame_count": len(index_payload["frames"]),
                }
            )
            write_json_file_atomic(frames_dir / "frames_index.json", index_payload)
            return self._result_payload(index_payload)
        except Exception as exc:
            logger.exception("Frame extraction failed: source=%s frames_dir=%s", source_path, frames_dir)
            index_payload.update(
                {
                    "status": "failed",
                    "completed": False,
                    "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "error_message": str(exc),
                    "error_code": getattr(exc, "error_code", None),
                    "error_filename": getattr(exc, "frame_name", None),
                    "extracted_frame_count": len(index_payload["frames"]),
                }
            )
            write_json_file_atomic(frames_dir / "frames_index.json", index_payload)
            return self._result_payload(index_payload)

    def _reserve_frames_dir(self, output_base: str) -> Path:
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        base_name = f"{output_base}__frames"
        frames_dir = self.recordings_dir / base_name
        counter = 2
        while frames_dir.exists():
            frames_dir = self.recordings_dir / f"{base_name}_{counter}"
            counter += 1
        frames_dir.mkdir(parents=True, exist_ok=False)
        return frames_dir

    def _base_index_payload(
        self,
        *,
        source_path: Path,
        source_filename: str,
        source_stem: str,
        output_base: str,
        frames_dir: Path,
        settings: dict,
        started_at: str,
        source_metadata: dict | None = None,
    ) -> dict:
        rate = settings["rate"]
        extraction = {
            "mode": rate["mode"],
            "seconds": rate.get("seconds"),
            "requested_fps": rate.get("fps"),
            "jpeg_quality": settings["jpeg_quality"],
        }
        payload = {
            "schema_version": 1,
            "status": "running",
            "completed": False,
            "source_video": source_filename,
            "source_path": relative_project_path(source_path),
            "source_stem": source_stem,
            "output_base": output_base,
            "frames_dir": frames_dir.name,
            "frames_path": relative_project_path(frames_dir),
            "extraction": extraction,
            "video_metadata": None,
            "estimated_frame_count": None,
            "extracted_frame_count": 0,
            "started_at": started_at,
            "finished_at": None,
            "requested_fps_exceeds_source_fps": False,
            "frames": [],
        }
        for key in ("source_type", "source_url", "source_title", "source_platform", "downloaded_media_path", "downloaded_video_path"):
            if source_metadata and source_metadata.get(key):
                payload[key] = source_metadata[key]
        return payload

    @staticmethod
    def _requested_fps_exceeds_source(rate: dict, source_fps: float | None) -> bool:
        if not source_fps or source_fps <= 0:
            return False
        return requested_extraction_fps(rate) > float(source_fps)

    @staticmethod
    def _read_frame_at(capture, cv2, timestamp_sec: float, frame_index: int):
        if frame_index == 1:
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            capture.set(cv2.CAP_PROP_POS_MSEC, max(0.0, timestamp_sec) * 1000.0)
        ok, frame = capture.read()
        return frame if ok else None

    @staticmethod
    def _write_jpeg_frame(cv2, frame_path: Path, frame, encode_params: list[int], frame_name: str) -> None:
        frame_path.parent.mkdir(parents=True, exist_ok=True)
        ok, encoded = cv2.imencode(".jpg", frame, encode_params)
        if not ok:
            raise FrameExtractionError(
                f"Could not write JPEG frame: {frame_name}",
                error_code="frame_write_failed",
                frame_name=frame_name,
            )
        try:
            encoded.tofile(str(frame_path))
        except Exception as exc:
            raise FrameExtractionError(
                f"Could not write JPEG frame: {frame_name}",
                error_code="frame_write_failed",
                frame_name=frame_name,
            ) from exc

    @staticmethod
    def _result_payload(index_payload: dict) -> dict:
        return {
            "status": index_payload.get("status"),
            "completed": index_payload.get("completed"),
            "cancelled": index_payload.get("cancelled", False),
            "error_message": index_payload.get("error_message"),
            "error_code": index_payload.get("error_code"),
            "error_filename": index_payload.get("error_filename"),
            "frames_dir": index_payload.get("frames_dir"),
            "frames_path": index_payload.get("frames_path"),
            "frames_index_path": f"{index_payload.get('frames_path')}/frames_index.json"
            if index_payload.get("frames_path")
            else None,
            "estimated_frame_count": index_payload.get("estimated_frame_count"),
            "extracted_frame_count": index_payload.get("extracted_frame_count", 0),
            "cancelled_at_t": index_payload.get("cancelled_at_t"),
            "requested_fps_exceeds_source_fps": index_payload.get("requested_fps_exceeds_source_fps", False),
            "video_metadata": index_payload.get("video_metadata"),
            "output_base": index_payload.get("output_base"),
        }
