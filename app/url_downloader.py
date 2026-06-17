import logging
import socket
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from . import config
from .transcript_store import safe_filename_part
from .utils import timestamp_for_filename


logger = logging.getLogger(__name__)

DIRECT_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
DIRECT_AUDIO_EXTENSIONS = set(config.SUPPORTED_AUDIO_ONLY_EXTENSIONS)
DIRECT_MEDIA_EXTENSIONS = DIRECT_VIDEO_EXTENSIONS | DIRECT_AUDIO_EXTENSIONS
DIRECT_DOWNLOAD_TIMEOUT_SEC = 30
DIRECT_DOWNLOAD_CHUNK_BYTES = 1024 * 1024


class UrlDownloadError(RuntimeError):
    def __init__(self, message: str, *, technical_details: str | None = None) -> None:
        super().__init__(message)
        self.technical_details = technical_details or message


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

    def download(self, source_url: str) -> dict:
        url = self._validate_url(source_url)
        direct_extension = get_direct_media_url_extension(url)
        if direct_extension:
            return self._download_direct_media(url, direct_extension)

        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"url__{timestamp_for_filename()}__{uuid4().hex[:8]}"
        output_template = str(self.downloads_dir / f"{prefix}.%(ext)s")

        try:
            import yt_dlp
        except ImportError as exc:
            raise RuntimeError(
                "Не найден yt-dlp. Установите зависимости из requirements-cpu.txt и перезапустите run.bat."
            ) from exc

        options = {
            "format": "m4a/bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 15,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        }

        logger.info("Downloading URL audio: url=%s output=%s", url, output_template)
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                prepared_path = Path(downloader.prepare_filename(info))
        except Exception as exc:
            logger.exception("URL audio download failed: url=%s", url)
            raise self._friendly_download_error(exc, prefix="Не удалось скачать аудио по ссылке") from exc

        source_path = self._find_downloaded_audio(prefix, prepared_path)
        if source_path is None:
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
        return result.as_dict()

    def download_video(self, source_url: str) -> dict:
        url = self._validate_url(source_url)
        direct_extension = get_direct_media_url_extension(url)
        if direct_extension:
            return self._download_direct_media(url, direct_extension)

        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"url_video__{timestamp_for_filename()}__{uuid4().hex[:8]}"
        output_template = str(self.downloads_dir / f"{prefix}.%(ext)s")

        try:
            import yt_dlp
        except ImportError as exc:
            raise RuntimeError(
                "Не найден yt-dlp. Установите зависимости из requirements-cpu.txt и перезапустите run.bat."
            ) from exc

        options = {
            "format": "bv*+ba/bestvideo+bestaudio/best",
            "outtmpl": output_template,
            "merge_output_format": "mkv",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 15,
        }

        logger.info("Downloading URL video: url=%s output=%s", url, output_template)
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                prepared_path = Path(downloader.prepare_filename(info))
        except Exception as exc:
            logger.exception("URL video download failed: url=%s", url)
            raise self._friendly_download_error(exc, prefix="Не удалось скачать видео по ссылке") from exc

        source_path = self._find_downloaded_video(prefix, prepared_path)
        if source_path is None:
            raise RuntimeError("yt-dlp завершил работу, но видеофайл не найден.")

        result = DownloadedAudio(
            source_path=source_path,
            source_title=self._optional_text(info.get("title")),
            source_platform=self._platform(info),
            audio_duration_sec=self._optional_float(info.get("duration")),
        ).as_dict()
        result["downloaded_media_path"] = str(source_path)
        result["downloaded_video_path"] = str(source_path)
        logger.info(
            "URL video downloaded: url=%s file=%s platform=%s title=%s duration=%s",
            url,
            source_path,
            result["source_platform"],
            result["source_title"],
            result["audio_duration_sec"],
        )
        return result

    def _download_direct_media(self, url: str, extension: str) -> dict:
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        target_path = self._reserve_download_path(self._direct_media_filename(url, extension))
        request = Request(url, headers={"User-Agent": "LocalMediaTranscriber/1.0"})

        logger.info("Downloading direct media URL: url=%s output=%s", url, target_path)
        try:
            with urlopen(request, timeout=DIRECT_DOWNLOAD_TIMEOUT_SEC) as response:
                status = getattr(response, "status", None)
                if status is None and hasattr(response, "getcode"):
                    status = response.getcode()
                if status and int(status) >= 400:
                    raise HTTPError(url, int(status), f"HTTP {status}", getattr(response, "headers", None), None)

                with target_path.open("xb") as file:
                    while True:
                        chunk = response.read(DIRECT_DOWNLOAD_CHUNK_BYTES)
                        if not chunk:
                            break
                        file.write(chunk)
        except Exception as exc:
            target_path.unlink(missing_ok=True)
            logger.exception("Direct media download failed: url=%s", url)
            raise self._friendly_download_error(exc, prefix="Не удалось скачать медиафайл") from exc

        if not target_path.exists() or target_path.stat().st_size <= 0:
            target_path.unlink(missing_ok=True)
            raise UrlDownloadError(
                "Не удалось скачать медиафайл: скачанный файл пустой.",
                technical_details="Downloaded direct media file is empty.",
            )

        result = DownloadedAudio(
            source_path=target_path,
            source_title=target_path.name,
            source_platform="direct",
            audio_duration_sec=None,
        ).as_dict()
        result["downloaded_media_path"] = str(target_path)
        if extension in DIRECT_VIDEO_EXTENSIONS:
            result["downloaded_video_path"] = str(target_path)
        logger.info("Direct media downloaded: url=%s file=%s size=%s", url, target_path, target_path.stat().st_size)
        return result

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
