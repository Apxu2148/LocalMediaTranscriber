from __future__ import annotations

import importlib
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from . import config
from .utils import write_json_file_atomic


OCR_BACKEND_IDS = ("tesseract", "easyocr", "paddleocr", "windows_ocr")
DEFAULT_OCR_SETTINGS = {
    "selected_backend": "tesseract",
    "tesseract_path": None,
    "default_languages": ["rus", "eng"],
}
COMMON_WINDOWS_TESSERACT_PATHS = (
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe",
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Tesseract-OCR" / "tesseract.exe",
)
_USE_SAVED_PATH = object()


class OcrManager:
    def __init__(self, *, settings_path: Path | None = None, timeout_sec: float = 5.0) -> None:
        self.settings_path = settings_path or (config.DATA_DIR / "settings.json")
        self.timeout_sec = timeout_sec

    def settings(self) -> dict:
        raw = self._read_settings_file()
        stored = raw.get("ocr") if isinstance(raw.get("ocr"), dict) else {}
        path_value = stored.get("tesseract_path")
        configured_path = str(path_value).strip() if path_value else None
        selected_backend = str(stored.get("selected_backend") or "").strip()
        if selected_backend not in OCR_BACKEND_IDS:
            selected_backend = DEFAULT_OCR_SETTINGS["selected_backend"]
        languages = self._normalize_default_languages(stored.get("default_languages"))
        return {
            "selected_backend": selected_backend,
            "tesseract_path": configured_path,
            "default_languages": languages,
        }

    def update_settings(self, changes: dict[str, Any]) -> dict:
        settings = self.settings()
        if "selected_backend" in changes:
            selected_backend = str(changes.get("selected_backend") or "").strip()
            if selected_backend not in OCR_BACKEND_IDS:
                raise ValueError("invalid_ocr_backend")
            settings["selected_backend"] = selected_backend
        if "tesseract_path" in changes:
            value = changes.get("tesseract_path")
            settings["tesseract_path"] = str(value).strip() if value and str(value).strip() else None
        if "default_languages" in changes:
            settings["default_languages"] = self._normalize_default_languages(changes.get("default_languages"))

        raw = self._read_settings_file()
        raw["ocr"] = settings
        write_json_file_atomic(self.settings_path, raw)
        return settings

    def status(
        self,
        configured_path: str | None | object = _USE_SAVED_PATH,
        *,
        backend: str | None = None,
    ) -> dict:
        if backend is not None and backend not in OCR_BACKEND_IDS:
            raise ValueError("invalid_ocr_backend")
        settings = self.settings()
        backends = {
            "tesseract": self.tesseract_status(configured_path),
            "easyocr": self.easyocr_status(),
            "paddleocr": self.paddleocr_status(),
            "windows_ocr": self.windows_ocr_status(),
        }
        selected_backend = settings["selected_backend"]
        return {
            "selected_backend": settings["selected_backend"],
            "backends": backends,
            "processing_enabled": selected_backend == "easyocr" and bool(backends["easyocr"].get("available")),
        }

    def tesseract_status(self, configured_path: str | None | object = _USE_SAVED_PATH) -> dict:
        settings = self.settings()
        if configured_path is _USE_SAVED_PATH:
            selected_path = settings["tesseract_path"]
        else:
            selected_path = str(configured_path).strip() if configured_path and str(configured_path).strip() else None

        if selected_path:
            candidate = Path(selected_path).expanduser()
            if not self._is_candidate_file(candidate):
                return self._unavailable_tesseract_status(
                    selected_path,
                    "invalid_configured_path",
                    configured_path=selected_path,
                )
            return self._check_tesseract_candidate(candidate, configured_path=selected_path)

        candidates: list[Path] = []
        path_candidate = shutil.which("tesseract")
        if path_candidate:
            candidates.append(Path(path_candidate))
        candidates.extend(COMMON_WINDOWS_TESSERACT_PATHS)

        seen: set[str] = set()
        first_error: dict | None = None
        for candidate in candidates:
            candidate_key = str(candidate).casefold()
            if candidate_key in seen:
                continue
            seen.add(candidate_key)
            if not self._is_candidate_file(candidate):
                continue
            result = self._check_tesseract_candidate(candidate, configured_path=None)
            if result["available"]:
                return result
            first_error = first_error or result

        return first_error or self._unavailable_tesseract_status(None, "not_found", configured_path=None)

    def easyocr_status(self) -> dict:
        return self._python_backend_status(
            backend_id="easyocr",
            name="EasyOCR",
            module_name="easyocr",
            backend_type="python_optional",
            languages=["ru", "en"],
            notes=[],
        )

    def paddleocr_status(self) -> dict:
        return self._python_backend_status(
            backend_id="paddleocr",
            name="PaddleOCR",
            module_name="paddleocr",
            backend_type="python_optional_experimental",
            languages=[],
            notes=["experimental"],
        )

    def windows_ocr_status(self) -> dict:
        base = {
            "id": "windows_ocr",
            "name": "Windows OCR",
            "type": "windows_system_experimental",
            "available": False,
            "status": "unsupported_platform",
            "version": None,
            "languages": [],
            "notes": ["windows_only", "experimental"],
        }
        if platform.system() != "Windows":
            return base
        try:
            module = importlib.import_module("winrt.windows.media.ocr")
        except (ImportError, ModuleNotFoundError):
            return {
                **base,
                "status": "not_installed",
                "notes": [*base["notes"], "optional_dependency_missing"],
            }
        except Exception:
            return {**base, "status": "check_failed", "notes": [*base["notes"], "import_check_failed"]}
        return {
            **base,
            "available": True,
            "status": "available",
            "version": self._module_version(module),
        }

    def _python_backend_status(
        self,
        *,
        backend_id: str,
        name: str,
        module_name: str,
        backend_type: str,
        languages: list[str],
        notes: list[str],
    ) -> dict:
        base = {
            "id": backend_id,
            "name": name,
            "type": backend_type,
            "available": False,
            "status": "not_installed",
            "version": None,
            "languages": list(languages),
            "notes": list(notes),
        }
        try:
            module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError):
            return {**base, "notes": [*notes, "optional_dependency_missing"]}
        except Exception:
            return {**base, "status": "check_failed", "notes": [*notes, "import_check_failed"]}
        return {
            **base,
            "available": True,
            "status": "available",
            "version": self._module_version(module),
        }

    def _check_tesseract_candidate(self, path: Path, *, configured_path: str | None) -> dict:
        base = self._unavailable_tesseract_status(str(path), None, configured_path=configured_path)
        try:
            version_result = self._run(path, "--version")
        except subprocess.TimeoutExpired:
            return {**base, "error": "version_timeout"}
        except (OSError, subprocess.SubprocessError):
            return {**base, "error": "version_check_failed"}

        version = self._parse_version(version_result.stdout or version_result.stderr)
        base["version"] = version
        if version_result.returncode != 0:
            return {**base, "error": "version_check_failed"}

        try:
            language_result = self._run(path, "--list-langs")
        except subprocess.TimeoutExpired:
            return {**base, "error": "languages_timeout"}
        except (OSError, subprocess.SubprocessError):
            return {**base, "error": "languages_check_failed"}
        if language_result.returncode != 0:
            return {**base, "error": "languages_check_failed"}

        languages = self._parse_languages(language_result.stdout)
        return {
            **base,
            "available": True,
            "status": "available",
            "languages": languages,
            "has_eng": "eng" in languages,
            "has_rus": "rus" in languages,
            "notes": [],
            "error": None,
        }

    def _run(self, path: Path, argument: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(path), argument],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=self.timeout_sec,
            check=False,
        )

    @staticmethod
    def _looks_like_tesseract(path: Path) -> bool:
        return path.name.casefold() in {"tesseract", "tesseract.exe"}

    @classmethod
    def _is_candidate_file(cls, path: Path) -> bool:
        try:
            return cls._looks_like_tesseract(path) and path.exists() and path.is_file()
        except OSError:
            return False

    @staticmethod
    def _parse_version(output: str | None) -> str | None:
        first_line = next((line.strip() for line in (output or "").splitlines() if line.strip()), "")
        match = re.search(r"\btesseract\s+([^\s]+)", first_line, flags=re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def _parse_languages(output: str | None) -> list[str]:
        languages: list[str] = []
        for line in (output or "").splitlines():
            value = line.strip()
            if not value or value.casefold().startswith("list of available languages"):
                continue
            if value not in languages:
                languages.append(value)
        return languages

    @staticmethod
    def _module_version(module: Any) -> str | None:
        value = getattr(module, "__version__", None)
        return str(value) if value is not None else None

    @staticmethod
    def _normalize_default_languages(value: Any) -> list[str]:
        if not isinstance(value, list):
            return list(DEFAULT_OCR_SETTINGS["default_languages"])
        languages: list[str] = []
        for item in value:
            language = str(item).strip()
            if language and re.fullmatch(r"[A-Za-z0-9_]+", language) and language not in languages:
                languages.append(language)
        return languages or list(DEFAULT_OCR_SETTINGS["default_languages"])

    def _read_settings_file(self) -> dict:
        try:
            if self.settings_path.exists():
                payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    return payload
        except (OSError, ValueError):
            pass
        return {}

    @staticmethod
    def _unavailable_tesseract_status(path: str | None, error: str | None, *, configured_path: str | None) -> dict:
        status = "not_found" if error == "not_found" else "check_failed"
        notes = ["external_path_required"] if error in {"not_found", "invalid_configured_path"} else []
        return {
            "id": "tesseract",
            "name": "Tesseract OCR",
            "type": "external_executable",
            "available": False,
            "status": status,
            "path": path,
            "version": None,
            "languages": [],
            "has_eng": False,
            "has_rus": False,
            "configured_path": configured_path,
            "notes": notes,
            "error": error,
        }
