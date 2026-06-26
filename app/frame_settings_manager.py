from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config
from .frame_extractor import DEFAULT_MAX_FRAME_SIZE, normalize_max_frame_size
from .utils import write_json_file_atomic


DEFAULT_FRAME_SETTINGS = {
    "max_frame_size": DEFAULT_MAX_FRAME_SIZE,
}


def normalize_frame_settings(value: Any) -> dict:
    source = value if isinstance(value, dict) else {}
    return {
        "max_frame_size": normalize_max_frame_size(source.get("max_frame_size")),
    }


class FrameSettingsManager:
    def __init__(self, *, settings_path: Path | None = None) -> None:
        self.settings_path = settings_path or (config.DATA_DIR / "settings.json")

    def settings(self) -> dict:
        raw = self._read_settings_file()
        return normalize_frame_settings(raw.get("frames"))

    def update_settings(self, changes: dict[str, Any]) -> dict:
        settings = self.settings()
        for key in DEFAULT_FRAME_SETTINGS:
            if key in changes:
                settings[key] = changes[key]
        settings = normalize_frame_settings(settings)
        raw = self._read_settings_file()
        raw["frames"] = settings
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
