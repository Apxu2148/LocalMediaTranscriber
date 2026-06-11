import logging
import shutil
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from faster_whisper.utils import download_model

from . import config


logger = logging.getLogger(__name__)

MODEL_REQUIRED_FILES = ("model.bin", "config.json")
MODEL_ALLOW_PATTERNS = (
    "config.json",
    "preprocessor_config.json",
    "model.bin",
    "tokenizer.json",
    "vocabulary.*",
)

MODEL_INFO = {
    "tiny": {
        "repo_id": "Systran/faster-whisper-tiny",
        "size_label": "~75 MB",
        "parameter_count_label": "~39M",
        "info_key": "tiny",
    },
    "base": {
        "repo_id": "Systran/faster-whisper-base",
        "size_label": "~140 MB",
        "parameter_count_label": "~74M",
        "info_key": "base",
    },
    "small": {
        "repo_id": "Systran/faster-whisper-small",
        "size_label": "~460 MB",
        "parameter_count_label": "~244M",
        "info_key": "small",
    },
    "medium": {
        "repo_id": "Systran/faster-whisper-medium",
        "size_label": "~1.5 GB",
        "parameter_count_label": "~769M",
        "info_key": "medium",
    },
    "large-v3": {
        "repo_id": "Systran/faster-whisper-large-v3",
        "size_label": "~3.1 GB",
        "parameter_count_label": "~1.55B",
        "info_key": "largeV3",
    },
}


@dataclass
class DownloadState:
    active: bool = False
    model: str | None = None
    status: str = "idle"
    progress_percent: int | None = None
    progress_available: bool = False
    message: str = "No model download is running."
    error_message: str | None = None
    local_path: str | None = None
    started_at: str | None = None
    finished_at: str | None = None

    def as_dict(self) -> dict:
        return {
            "active": self.active,
            "model": self.model,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "progress_available": self.progress_available,
            "message": self.message,
            "error_message": self.error_message,
            "local_path": self.local_path,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@dataclass
class WhisperModelManager:
    models_dir: Path = config.MODELS_DIR
    supported_models: tuple[str, ...] = config.SUPPORTED_WHISPER_MODELS
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _download_state: DownloadState = field(default_factory=DownloadState, init=False)
    _download_thread: threading.Thread | None = field(default=None, init=False, repr=False)

    @property
    def cache_dir(self) -> Path:
        return self.models_dir / "faster-whisper"

    @property
    def lock_dir(self) -> Path:
        return self.cache_dir / ".locks"

    def validate_model(self, model_name: str | None) -> str:
        selected_model = (model_name or "").strip()
        if selected_model not in self.supported_models:
            allowed = ", ".join(self.supported_models)
            raise ValueError(f"Unsupported Whisper model '{selected_model}'. Available: {allowed}.")
        return selected_model

    def list_models(self) -> list[dict]:
        return [self.model_status(model_name) for model_name in self.supported_models]

    def model_status(self, model_name: str) -> dict:
        selected_model = self.validate_model(model_name)
        repo_dir = self.model_cache_dir(selected_model)
        complete_snapshots = self.complete_snapshots(selected_model)
        local = bool(complete_snapshots)
        local_path = complete_snapshots[-1] if local else None
        info = self.model_info(selected_model)
        status = "available" if local else "not_downloaded"

        download_state = self.download_status()
        if download_state["model"] == selected_model:
            if download_state["active"]:
                status = download_state["status"]
            elif download_state["status"] == "download_error" and not local:
                status = "download_error"

        return {
            "name": selected_model,
            "status": status,
            "local": local,
            "is_downloaded": local,
            "path": str(local_path or repo_dir),
            "local_path": str(local_path) if local_path else None,
            "can_delete": self.can_delete_model(selected_model),
            "size_label": info["size_label"],
            "parameter_count_label": info["parameter_count_label"],
            "repo_id": info["repo_id"],
            "info_key": info["info_key"],
            "description": info["info_key"],
        }

    def model_info(self, model_name: str) -> dict:
        selected_model = self.validate_model(model_name)
        info = MODEL_INFO[selected_model]
        return {
            "name": selected_model,
            "origin": "OpenAI Whisper; faster-whisper/CTranslate2-compatible Systran conversion.",
            **info,
        }

    def all_model_info(self) -> list[dict]:
        return [self.model_info(model_name) for model_name in self.supported_models]

    def start_download(self, model_name: str) -> dict:
        selected_model = self.validate_model(model_name)
        with self._lock:
            if self._download_state.active:
                current = self._download_state.as_dict()
                current["accepted"] = False
                return current

            now = self._timestamp()
            self._download_state = DownloadState(
                active=True,
                model=selected_model,
                status="starting",
                progress_percent=None,
                progress_available=False,
                message=f"Starting download for model {selected_model}...",
                started_at=now,
            )
            self._download_thread = threading.Thread(
                target=self._download_worker,
                args=(selected_model,),
                name=f"whisper-model-download-{selected_model}",
                daemon=True,
            )
            self._download_thread.start()
            status = self._download_state.as_dict()
            status["accepted"] = True
            return status

    def download_status(self) -> dict:
        with self._lock:
            return self._download_state.as_dict()

    def delete_model(self, model_name: str, *, confirm: bool) -> dict:
        selected_model = self.validate_model(model_name)
        if not confirm:
            raise ValueError("Delete confirmation is required.")

        with self._lock:
            if self._download_state.active and self._download_state.model == selected_model:
                raise RuntimeError("Wait for the current model download to finish before deleting it.")

        paths = self.deletable_paths(selected_model)
        existing_paths = [path for path in paths if path.exists()]
        if not existing_paths:
            return {
                "deleted": False,
                "model": selected_model,
                "status": "not_downloaded",
                "message": "No local files were found for this model.",
            }

        for path in existing_paths:
            logger.info("Deleting Whisper model cache path: model=%s path=%s", selected_model, path)
            self._remove_tree_with_retries(path)

        return {
            "deleted": True,
            "model": selected_model,
            "status": "not_downloaded",
            "message": "Local model files were deleted.",
        }

    def can_delete_model(self, model_name: str) -> bool:
        return any(path.exists() for path in self.deletable_paths(model_name))

    @staticmethod
    def _remove_tree_with_retries(path: Path) -> None:
        for attempt in range(10):
            try:
                shutil.rmtree(path)
                return
            except FileNotFoundError:
                return
            except PermissionError:
                if attempt == 9:
                    raise
                time.sleep(0.1)

    def deletable_paths(self, model_name: str) -> list[Path]:
        selected_model = self.validate_model(model_name)
        paths = [
            self.model_cache_dir(selected_model),
            self.lock_dir / self.repo_cache_name(selected_model),
        ]
        return [path for path in paths if self._is_safe_model_cache_path(path, selected_model)]

    def model_cache_dir(self, model_name: str) -> Path:
        return self.cache_dir / self.repo_cache_name(model_name)

    def repo_cache_name(self, model_name: str) -> str:
        info = self.model_info(model_name)
        return f"models--{info['repo_id'].replace('/', '--')}"

    def complete_snapshots(self, model_name: str) -> list[Path]:
        selected_model = self.validate_model(model_name)
        snapshots_dir = self.model_cache_dir(selected_model) / "snapshots"
        if not snapshots_dir.exists():
            return []
        snapshot_paths = sorted(path for path in snapshots_dir.iterdir() if path.is_dir())
        return [
            path
            for path in snapshot_paths
            if all((path / filename).exists() for filename in MODEL_REQUIRED_FILES)
        ]

    def _download_worker(self, model_name: str) -> None:
        try:
            logger.info("Whisper model download started: model=%s", model_name)
            with self._lock:
                self._download_state.status = "downloading"
                self._download_state.message = f"Downloading model {model_name}..."
                self._download_state.error_message = None
                self._download_state.progress_percent = None
                self._download_state.progress_available = False
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            local_path = download_model(
                model_name,
                cache_dir=str(self.cache_dir),
            )
            status = self.model_status(model_name)
            if not status["is_downloaded"]:
                raise RuntimeError("The model download finished, but required model files were not found.")
            with self._lock:
                self._download_state = DownloadState(
                    active=False,
                    model=model_name,
                    status="available",
                    progress_percent=100,
                    progress_available=True,
                    message=f"Model {model_name} is available locally.",
                    local_path=str(local_path),
                    started_at=self._download_state.started_at,
                    finished_at=self._timestamp(),
                )
            logger.info("Whisper model download completed: model=%s path=%s", model_name, local_path)
        except Exception as exc:
            logger.exception("Whisper model download failed: model=%s", model_name)
            with self._lock:
                self._download_state = DownloadState(
                    active=False,
                    model=model_name,
                    status="download_error",
                    progress_percent=None,
                    progress_available=False,
                    message="Failed to download the model. Check the internet connection and try again.",
                    error_message=str(exc),
                    started_at=self._download_state.started_at,
                    finished_at=self._timestamp(),
                )

    def _is_safe_model_cache_path(self, path: Path, model_name: str) -> bool:
        expected_name = self.repo_cache_name(model_name)
        try:
            resolved = path.resolve()
            cache_root = self.cache_dir.resolve()
            lock_root = self.lock_dir.resolve()
        except OSError:
            return False

        if resolved.name != expected_name:
            return False
        return resolved.parent == cache_root or resolved.parent == lock_root

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
