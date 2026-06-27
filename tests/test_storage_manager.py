import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from app.storage_manager import StorageManager


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class StorageManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"codex_storage_manager_{uuid4().hex}"
        self.data_dir = self.root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def make_manager(self) -> StorageManager:
        return StorageManager(data_dir=self.data_dir)

    def test_summary_reports_known_folders_missing_folders_and_total_size(self) -> None:
        (self.data_dir / "downloads").mkdir()
        (self.data_dir / "downloads" / "media.mp4").write_bytes(b"abcd")
        (self.data_dir / "recordings" / "clip__frames").mkdir(parents=True)
        (self.data_dir / "recordings" / "clip__frames" / "frame.jpg").write_bytes(b"123")

        summary = self.make_manager().summary()
        folders = {folder["key"]: folder for folder in summary["folders"]}

        self.assertEqual(str(self.data_dir.resolve()), summary["data_path"])
        self.assertEqual({"downloads", "uploads", "recordings", "transcripts", "logs", "jobs", "queues"}, set(folders))
        self.assertTrue(folders["downloads"]["exists"])
        self.assertEqual(4, folders["downloads"]["size_bytes"])
        self.assertFalse(folders["uploads"]["exists"])
        self.assertEqual(0, folders["uploads"]["size_bytes"])
        self.assertEqual(7, summary["total_size_bytes"])

    def test_settings_default_to_keep_and_persist_changes(self) -> None:
        manager = self.make_manager()

        self.assertEqual(
            {"keep_downloaded_url_media": True, "keep_uploaded_temp_files": True},
            manager.settings(),
        )

        manager.update_settings({"keep_downloaded_url_media": False, "unknown": False})
        reloaded = self.make_manager().settings()

        self.assertEqual(
            {"keep_downloaded_url_media": False, "keep_uploaded_temp_files": True},
            reloaded,
        )

    def test_storage_settings_update_preserves_ocr_section(self) -> None:
        settings_path = self.data_dir / "settings.json"
        settings_path.write_text(
            '{"ocr":{"tesseract_path":"C:\\\\OCR\\\\tesseract.exe","default_languages":["rus","eng"]}}',
            encoding="utf-8",
        )

        self.make_manager().update_settings({"keep_downloaded_url_media": False})

        content = settings_path.read_text(encoding="utf-8")
        self.assertIn('"ocr"', content)
        self.assertIn('"tesseract_path"', content)

    def test_cleanup_deletes_only_allowed_intermediate_folders(self) -> None:
        (self.data_dir / "downloads" / "nested").mkdir(parents=True)
        (self.data_dir / "downloads" / "media.mp4").write_bytes(b"1234")
        (self.data_dir / "downloads" / "nested" / "part.tmp").write_bytes(b"12")
        (self.data_dir / "recordings").mkdir()
        (self.data_dir / "recordings" / "keep.wav").write_bytes(b"keep")
        (self.data_dir / "transcripts").mkdir()
        (self.data_dir / "transcripts" / "keep.txt").write_text("keep", encoding="utf-8")

        result = self.make_manager().cleanup_folder("downloads")

        self.assertEqual("downloads", result["folder"])
        self.assertEqual(2, result["deleted_entries"])
        self.assertEqual(6, result["deleted_bytes"])
        self.assertEqual([], result["errors"])
        self.assertEqual([], list((self.data_dir / "downloads").iterdir()))
        self.assertTrue((self.data_dir / "recordings" / "keep.wav").exists())
        self.assertTrue((self.data_dir / "transcripts" / "keep.txt").exists())

        with self.assertRaises(RuntimeError):
            self.make_manager().cleanup_folder("transcripts")

    def test_cleanup_missing_allowed_folder_is_a_noop(self) -> None:
        result = self.make_manager().cleanup_folder("uploads")

        self.assertEqual("uploads", result["folder"])
        self.assertEqual(0, result["deleted_entries"])
        self.assertEqual(0, result["deleted_bytes"])
        self.assertEqual([], result["errors"])

    def test_retention_cleanup_deletes_downloads_only_inside_project_data(self) -> None:
        manager = self.make_manager()
        manager.update_settings({"keep_downloaded_url_media": False})
        media_path = self.data_dir / "downloads" / "media.mp4"
        media_path.parent.mkdir(parents=True)
        media_path.write_bytes(b"media")

        result = manager.apply_retention_cleanup({
            "source_type": "url",
            "status": "completed",
            "downloaded_media_path": str(media_path),
        })

        self.assertTrue(result["downloaded_media_deleted"])
        self.assertFalse(media_path.exists())

        outside_path = self.root / "outside.mp4"
        outside_path.write_bytes(b"outside")
        result = manager.apply_retention_cleanup({
            "source_type": "url",
            "status": "cancelled",
            "downloaded_media_path": str(outside_path),
        })

        self.assertFalse(result["downloaded_media_deleted"])
        self.assertTrue(result["downloaded_media_delete_error"])
        self.assertTrue(outside_path.exists())

    def test_retention_cleanup_deletes_queue_owned_url_downloads(self) -> None:
        manager = self.make_manager()
        manager.update_settings({"keep_downloaded_url_media": False})
        media_path = self.data_dir / "queues" / "queue_1" / "item_001_url" / "downloads" / "media.mp4"
        media_path.parent.mkdir(parents=True)
        media_path.write_bytes(b"media")

        result = manager.apply_retention_cleanup({
            "source_type": "url",
            "status": "completed",
            "downloaded_media_path": str(media_path),
        })

        self.assertTrue(result["downloaded_media_deleted"])
        self.assertFalse(media_path.exists())

    def test_retention_cleanup_deletes_uploaded_temp_only_inside_project_data(self) -> None:
        manager = self.make_manager()
        manager.update_settings({"keep_uploaded_temp_files": False})
        upload_path = self.data_dir / "uploads" / "input.wav"
        upload_path.parent.mkdir(parents=True)
        upload_path.write_bytes(b"upload")

        result = manager.apply_retention_cleanup({
            "source_type": "local_file",
            "status": "completed",
            "source_path": str(upload_path),
        })

        self.assertTrue(result["uploaded_temp_deleted"])
        self.assertFalse(upload_path.exists())

        outside_path = self.root / "original.wav"
        outside_path.write_bytes(b"original")
        result = manager.apply_retention_cleanup({
            "source_type": "local_file",
            "status": "completed",
            "source_path": str(outside_path),
        })

        self.assertFalse(result["uploaded_temp_deleted"])
        self.assertTrue(result["uploaded_temp_delete_error"])
        self.assertTrue(outside_path.exists())

    def test_retention_cleanup_never_deletes_local_input_as_downloaded_media(self) -> None:
        manager = self.make_manager()
        manager.update_settings({"keep_downloaded_url_media": False})
        media_path = self.data_dir / "downloads" / "local-input.mp4"
        media_path.parent.mkdir(parents=True)
        media_path.write_bytes(b"local")

        result = manager.apply_retention_cleanup({
            "source_type": "local_file",
            "status": "error",
            "downloaded_media_path": str(media_path),
            "source_path": str(media_path),
        })

        self.assertNotIn("downloaded_media_deleted", result)
        self.assertTrue(media_path.exists())

    def test_retention_cleanup_missing_url_download_is_a_noop(self) -> None:
        manager = self.make_manager()
        manager.update_settings({"keep_downloaded_url_media": False})
        missing_path = self.data_dir / "downloads" / "missing.mp4"

        result = manager.apply_retention_cleanup({
            "source_type": "url",
            "status": "cancelled",
            "downloaded_media_path": str(missing_path),
        })

        self.assertFalse(result["downloaded_media_deleted"])
        self.assertIsNone(result["downloaded_media_delete_error"])

    def test_cancelled_local_upload_remains_even_when_keep_is_disabled(self) -> None:
        manager = self.make_manager()
        manager.update_settings({"keep_uploaded_temp_files": False})
        upload_path = self.data_dir / "uploads" / "cancelled.wav"
        upload_path.parent.mkdir(parents=True)
        upload_path.write_bytes(b"upload")

        result = manager.apply_retention_cleanup({
            "source_type": "local_file",
            "status": "cancelled",
            "source_path": str(upload_path),
        })

        self.assertNotIn("uploaded_temp_deleted", result)
        self.assertTrue(upload_path.exists())


if __name__ == "__main__":
    unittest.main()
