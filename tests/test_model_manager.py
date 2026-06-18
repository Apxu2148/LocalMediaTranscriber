import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app import config
from app import utils as utils_module
from app.model_manager import DownloadState, WhisperModelManager


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"
config.JOBS_DIR = PROJECT_TMP

with patch.object(utils_module, "setup_logging"):
    from app import main as main_module  # noqa: E402


class ModelManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"model_manager_{uuid4().hex}"
        self.root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def temp_root(self, name: str) -> Path:
        root = self.root / name
        root.mkdir(parents=True, exist_ok=True)
        return root

    def make_manager(self, root: Path) -> WhisperModelManager:
        return WhisperModelManager(models_dir=root, supported_models=("tiny", "small"))

    def write_complete_snapshot(self, manager: WhisperModelManager, model: str = "small") -> Path:
        snapshot = manager.model_cache_dir(model) / "snapshots" / "test-snapshot"
        snapshot.mkdir(parents=True)
        (snapshot / "model.bin").write_bytes(b"model")
        (snapshot / "config.json").write_text("{}", encoding="utf-8")
        return snapshot

    def test_supported_model_list_returns_expected_shape(self) -> None:
        manager = self.make_manager(self.temp_root("supported"))
        snapshot = self.write_complete_snapshot(manager)

        models = manager.list_models()
        small = next(item for item in models if item["name"] == "small")

        self.assertTrue(small["is_downloaded"])
        self.assertEqual("available", small["status"])
        self.assertEqual(str(snapshot), small["local_path"])
        self.assertTrue(small["can_delete"])
        self.assertIn("size_label", small)
        self.assertIn("repo_id", small)

    def test_invalid_model_is_rejected_and_info_exists(self) -> None:
        manager = self.make_manager(self.temp_root("invalid"))
        with self.assertRaises(ValueError):
            manager.model_status("medium")

        info = manager.model_info("tiny")
        self.assertEqual("tiny", info["name"])
        self.assertIn("parameter_count_label", info)

    def test_delete_removes_only_selected_model_cache(self) -> None:
        manager = self.make_manager(self.temp_root("delete"))
        selected_snapshot = self.write_complete_snapshot(manager, "small")
        other_snapshot = self.write_complete_snapshot(manager, "tiny")

        result = manager.delete_model("small", confirm=True)

        self.assertTrue(result["deleted"])
        self.assertFalse(selected_snapshot.exists())
        self.assertTrue(other_snapshot.exists())

    def test_delete_refuses_invalid_and_unsafe_paths(self) -> None:
        manager = self.make_manager(self.temp_root("unsafe"))

        with self.assertRaises(ValueError):
            manager.delete_model("medium", confirm=True)
        with self.assertRaises(ValueError):
            manager.delete_model("small", confirm=False)

        self.assertFalse(manager._is_safe_model_cache_path(manager.cache_dir, "small"))

    def test_download_status_endpoint_shape(self) -> None:
        with TestClient(main_module.app) as client:
            response = client.get("/api/models/download-status")
            self.assertEqual(200, response.status_code)
            payload = response.json()
            self.assertIn("active", payload)
            self.assertIn("progress_percent", payload)
            self.assertIn("status", payload)

    def test_retry_download_clears_failed_state_before_worker_runs(self) -> None:
        class FakeThread:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def start(self) -> None:
                pass

        manager = self.make_manager(self.temp_root("download"))
        manager._download_state = DownloadState(
            active=False,
            model="small",
            status="download_error",
            message="old error",
            error_message="old technical error",
        )

        with patch("app.model_manager.threading.Thread", FakeThread):
            status = manager.start_download("small")

        self.assertTrue(status["accepted"])
        self.assertTrue(status["active"])
        self.assertEqual("starting", status["status"])
        self.assertIsNone(status["error_message"])
        self.assertNotIn("old", status["message"])

    def test_successful_download_clears_progress_after_ready_state(self) -> None:
        manager = self.make_manager(self.temp_root("download_success"))

        def fake_download_model(_model_name: str, cache_dir: str) -> Path:
            self.assertEqual(str(manager.cache_dir), cache_dir)
            return self.write_complete_snapshot(manager, "small")

        manager._download_state = DownloadState(
            active=True,
            model="small",
            status="downloading",
            progress_percent=0,
            progress_available=True,
        )

        with patch("app.model_manager.download_model", side_effect=fake_download_model):
            manager._download_worker("small")

        status = manager.download_status()
        self.assertFalse(status["active"])
        self.assertEqual("available", status["status"])
        self.assertIsNone(status["progress_percent"])
        self.assertFalse(status["progress_available"])
        self.assertEqual("available", manager.model_status("small")["status"])

    def test_ready_state_does_not_conflict_with_active_download(self) -> None:
        manager = self.make_manager(self.temp_root("ready"))
        snapshot = self.write_complete_snapshot(manager)
        manager._download_state = DownloadState(
            active=True,
            model="small",
            status="downloading",
            progress_percent=0,
            progress_available=True,
        )

        status = manager.mark_model_ready("small", local_path=snapshot)

        self.assertFalse(status["active"])
        self.assertEqual("available", status["status"])
        self.assertIsNone(status["progress_percent"])
        self.assertFalse(status["progress_available"])
        self.assertEqual("available", manager.model_status("small")["status"])

    def test_failed_verification_sets_failed_state_without_progress(self) -> None:
        manager = self.make_manager(self.temp_root("verify_failed"))
        self.write_complete_snapshot(manager)

        status = manager.mark_model_verification_failed("small", error_message="CUDA failed")
        model_status = manager.model_status("small")

        self.assertFalse(status["active"])
        self.assertEqual("verification_error", status["status"])
        self.assertIsNone(status["progress_percent"])
        self.assertFalse(status["progress_available"])
        self.assertEqual("verification_error", model_status["status"])
        self.assertTrue(model_status["is_downloaded"])

    def test_verify_endpoint_uses_mocked_transcriber_without_downloading(self) -> None:
        with (
            patch.object(main_module.model_manager, "model_status", return_value={"is_downloaded": True, "local_path": "C:\\model"}),
            patch.object(
                main_module.transcriber,
                "verify_model",
                return_value={
                    "success": True,
                    "model": "small",
                    "requested_device": "cpu",
                    "resolved_device": "cpu",
                    "compute_type": "int8",
                },
            ) as verify_model,
            patch.object(main_module.model_manager, "mark_model_ready") as mark_model_ready,
            TestClient(main_module.app) as client,
        ):
            response = client.post("/api/models/verify", json={"model": "small", "device": "cpu"})

            self.assertEqual(200, response.status_code)
            self.assertTrue(response.json()["success"])
            verify_model.assert_called_once_with("small", "cpu")
            mark_model_ready.assert_called_once()
            self.assertEqual("small", mark_model_ready.call_args.args[0])
            self.assertEqual("C:\\model", mark_model_ready.call_args.kwargs["local_path"])

    def test_verify_endpoint_records_failed_verification(self) -> None:
        with (
            patch.object(main_module.model_manager, "model_status", return_value={"is_downloaded": True, "local_path": "C:\\model"}),
            patch.object(main_module.transcriber, "verify_model", side_effect=RuntimeError("CUDA failed")),
            patch.object(main_module.model_manager, "mark_model_verification_failed") as mark_model_verification_failed,
            TestClient(main_module.app) as client,
        ):
            response = client.post("/api/models/verify", json={"model": "small", "device": "cpu"})

            self.assertEqual(200, response.status_code)
            payload = response.json()
            self.assertFalse(payload["success"])
            self.assertEqual("verification_error", payload["status"])
            mark_model_verification_failed.assert_called_once_with("small", error_message="CUDA failed")

    def test_invalid_model_endpoint_is_rejected(self) -> None:
        with TestClient(main_module.app) as client:
            response = client.post("/api/models/download", json={"model": "unknown"})
            self.assertEqual(400, response.status_code)


if __name__ == "__main__":
    unittest.main()
