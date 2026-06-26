import json
import logging
import shutil
import socket
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from . import config
from .transcript_store import safe_filename_part
from .url_download_manager import normalize_url_download_settings
from .utils import timestamp_for_filename


logger = logging.getLogger(__name__)

DIRECT_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
DIRECT_AUDIO_EXTENSIONS = set(config.SUPPORTED_AUDIO_ONLY_EXTENSIONS)
DIRECT_MEDIA_EXTENSIONS = DIRECT_VIDEO_EXTENSIONS | DIRECT_AUDIO_EXTENSIONS
DIRECT_DOWNLOAD_TIMEOUT_SEC = 30
DIRECT_DOWNLOAD_CHUNK_BYTES = 1024 * 1024
DEFAULT_AUDIO_FORMAT = "m4a/bestaudio/best"
DEFAULT_VIDEO_FORMAT = "bv*+ba/bestvideo+bestaudio/best"
VIDEO_FORMAT_PROFILES = {
    "auto": DEFAULT_VIDEO_FORMAT,
    "best_for_extraction": (
        "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/"
        "bv*[height<=720]+ba/b[height<=720]/bv*[height<=1080]+ba/b[height<=1080]/best"
    ),
    "best_quality": "bv*+ba/best",
    "smallest_file": "worstvideo+worstaudio/worst",
    "prefer_webm": "bv*[ext=webm]+ba[ext=webm]/b[ext=webm]/bv*+ba/best",
    "prefer_mp4": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/best",
    "prefer_mkv": "bv*[ext=mkv]+ba/b[ext=mkv]/bv*+ba/best",
    "prefer_mov": "b[ext=mov]/bv*[ext=mov]+ba/bv*+ba/best",
    "prefer_avi": "b[ext=avi]/bv*[ext=avi]+ba/bv*+ba/best",
    "audio_friendly": DEFAULT_VIDEO_FORMAT,
}
AUDIO_FORMAT_PROFILES = {
    "auto": DEFAULT_AUDIO_FORMAT,
    "best_for_extraction": DEFAULT_AUDIO_FORMAT,
    "best_quality": "bestaudio/best",
    "smallest_file": "worstaudio/worst",
    "prefer_webm": "bestaudio[ext=webm]/bestaudio/best",
    "prefer_mp4": DEFAULT_AUDIO_FORMAT,
    "prefer_mkv": DEFAULT_AUDIO_FORMAT,
    "prefer_mov": DEFAULT_AUDIO_FORMAT,
    "prefer_avi": DEFAULT_AUDIO_FORMAT,
    "audio_friendly": DEFAULT_AUDIO_FORMAT,
}
VIDEO_MERGE_FORMATS = {
    "best_for_extraction": "mp4/mkv",
    "prefer_webm": "webm/mkv",
    "prefer_mp4": "mp4/mkv",
    "prefer_mkv": "mkv",
}


def bounded_video_format(profile: str, max_video_height: str) -> str:
    base = VIDEO_FORMAT_PROFILES.get(profile, DEFAULT_VIDEO_FORMAT)
    if max_video_height == "auto":
        return base
    height_filter = f"height<={max_video_height}"
    bounded_profiles = {
        "auto": f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}",
        "best_for_extraction": (
            f"bv*[{height_filter}][ext=mp4]+ba[ext=m4a]/b[{height_filter}][ext=mp4]/"
            f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}"
        ),
        "best_quality": f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}",
        "smallest_file": f"worstvideo[{height_filter}]+worstaudio/worst[{height_filter}]/{base}",
        "prefer_webm": (
            f"bv*[{height_filter}][ext=webm]+ba[ext=webm]/b[{height_filter}][ext=webm]/"
            f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}"
        ),
        "prefer_mp4": (
            f"bv*[{height_filter}][ext=mp4]+ba[ext=m4a]/b[{height_filter}][ext=mp4]/"
            f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}"
        ),
        "prefer_mkv": (
            f"bv*[{height_filter}][ext=mkv]+ba/b[{height_filter}][ext=mkv]/"
            f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}"
        ),
        "prefer_mov": (
            f"b[{height_filter}][ext=mov]/bv*[{height_filter}][ext=mov]+ba/"
            f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}"
        ),
        "prefer_avi": (
            f"b[{height_filter}][ext=avi]/bv*[{height_filter}][ext=avi]+ba/"
            f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}"
        ),
        "audio_friendly": f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}",
    }
    return bounded_profiles.get(profile, f"bv*[{height_filter}]+ba/b[{height_filter}]/best[{height_filter}]/{base}")


def resolve_url_download_options(settings: dict | None, *, needs_video: bool) -> dict:
    normalized = normalize_url_download_settings(settings)
    profile = normalized["format_profile"]
    if profile == "custom":
        format_string = normalized["custom_format"]
    else:
        if needs_video:
            format_string = bounded_video_format(profile, normalized["max_video_height"])
        else:
            format_string = AUDIO_FORMAT_PROFILES.get(profile, DEFAULT_AUDIO_FORMAT)
    return {
        **normalized,
        "format_string": format_string,
        "merge_output_format": VIDEO_MERGE_FORMATS.get(profile, "mkv") if needs_video else None,
    }


class UrlDownloadError(RuntimeError):
    download_error = True

    def __init__(self, message: str, *, technical_details: str | None = None) -> None:
        super().__init__(message)
        self.technical_details = technical_details or message


class UrlDownloadCancelled(RuntimeError):
    cancelled = True

    def __init__(self) -> None:
        super().__init__("URL download was cancelled.")
        self.technical_details = "URL download was cancelled by the user."


def get_direct_media_url_extension(url: str) -> str | None:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    suffix = Path(unquote(parsed.path)).suffix.lower()
    return suffix if suffix in DIRECT_MEDIA_EXTENSIONS else None


def is_direct_media_url(url: str) -> bool:
    return get_direct_media_url_extension(url) is not None


@dataclass(frozen=True)
class DownloadedAudio:
    source_path: Path
    source_title: str | None
    source_platform: str
    audio_duration_sec: float | None

    def as_dict(self) -> dict:
        payload = asdict(self)
        payload["source_path"] = str(self.source_path)
        payload["downloaded_audio_path"] = str(self.source_path)
        return payload


class UrlDownloader:
    def __init__(self, downloads_dir: Path | None = None) -> None:
        self.downloads_dir = downloads_dir or config.DOWNLOADS_DIR

    def download(
        self,
        source_url: str,
        cancel_event: threading.Event | None = None,
        progress_callback: Callable[[dict], None] | None = None,
        download_settings: dict | None = None,
    ) -> dict:
        url = self._validate_url(source_url)
        download_started_at = time.monotonic()
        resolved_options = resolve_url_download_options(download_settings, needs_video=False)
        direct_extension = get_direct_media_url_extension(url)
        if direct_extension:
            return self._download_direct_media(
                url,
                direct_extension,
                cancel_event,
                progress_callback,
                resolved_options=resolved_options,
                download_started_at=download_started_at,
            )

        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"url__{timestamp_for_filename()}__{uuid4().hex[:8]}"
        output_template = str(self.downloads_dir / f"{prefix}.%(ext)s")

        try:
            import yt_dlp
        except ImportError as exc:
            raise RuntimeError(
                "Не найден yt-dlp. Установите зависимости из requirements-cpu.txt и перезапустите run.bat."
            ) from exc

        cancelled = False

        def progress_hook(progress: dict) -> None:
            nonlocal cancelled
            if cancel_event is not None and cancel_event.is_set():
                cancelled = True
                raise UrlDownloadCancelled()
            if progress.get("status") == "downloading":
                self._emit_progress(
                    progress_callback,
                    self._yt_dlp_progress(progress),
                )

        def postprocessor_hook(_progress: dict) -> None:
            nonlocal cancelled
            if cancel_event is not None and cancel_event.is_set():
                cancelled = True
                raise UrlDownloadCancelled()

        options = {
            "format": resolved_options["format_string"],
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 15,
            "progress_hooks": [progress_hook],
            "postprocessor_hooks": [postprocessor_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        }

        logger.info("Downloading URL audio: url=%s output=%s", url, output_template)
        self._emit_progress(progress_callback, self._indeterminate_progress("yt_dlp"))
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                prepared_path = Path(downloader.prepare_filename(info))
        except Exception as exc:
            self._cleanup_prefix(prefix)
            if cancelled or (cancel_event is not None and cancel_event.is_set()) or getattr(exc, "cancelled", False):
                logger.info("URL audio download cancelled: url=%s", url)
                raise UrlDownloadCancelled() from exc
            logger.exception("URL audio download failed: url=%s", url)
            raise self._friendly_download_error(exc, prefix="Не удалось скачать аудио по ссылке") from exc

        source_path = self._find_downloaded_audio(prefix, prepared_path)
        if source_path is None:
            self._cleanup_prefix(prefix)
            raise RuntimeError("yt-dlp завершил работу, но извлеченный аудиофайл не найден.")

        result = DownloadedAudio(
            source_path=source_path,
            source_title=self._optional_text(info.get("title")),
            source_platform=self._platform(info),
            audio_duration_sec=self._optional_float(info.get("duration")),
        )
        logger.info(
            "URL audio downloaded: url=%s file=%s platform=%s title=%s duration=%s",
            url,
            result.source_path,
            result.source_platform,
            result.source_title,
            result.audio_duration_sec,
        )
        self._emit_progress(progress_callback, self._completed_progress(result.source_path.stat().st_size, "yt_dlp"))
        payload = result.as_dict()
        payload["url_download_diagnostics"] = self._download_diagnostics(
            result.source_path,
            resolved_options,
            download_started_at,
        )
        return payload

    def download_video(
        self,
        source_url: str,
        cancel_event: threading.Event | None = None,
        progress_callback: Callable[[dict], None] | None = None,
        download_settings: dict | None = None,
    ) -> dict:
        url = self._validate_url(source_url)
        download_started_at = time.monotonic()
        resolved_options = resolve_url_download_options(download_settings, needs_video=True)
        direct_extension = get_direct_media_url_extension(url)
        if direct_extension:
            return self._download_direct_media(
                url,
                direct_extension,
                cancel_event,
                progress_callback,
                resolved_options=resolved_options,
                download_started_at=download_started_at,
            )

        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"url_video__{timestamp_for_filename()}__{uuid4().hex[:8]}"
        output_template = str(self.downloads_dir / f"{prefix}.%(ext)s")

        try:
            import yt_dlp
        except ImportError as exc:
            raise RuntimeError(
                "Не найден yt-dlp. Установите зависимости из requirements-cpu.txt и перезапустите run.bat."
            ) from exc

        cancelled = False

        def progress_hook(progress: dict) -> None:
            nonlocal cancelled
            if cancel_event is not None and cancel_event.is_set():
                cancelled = True
                raise UrlDownloadCancelled()
            if progress.get("status") == "downloading":
                self._emit_progress(progress_callback, self._yt_dlp_progress(progress))

        def postprocessor_hook(_progress: dict) -> None:
            nonlocal cancelled
            if cancel_event is not None and cancel_event.is_set():
                cancelled = True
                raise UrlDownloadCancelled()

        options = {
            "format": resolved_options["format_string"],
            "outtmpl": output_template,
            "merge_output_format": resolved_options["merge_output_format"],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 15,
            "progress_hooks": [progress_hook],
            "postprocessor_hooks": [postprocessor_hook],
        }

        logger.info("Downloading URL video: url=%s output=%s", url, output_template)
        self._emit_progress(progress_callback, self._indeterminate_progress("yt_dlp"))
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                prepared_path = Path(downloader.prepare_filename(info))
        except Exception as exc:
            self._cleanup_prefix(prefix)
            if cancelled or (cancel_event is not None and cancel_event.is_set()) or getattr(exc, "cancelled", False):
                logger.info("URL video download cancelled: url=%s", url)
                raise UrlDownloadCancelled() from exc
            logger.exception("URL video download failed: url=%s", url)
            raise self._friendly_download_error(exc, prefix="Не удалось скачать видео по ссылке") from exc

        source_path = self._find_downloaded_video(prefix, prepared_path)
        if source_path is None:
            self._cleanup_prefix(prefix)
            raise RuntimeError("yt-dlp завершил работу, но видеофайл не найден.")

        result = DownloadedAudio(
            source_path=source_path,
            source_title=self._optional_text(info.get("title")),
            source_platform=self._platform(info),
            audio_duration_sec=self._optional_float(info.get("duration")),
        ).as_dict()
        result["downloaded_media_path"] = str(source_path)
        result["downloaded_video_path"] = str(source_path)
        result["url_download_diagnostics"] = self._download_diagnostics(
            source_path,
            resolved_options,
            download_started_at,
        )
        logger.info(
            "URL video downloaded: url=%s file=%s platform=%s title=%s duration=%s",
            url,
            source_path,
            result["source_platform"],
            result["source_title"],
            result["audio_duration_sec"],
        )
        self._emit_progress(progress_callback, self._completed_progress(source_path.stat().st_size, "yt_dlp"))
        return result

    def _download_direct_media(
        self,
        url: str,
        extension: str,
        cancel_event: threading.Event | None = None,
        progress_callback: Callable[[dict], None] | None = None,
        *,
        resolved_options: dict | None = None,
        download_started_at: float | None = None,
    ) -> dict:
        resolved_options = resolved_options or resolve_url_download_options(None, needs_video=extension in DIRECT_VIDEO_EXTENSIONS)
        download_started_at = download_started_at or time.monotonic()
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        target_path = self._reserve_download_path(self._direct_media_filename(url, extension))
        partial_path = target_path.with_name(f"{target_path.name}.{uuid4().hex[:8]}.part")
        request = Request(url, headers={"User-Agent": "LocalMediaTranscriber/1.0"})

        logger.info("Downloading direct media URL: url=%s output=%s", url, target_path)
        try:
            with urlopen(request, timeout=DIRECT_DOWNLOAD_TIMEOUT_SEC) as response:
                status = getattr(response, "status", None)
                if status is None and hasattr(response, "getcode"):
                    status = response.getcode()
                if status and int(status) >= 400:
                    raise HTTPError(url, int(status), f"HTTP {status}", getattr(response, "headers", None), None)

                total_bytes = self._content_length(response)
                downloaded_bytes = 0
                started_at = time.monotonic()
                self._emit_progress(
                    progress_callback,
                    self._download_progress(downloaded_bytes, total_bytes, started_at, "direct"),
                )
                with partial_path.open("xb") as file:
                    while True:
                        if cancel_event is not None and cancel_event.is_set():
                            raise UrlDownloadCancelled()
                        chunk = response.read(DIRECT_DOWNLOAD_CHUNK_BYTES)
                        if not chunk:
                            break
                        file.write(chunk)
                        downloaded_bytes += len(chunk)
                        self._emit_progress(
                            progress_callback,
                            self._download_progress(downloaded_bytes, total_bytes, started_at, "direct"),
                        )
                if cancel_event is not None and cancel_event.is_set():
                    raise UrlDownloadCancelled()
        except UrlDownloadCancelled:
            self._safe_unlink_partial(partial_path)
            logger.info("Direct media download cancelled: url=%s", url)
            raise
        except Exception as exc:
            self._safe_unlink_partial(partial_path)
            logger.exception("Direct media download failed: url=%s", url)
            raise self._friendly_download_error(exc, prefix="Не удалось скачать медиафайл") from exc

        if not partial_path.exists() or partial_path.stat().st_size <= 0:
            self._safe_unlink_partial(partial_path)
            raise UrlDownloadError(
                "Не удалось скачать медиафайл: скачанный файл пустой.",
                technical_details="Downloaded direct media file is empty.",
            )
        try:
            partial_path.replace(target_path)
        except OSError as exc:
            self._safe_unlink_partial(partial_path)
            raise UrlDownloadError(
                "Не удалось завершить скачивание медиафайла.",
                technical_details=str(exc),
            ) from exc

        result = DownloadedAudio(
            source_path=target_path,
            source_title=target_path.name,
            source_platform="direct",
            audio_duration_sec=None,
        ).as_dict()
        result["downloaded_media_path"] = str(target_path)
        if extension in DIRECT_VIDEO_EXTENSIONS:
            result["downloaded_video_path"] = str(target_path)
        direct_options = {**resolved_options, "format_string": "direct_url"}
        result["url_download_diagnostics"] = self._download_diagnostics(
            target_path,
            direct_options,
            download_started_at,
        )
        logger.info("Direct media downloaded: url=%s file=%s size=%s", url, target_path, target_path.stat().st_size)
        self._emit_progress(progress_callback, self._completed_progress(target_path.stat().st_size, "direct"))
        return result

    def _download_diagnostics(self, path: Path, resolved_options: dict, started_at: float) -> dict:
        diagnostics = {
            "downloaded_container": path.suffix.lower().lstrip(".") or None,
            "video_codec": None,
            "audio_codec": None,
            "resolution": None,
            "fps": None,
            "file_size_mb": round(path.stat().st_size / (1024 * 1024), 3),
            "download_time_sec": round(max(0.0, time.monotonic() - started_at), 3),
            "url_download_format_profile": resolved_options["format_profile"],
            "url_download_max_video_height": resolved_options["max_video_height"],
            "yt_dlp_format_string_used": resolved_options["format_string"],
            "media_probe_status": "disabled",
        }
        if resolved_options.get("log_media_probe", True):
            diagnostics.update(self._probe_media(path))
        logger.info(
            "URL download diagnostics: file=%s profile=%s format=%s container=%s video_codec=%s "
            "audio_codec=%s resolution=%s fps=%s size_mb=%s download_sec=%s probe=%s",
            path,
            diagnostics["url_download_format_profile"],
            diagnostics["yt_dlp_format_string_used"],
            diagnostics["downloaded_container"],
            diagnostics["video_codec"],
            diagnostics["audio_codec"],
            diagnostics["resolution"],
            diagnostics["fps"],
            diagnostics["file_size_mb"],
            diagnostics["download_time_sec"],
            diagnostics["media_probe_status"],
        )
        return diagnostics

    @staticmethod
    def _probe_media(path: Path) -> dict:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return {"media_probe_status": "unavailable"}
        try:
            result = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-print_format",
                    "json",
                    "-show_entries",
                    "format=format_name:stream=codec_type,codec_name,width,height,r_frame_rate",
                    str(path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
            if result.returncode != 0:
                return {"media_probe_status": "check_failed"}
            payload = json.loads(result.stdout or "{}")
            streams = payload.get("streams") if isinstance(payload.get("streams"), list) else []
            video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
            audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
            width = video.get("width")
            height = video.get("height")
            return {
                "media_probe_status": "available",
                "video_codec": video.get("codec_name"),
                "audio_codec": audio.get("codec_name"),
                "resolution": f"{width}x{height}" if width and height else None,
                "fps": UrlDownloader._parse_frame_rate(video.get("r_frame_rate")),
            }
        except (OSError, ValueError, subprocess.SubprocessError):
            logger.warning("Could not probe downloaded URL media: path=%s", path, exc_info=True)
            return {"media_probe_status": "check_failed"}

    @staticmethod
    def _parse_frame_rate(value) -> float | None:
        text = str(value or "").strip()
        try:
            if "/" in text:
                numerator, denominator = text.split("/", 1)
                rate = float(numerator) / float(denominator)
            else:
                rate = float(text)
            return round(rate, 3) if rate > 0 else None
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    @staticmethod
    def _content_length(response) -> int | None:
        headers = getattr(response, "headers", None)
        value = headers.get("Content-Length") if headers is not None and hasattr(headers, "get") else None
        try:
            total = int(value) if value is not None else None
            return total if total and total > 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _emit_progress(callback: Callable[[dict], None] | None, progress: dict) -> None:
        if callback is not None:
            callback(progress)

    @staticmethod
    def _indeterminate_progress(source: str) -> dict:
        return {
            "mode": "indeterminate",
            "percent": None,
            "downloaded_bytes": 0,
            "total_bytes": None,
            "speed_bytes_per_sec": None,
            "eta_sec": None,
            "source": source,
        }

    @staticmethod
    def _completed_progress(downloaded_bytes: int, source: str) -> dict:
        return {
            "mode": "determinate",
            "percent": 100.0,
            "downloaded_bytes": downloaded_bytes,
            "total_bytes": downloaded_bytes,
            "speed_bytes_per_sec": None,
            "eta_sec": 0,
            "source": source,
        }

    @staticmethod
    def _download_progress(downloaded_bytes: int, total_bytes: int | None, started_at: float, source: str) -> dict:
        elapsed = max(0.001, time.monotonic() - started_at)
        speed = downloaded_bytes / elapsed if downloaded_bytes > 0 else None
        remaining = max(0, total_bytes - downloaded_bytes) if total_bytes is not None else None
        eta = remaining / speed if remaining is not None and speed else None
        percent = min(100.0, downloaded_bytes * 100.0 / total_bytes) if total_bytes else None
        return {
            "mode": "determinate" if total_bytes else "indeterminate",
            "percent": round(percent, 1) if percent is not None else None,
            "downloaded_bytes": downloaded_bytes,
            "total_bytes": total_bytes,
            "speed_bytes_per_sec": round(speed, 1) if speed is not None else None,
            "eta_sec": round(eta, 1) if eta is not None else None,
            "source": source,
        }

    @staticmethod
    def _yt_dlp_progress(progress: dict) -> dict:
        downloaded = int(progress.get("downloaded_bytes") or 0)
        total_value = progress.get("total_bytes") or progress.get("total_bytes_estimate")
        try:
            total = int(total_value) if total_value else None
        except (TypeError, ValueError):
            total = None
        percent = min(100.0, downloaded * 100.0 / total) if total else None
        return {
            "mode": "determinate" if total else "indeterminate",
            "percent": round(percent, 1) if percent is not None else None,
            "downloaded_bytes": downloaded,
            "total_bytes": total,
            "speed_bytes_per_sec": UrlDownloader._optional_float(progress.get("speed")),
            "eta_sec": UrlDownloader._optional_float(progress.get("eta")),
            "source": "yt_dlp",
        }

    def _safe_unlink_partial(self, path: Path) -> None:
        try:
            if path.resolve().parent == self.downloads_dir.resolve():
                path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not remove partial download: path=%s", path, exc_info=True)

    def _cleanup_prefix(self, prefix: str) -> None:
        try:
            root = self.downloads_dir.resolve()
            for path in self.downloads_dir.glob(f"{prefix}.*"):
                try:
                    if path.is_file() and path.resolve().parent == root:
                        path.unlink(missing_ok=True)
                except OSError:
                    quarantine_path = path.with_name(f"{path.name}.partial")
                    try:
                        if path.resolve().parent == root:
                            path.replace(quarantine_path)
                    except OSError:
                        logger.warning("Could not remove or quarantine partial yt-dlp file: path=%s", path, exc_info=True)
        except OSError:
            logger.warning("Could not inspect partial yt-dlp files: prefix=%s", prefix, exc_info=True)

    def _direct_media_filename(self, url: str, extension: str) -> str:
        parsed = urlparse(url)
        raw_name = unquote(Path(parsed.path).name or "")
        parsed_name = Path(raw_name)
        stem = parsed_name.stem.strip()
        suffix = parsed_name.suffix.lower()
        if not stem or suffix != extension:
            return f"url_media_{timestamp_for_filename()}{extension}"
        return f"{safe_filename_part(stem, max_length=96)}{extension}"

    def _reserve_download_path(self, filename: str) -> Path:
        target = self.downloads_dir / filename
        if not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        counter = 2
        while True:
            candidate = self.downloads_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _find_downloaded_audio(self, prefix: str, prepared_path: Path) -> Path | None:
        candidates = [
            prepared_path.with_suffix(".m4a"),
            prepared_path,
        ]
        candidates.extend(sorted(self.downloads_dir.glob(f"{prefix}.*")))
        return next((path for path in candidates if path.exists() and path.is_file()), None)

    def _find_downloaded_video(self, prefix: str, prepared_path: Path) -> Path | None:
        candidates = [
            prepared_path.with_suffix(".mkv"),
            prepared_path,
        ]
        candidates.extend(sorted(self.downloads_dir.glob(f"{prefix}.*")))
        return next((path for path in candidates if path.exists() and path.is_file()), None)

    @staticmethod
    def _validate_url(source_url: str) -> str:
        url = (source_url or "").strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RuntimeError("Укажите корректную публичную HTTP(S)-ссылку.")
        if parsed.username or parsed.password:
            raise RuntimeError("Ссылки со встроенной авторизацией не поддерживаются.")
        return url

    @staticmethod
    def _friendly_download_error(exc: Exception, *, prefix: str) -> UrlDownloadError:
        reason = _clean_error_text(exc)
        lowered = reason.lower()
        if isinstance(exc, (TimeoutError, socket.timeout)) or "timed out" in lowered or "timeout" in lowered:
            return UrlDownloadError(
                "Скачивание превысило таймаут. Проверьте соединение или попробуйте другой источник.",
                technical_details=reason,
            )
        if isinstance(exc, HTTPError) and exc.code in {401, 403}:
            return UrlDownloadError("Источник требует авторизацию или cookies.", technical_details=reason)
        if any(token in lowered for token in ("cookie", "cookies", "sign in", "login", "unauthorized", "forbidden", "private video")):
            return UrlDownloadError("Источник требует авторизацию или cookies.", technical_details=reason)
        if isinstance(exc, URLError) and exc.reason:
            reason = _clean_error_text(exc.reason)
        return UrlDownloadError(f"{prefix}: {reason}", technical_details=reason)

    @staticmethod
    def _platform(info: dict) -> str:
        extractor = str(info.get("extractor_key") or info.get("extractor") or "unknown").lower()
        if "youtube" in extractor:
            return "youtube"
        if "rutube" in extractor:
            return "rutube"
        if extractor == "vk" or "vkontakte" in extractor:
            return "vk"
        return extractor or "unknown"

    @staticmethod
    def _optional_text(value) -> str | None:
        text = str(value or "").strip()
        return text or None

    @staticmethod
    def _optional_float(value) -> float | None:
        try:
            return round(float(value), 3) if value is not None else None
        except (TypeError, ValueError):
            return None


def _clean_error_text(value) -> str:
    text = str(value or "").strip() or value.__class__.__name__
    repaired = _repair_common_mojibake(text)
    text = " ".join(repaired.replace("\r", " ").replace("\n", " ").split())
    if len(text) > 500:
        return f"{text[:497]}..."
    return text


def _repair_common_mojibake(text: str) -> str:
    if not any(marker in text for marker in ("Р", "СЃ", "С‹", "Рќ")):
        return text
    try:
        repaired = text.encode("cp1251").decode("utf-8")
    except UnicodeError:
        return text
    original_cyrillic = sum("А" <= char <= "я" or char in "Ёё" for char in text)
    repaired_cyrillic = sum("А" <= char <= "я" or char in "Ёё" for char in repaired)
    return repaired if repaired_cyrillic > original_cyrillic else text
