from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from . import config
from .utils import write_json_file_atomic


DEFAULT_STORAGE_SETTINGS = {
    "keep_downloaded_url_media": True,
    "keep_uploaded_temp_files": True,
}


class StorageManager:
    def __init__(
        self,
        *,
        data_dir: Path | None = None,
        settings_path: Path | None = None,
    ) -> None:
        self.data_dir = (data_dir or config.DATA_DIR).resolve()
        self.settings_path = settings_path or (self.data_dir / "settings.json")
        self.folder_paths = {
            "downloads": self.data_dir / "downloads",
            "uploads": self.data_dir / "uploads",
            "recordings": self.data_dir / "recordings",
            "transcripts": self.data_dir / "transcripts",
            "logs": self.data_dir / "logs",
            "jobs": self.data_dir / "jobs",
        }
        self.cleanup_allowed = {"downloads", "uploads"}

    def summary(self) -> dict:
        folders = [self._folder_summary(key, path) for key, path in self.folder_paths.items()]
        return {
            "data_path": str(self.data_dir),
            "total_size_bytes": self._path_size(self.data_dir) if self.data_dir.exists() else 0,
            "folders": folders,
        }

    def settings(self) -> dict:
        payload = dict(DEFAULT_STORAGE_SETTINGS)
        try:
            if self.settings_path.exists():
                import json

                stored = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(stored, dict):
                    for key in payload:
                        if key in stored:
                            payload[key] = bool(stored[key])
        except Exception:
            return dict(DEFAULT_STORAGE_SETTINGS)
        return payload

    def update_settings(self, changes: dict[str, Any]) -> dict:
        settings = self.settings()
        for key in DEFAULT_STORAGE_SETTINGS:
            if key in changes:
                settings[key] = bool(changes[key])
        write_json_file_atomic(self.settings_path, settings)
        return settings

    def cleanup_folder(self, key: str) -> dict:
        folder_key = key.strip().lower()
        if folder_key not in self.cleanup_allowed:
            raise RuntimeError("Очистка хранилища доступна только для downloads и uploads.")
        folder = self._safe_known_folder(folder_key)
        errors: list[str] = []
        deleted_entries = 0
        deleted_bytes = 0

        if not folder.exists():
            return {
                "folder": folder_key,
                "path": str(folder),
                "deleted_entries": 0,
                "deleted_bytes": 0,
                "errors": [],
            }

        for child in list(folder.iterdir()):
            try:
                deleted_bytes += self._path_size(child)
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
                deleted_entries += 1
            except Exception as exc:
                errors.append(f"{child}: {exc}")

        return {
            "folder": folder_key,
            "path": str(folder),
            "deleted_entries": deleted_entries,
            "deleted_bytes": deleted_bytes,
            "errors": errors,
        }

    def apply_retention_cleanup(self, item: dict) -> dict:
        settings = self.settings()
        result: dict[str, Any] = {}
        if not settings.get("keep_downloaded_url_media", True):
            path = (
                item.get("downloaded_video_path")
                or item.get("downloaded_media_path")
                or item.get("downloaded_audio_path")
            )
            result.update(self._delete_intermediate_file(path, "downloads", "downloaded_media"))

        if not settings.get("keep_uploaded_temp_files", True):
            path = item.get("source_path") if item.get("source_type") == "local_file" else None
            result.update(self._delete_intermediate_file(path, "uploads", "uploaded_temp"))

        return result

    def _folder_summary(self, key: str, path: Path) -> dict:
        exists = path.exists()
        return {
            "key": key,
            "path": str(path),
            "exists": exists,
            "size_bytes": self._path_size(path) if exists else 0,
        }

    def _path_size(self, path: Path) -> int:
        try:
            if not path.exists():
                return 0
            if path.is_file():
                return path.stat().st_size
            total = 0
            for child in path.rglob("*"):
                try:
                    if child.is_file():
                        total += child.stat().st_size
                except OSError:
                    continue
            return total
        except OSError:
            return 0

    def _safe_known_folder(self, key: str) -> Path:
        folder = self.folder_paths[key].resolve()
        if not folder.is_relative_to(self.data_dir):
            raise RuntimeError("Настроенная папка хранилища находится вне project data.")
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _delete_intermediate_file(self, path_value: str | None, folder_key: str, prefix: str) -> dict:
        payload = {
            f"{prefix}_deleted": False,
            f"{prefix}_delete_error": None,
        }
        if not path_value:
            return payload

        folder = self._safe_known_folder(folder_key)
        try:
            path = Path(path_value).resolve()
            if not path.is_relative_to(self.data_dir) or not path.is_relative_to(folder):
                payload[f"{prefix}_delete_error"] = "Путь находится вне разрешенной папки project data."
                return payload
            if path.exists() and path.is_file():
                path.unlink()
                payload[f"{prefix}_deleted"] = True
        except Exception as exc:
            payload[f"{prefix}_delete_error"] = str(exc)
        return payload
