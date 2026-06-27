import json
import shutil
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from app import config
from app import ocr_processor as ocr_module
from app.ocr_processor import EasyOcrFrameProcessor, OcrProcessorError, process_easyocr_frames


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeReader:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def readtext(self, path: str, detail: int = 1):
        self.calls.append(Path(path).name)
        response = self.responses.get(Path(path).name, [])
        if isinstance(response, Exception):
            raise response
        return response


class SequenceClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        self.value += 0.1
        return self.value


class EasyOcrFrameProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"ocr_processor_{uuid4().hex}"
        self.frames_dir = self.root / "clip__frames"
        self.frames_dir.mkdir(parents=True)
        self.index_path = self.frames_dir / "frames_index.json"
        self.frames = [
            {"index": 1, "t": 0.0, "file": "frame_000001.jpg", "width": 100, "height": 50},
            {"index": 2, "t": 10.0, "file": "frame_000002.jpg", "width": 100, "height": 50},
        ]
        for frame in self.frames:
            (self.frames_dir / frame["file"]).write_bytes(b"jpeg")
        self.index_path.write_text(json.dumps({"frames": self.frames}, ensure_ascii=False), encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_missing_easyocr_import_fails_without_crashing_startup(self) -> None:
        with patch.object(ocr_module.importlib, "import_module", side_effect=ModuleNotFoundError("easyocr")):
            with self.assertRaisesRegex(OcrProcessorError, "EasyOCR is not installed"):
                process_easyocr_frames(frames_index_path=self.index_path)

    def test_ocr_processor_does_not_import_easyocr_at_module_import_time(self) -> None:
        source = (PROJECT_ROOT / "app" / "ocr_processor.py").read_text(encoding="utf-8")

        self.assertNotIn("import easyocr", source)

    def test_converts_easyocr_results_to_jsonl_and_txt(self) -> None:
        reader = FakeReader({
            "frame_000001.jpg": [([[1, 2], [3, 2], [3, 4], [1, 4]], "Hello 123", 0.91)],
            "frame_000002.jpg": [([[5, 6], [7, 6], [7, 8], [5, 8]], "Привет", 0.82)],
        })
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader, clock=SequenceClock())

        result = processor.process_frames(frames_index_path=self.index_path, languages=["ru", "en"])

        self.assertEqual("completed", result["status"])
        self.assertEqual(2, result["frames_processed"])
        self.assertEqual(2, result["frames_with_text"])
        self.assertEqual(["frame_000001.jpg", "frame_000002.jpg"], reader.calls)
        jsonl_path = config.BASE_DIR / result["jsonl_path"]
        txt_path = config.BASE_DIR / result["txt_path"]
        records = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual("Hello 123", records[0]["text"])
        self.assertEqual(0.91, records[0]["blocks"][0]["confidence"])
        self.assertIn("Привет", txt_path.read_text(encoding="utf-8"))

    def test_can_write_outputs_to_separate_ocr_directory(self) -> None:
        reader = FakeReader({"frame_000001.jpg": [], "frame_000002.jpg": []})
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader)
        ocr_dir = self.root / "item_001" / "ocr"

        result = processor.process_frames(frames_index_path=self.index_path, output_dir=ocr_dir)

        self.assertEqual((ocr_dir / "frames_ocr.jsonl").resolve(), (config.BASE_DIR / result["jsonl_path"]).resolve())
        self.assertEqual((ocr_dir / "frames_ocr.txt").resolve(), (config.BASE_DIR / result["txt_path"]).resolve())
        self.assertEqual(self.frames_dir.resolve(), (config.BASE_DIR / result["frames_path"]).resolve())
        self.assertFalse((self.frames_dir / "frames_ocr.jsonl").exists())

    def test_empty_frame_result_is_recorded_and_skipped_in_txt(self) -> None:
        reader = FakeReader({"frame_000001.jpg": [], "frame_000002.jpg": []})
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader)

        result = processor.process_frames(frames_index_path=self.index_path)

        self.assertEqual(2, result["frames_processed"])
        self.assertEqual(0, result["frames_with_text"])
        self.assertEqual("", (self.frames_dir / "frames_ocr.txt").read_text(encoding="utf-8"))

    def test_frame_level_error_and_missing_file_do_not_stop_processing(self) -> None:
        self.frames[1]["file"] = "missing.jpg"
        self.index_path.write_text(json.dumps({"frames": self.frames}, ensure_ascii=False), encoding="utf-8")
        reader = FakeReader({"frame_000001.jpg": RuntimeError("bad frame")})
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader)

        result = processor.process_frames(frames_index_path=self.index_path)

        records = [json.loads(line) for line in (self.frames_dir / "frames_ocr.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual("completed", result["status"])
        self.assertIn("bad frame", records[0]["error"])
        self.assertIn("missing", records[1]["error"])
        self.assertIn("OCR error", (self.frames_dir / "frames_ocr.txt").read_text(encoding="utf-8"))

    def test_cancellation_stops_between_frames_and_keeps_complete_partial_outputs(self) -> None:
        cancel_event = threading.Event()
        progress: list[dict] = []
        reader = FakeReader({
            "frame_000001.jpg": [([[0, 0], [1, 0], [1, 1], [0, 1]], "first", 0.9)],
            "frame_000002.jpg": [([[0, 0], [1, 0], [1, 1], [0, 1]], "second", 0.9)],
        })

        def on_progress(payload: dict) -> None:
            progress.append(payload)
            cancel_event.set()

        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader)
        result = processor.process_frames(
            frames_index_path=self.index_path,
            cancel_event=cancel_event,
            progress_callback=on_progress,
        )

        self.assertEqual("cancelled", result["status"])
        self.assertEqual(1, result["frames_processed"])
        records = (self.frames_dir / "frames_ocr.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(1, len(records))
        self.assertEqual(1, progress[0]["frames_processed"])

    def test_missing_frames_are_controlled_failure(self) -> None:
        self.index_path.write_text(json.dumps({"frames": []}), encoding="utf-8")
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: FakeReader({}))

        with self.assertRaisesRegex(OcrProcessorError, "no frames"):
            processor.process_frames(frames_index_path=self.index_path)

    def test_benchmark_fields_are_computed(self) -> None:
        reader = FakeReader({"frame_000001.jpg": [], "frame_000002.jpg": []})
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader, clock=SequenceClock())

        result = processor.process_frames(frames_index_path=self.index_path)

        self.assertIn("ocr_time_sec", result)
        self.assertIn("sec_per_frame", result)
        self.assertEqual("easyocr", result["backend"])
        self.assertEqual(["ru", "en"], result["languages"])

    def test_estimate_frame_runtime_uses_fake_reader_without_writing_artifacts(self) -> None:
        reader = FakeReader({"frame_000001.jpg": [], "frame_000002.jpg": []})
        processor = EasyOcrFrameProcessor(reader_factory=lambda _langs: reader, clock=SequenceClock())

        result = processor.estimate_frame_runtime(
            frame_paths=[self.frames_dir / "frame_000001.jpg", self.frames_dir / "frame_000002.jpg"],
            languages=["ru", "en"],
        )

        self.assertEqual("complete", result["status"])
        self.assertEqual(2, result["sample_frames"])
        self.assertEqual(0.1, result["average_sec_per_frame"])
        self.assertEqual(["frame_000001.jpg", "frame_000002.jpg"], reader.calls)
        self.assertFalse((self.frames_dir / "frames_ocr.jsonl").exists())
        self.assertFalse((self.frames_dir / "frames_ocr.txt").exists())

    def test_easyocr_dependency_is_isolated_to_optional_requirements(self) -> None:
        self.assertEqual("easyocr", (PROJECT_ROOT / "requirements-ocr-easyocr.txt").read_text(encoding="utf-8").strip())
        self.assertNotIn("easyocr", (PROJECT_ROOT / "requirements-cpu.txt").read_text(encoding="utf-8").casefold())
        self.assertNotIn("easyocr", (PROJECT_ROOT / "requirements-gpu.txt").read_text(encoding="utf-8").casefold())


if __name__ == "__main__":
    unittest.main()
