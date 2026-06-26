from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config
from .utils import write_json_file_atomic


URL_DOWNLOAD_PROFILE_IDS = (
    "auto",
    "best_for_extraction",
    "best_quality",
    "smallest_file",
    "prefer_webm",
    "prefer_mp4",
    "prefer_mkv",
    "prefer_mov",
    "prefer_avi",
    "audio_friendly",
    "custom",
)
URL_DOWNLOAD_MAX_VIDEO_HEIGHTS = ("auto", "480", "720", "1080", "1440", "2160")
DEFAULT_URL_DOWNLOAD_SETTINGS = {
    "format_profile": "auto",
    "custom_format": "",
    "max_video_height": "auto",
    "log_media_probe": True,
    "log_extraction_benchmark": True,
}


def normalize_url_download_settings(value: Any) -> dict:
    source = value if isinstance(value, dict) else {}
    profile = str(source.get("format_profile") or "auto").strip().lower()
    if profile not in URL_DOWNLOAD_PROFILE_IDS:
        profile = "auto"
    custom_format = str(source.get("custom_format") or "").strip()[:1000]
    if profile == "custom" and not custom_format:
        profile = "auto"
    max_video_height = str(source.get("max_video_height") or "auto").strip().lower()
    if max_video_height not in URL_DOWNLOAD_MAX_VIDEO_HEIGHTS:
        max_video_height = "auto"
    return {
        "format_profile": profile,
        "custom_format": custom_format,
        "max_video_height": max_video_height,
        "log_media_probe": bool(source.get("log_media_probe", True)),
        "log_extraction_benchmark": bool(source.get("log_extraction_benchmark", True)),
    }


def normalize_url_download_plan(value: Any) -> dict:
    return {**normalize_url_download_settings(value), "status": "pending"}


class UrlDownloadSettingsManager:
    def __init__(self, *, settings_path: Path | None = None) -> None:
        self.settings_path = settings_path or (config.DATA_DIR / "settings.json")

    def settings(self) -> dict:
        raw = self._read_settings_file()
        return normalize_url_download_settings(raw.get("url_download"))

    def update_settings(self, changes: dict[str, Any]) -> dict:
        settings = self.settings()
        for key in DEFAULT_URL_DOWNLOAD_SETTINGS:
            if key in changes:
                settings[key] = changes[key]
        settings = normalize_url_download_settings(settings)
        raw = self._read_settings_file()
        raw["url_download"] = settings
        write_json_file_atomic(self.settings_path, raw)
        return settings

    def _read_settings_file(self) -> dict:
        try:
            if self.settings_path.exists():
                payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    return payload
        except (OSError, ValueError):
            pass
        return {}
