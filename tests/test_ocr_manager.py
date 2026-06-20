import json
import shutil
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import Mock, patch

from app import ocr_manager as ocr_module
from app.ocr_manager import OcrManager


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class OcrManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"codex_ocr_manager_{uuid4().hex}"
        self.root.mkdir(parents=True)
        self.settings_path = self.root / "settings.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def make_executable(self, folder: str = "configured") -> Path:
        path = self.root / folder / "tesseract.exe"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"test executable")
        return path

    @staticmethod
    def completed(argument: str, stdout: str, returncode: int = 0) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(["tesseract.exe", argument], returncode, stdout=stdout, stderr="")

    def successful_runs(self) -> list[subprocess.CompletedProcess[str]]:
        return [
            self.completed("--version", "tesseract 5.3.0\n leptonica-1.82"),
            self.completed("--list-langs", "List of available languages in tessdata (3):\neng\nrus\nosd\n"),
        ]

    def test_finds_configured_valid_tesseract_and_parses_version_and_languages(self) -> None:
        executable = self.make_executable()
        manager = OcrManager(settings_path=self.settings_path)
        manager.update_settings({"tesseract_path": str(executable)})

        with patch.object(ocr_module.subprocess, "run", side_effect=self.successful_runs()) as run:
            status = manager.tesseract_status()

        self.assertTrue(status["available"])
        self.assertEqual(str(executable), status["path"])
        self.assertEqual(str(executable), status["configured_path"])
        self.assertEqual("5.3.0", status["version"])
        self.assertEqual(["eng", "rus", "osd"], status["languages"])
        self.assertTrue(status["has_eng"])
        self.assertTrue(status["has_rus"])
        self.assertEqual(2, run.call_count)
        self.assertEqual(5.0, run.call_args.kwargs["timeout"])

    def test_falls_back_to_path_lookup(self) -> None:
        executable = self.make_executable("path")
        manager = OcrManager(settings_path=self.settings_path)

        with (
            patch.object(ocr_module.shutil, "which", return_value=str(executable)),
            patch.object(ocr_module.subprocess, "run", side_effect=self.successful_runs()),
        ):
            status = manager.tesseract_status()

        self.assertTrue(status["available"])
        self.assertEqual(str(executable), status["path"])
        self.assertIsNone(status["configured_path"])

    def test_falls_back_to_common_windows_install_path(self) -> None:
        executable = self.make_executable("common")
        manager = OcrManager(settings_path=self.settings_path)

        with (
            patch.object(ocr_module.shutil, "which", return_value=None),
            patch.object(ocr_module, "COMMON_WINDOWS_TESSERACT_PATHS", (executable,)),
            patch.object(ocr_module.subprocess, "run", side_effect=self.successful_runs()),
        ):
            status = manager.tesseract_status()

        self.assertTrue(status["available"])
        self.assertEqual(str(executable), status["path"])

    def test_missing_tesseract_returns_unavailable_without_exception(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        with (
            patch.object(ocr_module.shutil, "which", return_value=None),
            patch.object(ocr_module, "COMMON_WINDOWS_TESSERACT_PATHS", (self.root / "missing" / "tesseract.exe",)),
        ):
            status = manager.tesseract_status()

        self.assertFalse(status["available"])
        self.assertEqual("not_found", status["error"])
        self.assertIsNone(status["path"])

    def test_invalid_configured_path_returns_clear_error_without_fallback(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        invalid = self.root / "missing" / "tesseract.exe"
        manager.update_settings({"tesseract_path": str(invalid)})

        with (
            patch.object(ocr_module.shutil, "which") as which,
            patch.object(ocr_module.subprocess, "run") as run,
        ):
            status = manager.tesseract_status()

        self.assertFalse(status["available"])
        self.assertEqual("invalid_configured_path", status["error"])
        self.assertEqual(str(invalid), status["configured_path"])
        which.assert_not_called()
        run.assert_not_called()

    def test_version_timeout_and_failure_are_handled(self) -> None:
        executable = self.make_executable()
        manager = OcrManager(settings_path=self.settings_path)
        for side_effect, expected in (
            (subprocess.TimeoutExpired([str(executable), "--version"], 5), "version_timeout"),
            (self.completed("--version", "failed", returncode=1), "version_check_failed"),
        ):
            with self.subTest(expected=expected), patch.object(ocr_module.subprocess, "run", side_effect=[side_effect]):
                status = manager.tesseract_status(str(executable))
            self.assertFalse(status["available"])
            self.assertEqual(expected, status["error"])

    def test_language_timeout_and_failure_are_handled(self) -> None:
        executable = self.make_executable()
        manager = OcrManager(settings_path=self.settings_path)
        version = self.completed("--version", "tesseract 5.3.0")
        for language_result, expected in (
            (subprocess.TimeoutExpired([str(executable), "--list-langs"], 5), "languages_timeout"),
            (self.completed("--list-langs", "failed", returncode=1), "languages_check_failed"),
        ):
            with self.subTest(expected=expected), patch.object(
                ocr_module.subprocess,
                "run",
                side_effect=[version, language_result],
            ):
                status = manager.tesseract_status(str(executable))
            self.assertFalse(status["available"])
            self.assertEqual("5.3.0", status["version"])
            self.assertEqual(expected, status["error"])

    def test_language_parser_ignores_headers_whitespace_and_duplicates(self) -> None:
        output = "\n List of available languages in C:\\tessdata (4): \n eng \n\n rus\neng\n osd \n"
        self.assertEqual(["eng", "rus", "osd"], OcrManager._parse_languages(output))

    def test_settings_preserve_other_sections_and_normalize_languages(self) -> None:
        self.settings_path.write_text(json.dumps({"keep_downloaded_url_media": False}), encoding="utf-8")
        manager = OcrManager(settings_path=self.settings_path)
        manager.update_settings({"tesseract_path": "  C:\\OCR\\tesseract.exe  ", "default_languages": ["rus", "eng", "rus", "bad-code"]})

        payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
        self.assertFalse(payload["keep_downloaded_url_media"])
        self.assertEqual(r"C:\OCR\tesseract.exe", payload["ocr"]["tesseract_path"])
        self.assertEqual(["rus", "eng"], payload["ocr"]["default_languages"])

    def test_easyocr_available_without_initializing_reader(self) -> None:
        reader = Mock()
        module = SimpleNamespace(__version__="1.7.2", Reader=reader)
        manager = OcrManager(settings_path=self.settings_path)

        with patch.object(ocr_module.importlib, "import_module", return_value=module) as import_module:
            status = manager.easyocr_status()

        self.assertTrue(status["available"])
        self.assertEqual("available", status["status"])
        self.assertEqual("1.7.2", status["version"])
        self.assertEqual(["ru", "en"], status["languages"])
        import_module.assert_called_once_with("easyocr")
        reader.assert_not_called()

    def test_easyocr_not_installed(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        with patch.object(ocr_module.importlib, "import_module", side_effect=ModuleNotFoundError):
            status = manager.easyocr_status()

        self.assertFalse(status["available"])
        self.assertEqual("not_installed", status["status"])
        self.assertIn("optional_dependency_missing", status["notes"])

    def test_paddleocr_available_and_experimental(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        module = SimpleNamespace(__version__="3.0.0")
        with patch.object(ocr_module.importlib, "import_module", return_value=module):
            status = manager.paddleocr_status()

        self.assertTrue(status["available"])
        self.assertEqual("3.0.0", status["version"])
        self.assertIn("experimental", status["notes"])

    def test_paddleocr_not_installed_and_experimental(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        with patch.object(ocr_module.importlib, "import_module", side_effect=ImportError):
            status = manager.paddleocr_status()

        self.assertFalse(status["available"])
        self.assertEqual("not_installed", status["status"])
        self.assertIn("experimental", status["notes"])

    def test_windows_ocr_is_unsupported_off_windows(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        with (
            patch.object(ocr_module.platform, "system", return_value="Linux"),
            patch.object(ocr_module.importlib, "import_module") as import_module,
        ):
            status = manager.windows_ocr_status()

        self.assertEqual("unsupported_platform", status["status"])
        self.assertFalse(status["available"])
        import_module.assert_not_called()

    def test_windows_ocr_is_experimental_on_windows(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        with (
            patch.object(ocr_module.platform, "system", return_value="Windows"),
            patch.object(ocr_module.importlib, "import_module", return_value=SimpleNamespace()),
        ):
            status = manager.windows_ocr_status()

        self.assertTrue(status["available"])
        self.assertEqual("available", status["status"])
        self.assertIn("experimental", status["notes"])

    def test_combined_status_lists_all_backends_and_keeps_processing_disabled(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        unavailable = {"available": False}
        with (
            patch.object(manager, "tesseract_status", return_value={"id": "tesseract", **unavailable}),
            patch.object(manager, "easyocr_status", return_value={"id": "easyocr", **unavailable}),
            patch.object(manager, "paddleocr_status", return_value={"id": "paddleocr", **unavailable}),
            patch.object(manager, "windows_ocr_status", return_value={"id": "windows_ocr", **unavailable}),
        ):
            status = manager.status()

        self.assertEqual("tesseract", status["selected_backend"])
        self.assertEqual({"tesseract", "easyocr", "paddleocr", "windows_ocr"}, set(status["backends"]))
        self.assertFalse(status["processing_enabled"])

    def test_selected_backend_is_persisted_and_invalid_updates_are_rejected(self) -> None:
        manager = OcrManager(settings_path=self.settings_path)
        manager.update_settings({"selected_backend": "easyocr"})

        self.assertEqual("easyocr", OcrManager(settings_path=self.settings_path).settings()["selected_backend"])
        with self.assertRaisesRegex(ValueError, "invalid_ocr_backend"):
            manager.update_settings({"selected_backend": "unknown"})
        self.assertEqual("easyocr", manager.settings()["selected_backend"])

    def test_invalid_stored_backend_falls_back_to_tesseract(self) -> None:
        self.settings_path.write_text(json.dumps({"ocr": {"selected_backend": "unknown"}}), encoding="utf-8")
        self.assertEqual("tesseract", OcrManager(settings_path=self.settings_path).settings()["selected_backend"])


if __name__ == "__main__":
    unittest.main()
