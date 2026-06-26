import shutil
import threading
import unittest
from pathlib import Path
from uuid import uuid4

from app.queue_manager import QueueFile, QueueManager
from app.runtime_estimate import RuntimeEstimateError, RuntimeEstimator


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class SequenceClock:
    def __init__(self, *values: float) -> None:
        self.values = iter(values)

    def __call__(self) -> float:
        return next(self.values)


class RuntimeEstimatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"runtime_estimate_{uuid4().hex}"
        self.temp_root = self.root / "temp"
        self.root.mkdir(parents=True, exist_ok=True)
        self.source = self.root / "source.mp4"
        self.source.write_bytes(b"source")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_combined_estimate_uses_item_plan_and_cleans_workspace(self) -> None:
        calls: dict[str, object] = {}

        def prepare_sample(source: Path, sample_duration: float, source_duration: float, workspace: Path) -> Path:
            calls["sample"] = (source, sample_duration, source_duration)
            sample = workspace / "sample.wav"
            sample.write_bytes(b"sample")
            return sample

        def process_audio(sample: Path, model: str, device: str) -> dict:
            calls["audio"] = (sample.name, model, device)
            (sample.parent / "audio_scratch.tmp").write_bytes(b"scratch")
            return {"device": "cuda", "compute_type": "float16"}

        def process_frames(source: Path, output: Path, duration: float, rate: dict, quality: int, max_size: str) -> dict:
            calls["frames"] = (source, duration, rate, quality, max_size)
            (output / "sample.jpg").write_bytes(b"jpeg")
            return {"sample_frames": 3}

        estimator = RuntimeEstimator(
            audio_processor=process_audio,
            frame_processor=process_frames,
            duration_reader=lambda _path: 180.0,
            sample_preparer=prepare_sample,
            temp_root=self.temp_root,
            clock=SequenceClock(0.0, 8.0, 10.0, 11.2),
        )
        result = estimator.estimate({
            "source_path": str(self.source),
            "source_type": "local_file",
            "processing_plan": {
                "audio": {"enabled": True, "model": "base", "device": "cuda"},
                "frames": {
                    "enabled": True,
                    "rate": {"mode": "interval", "seconds": 30},
                    "jpeg_quality": 75,
                    "max_frame_size": "width_1280",
                },
            },
        })

        self.assertEqual(("sample.wav", "base", "cuda"), calls["audio"])
        self.assertEqual(
            ({"mode": "interval", "seconds": 30}, 75, "width_1280"),
            (calls["frames"][2], calls["frames"][3], calls["frames"][4]),
        )
        self.assertEqual(60.0, result["sample_duration_sec"])
        self.assertEqual(24.0, result["audio"]["estimated_full_runtime_sec"])
        self.assertEqual(7.5, result["audio"]["speed_factor"])
        self.assertEqual(7, result["frames"]["estimated_total_frames"])
        self.assertEqual(2.8, result["frames"]["estimated_full_runtime_sec"])
        self.assertEqual(26.8, result["total_estimated_full_runtime_sec"])
        self.assertEqual([], list(self.temp_root.iterdir()))

    def test_short_source_caps_sample_and_skips_disabled_frames(self) -> None:
        sample_durations: list[float] = []

        def prepare_sample(source: Path, sample_duration: float, _source_duration: float, _workspace: Path) -> Path:
            sample_durations.append(sample_duration)
            return source

        estimator = RuntimeEstimator(
            audio_processor=lambda _path, _model, _device: {"device": "cpu", "compute_type": "int8"},
            frame_processor=lambda *_args: self.fail("frames must be skipped"),
            duration_reader=lambda _path: 30.0,
            sample_preparer=prepare_sample,
            temp_root=self.temp_root,
            clock=SequenceClock(2.0, 5.0),
        )
        result = estimator.estimate({
            "source_path": str(self.source),
            "processing_plan": {
                "audio": {"enabled": True, "model": "small", "device": "cpu"},
                "frames": {"enabled": False},
            },
        })

        self.assertEqual([30.0], sample_durations)
        self.assertEqual(30.0, result["sample_duration_sec"])
        self.assertEqual(3.0, result["audio"]["estimated_full_runtime_sec"])
        self.assertFalse(result["frames"]["enabled"])

    def test_no_enabled_operations_returns_clear_noop_without_reading_duration(self) -> None:
        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: self.fail("audio must be skipped"),
            frame_processor=lambda *_args: self.fail("frames must be skipped"),
            duration_reader=lambda _path: self.fail("duration must be skipped"),
            temp_root=self.temp_root,
        )
        result = estimator.estimate({
            "processing_plan": {
                "audio": {"enabled": False},
                "frames": {"enabled": False},
                "ocr": {"enabled": True, "engine_available": True, "status": "coming_soon"},
            },
        })

        self.assertEqual("complete", result["status"])
        self.assertTrue(result["no_enabled_operations"])
        self.assertIsNone(result["total_estimated_full_runtime_sec"])

    def test_frame_only_estimate_skips_audio(self) -> None:
        frame_calls: list[tuple[float, dict, int, str]] = []

        def process_frames(_source: Path, output: Path, duration: float, rate: dict, quality: int, max_size: str) -> dict:
            frame_calls.append((duration, rate, quality, max_size))
            (output / "sample.jpg").write_bytes(b"jpeg")
            return {"sample_frames": 2}

        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: self.fail("audio must be skipped"),
            frame_processor=process_frames,
            duration_reader=lambda _path: 90.0,
            temp_root=self.temp_root,
            clock=SequenceClock(0.0, 1.0),
        )
        result = estimator.estimate({
            "source_path": str(self.source),
            "processing_plan": {
                "audio": {"enabled": False},
                "frames": {
                    "enabled": True,
                    "rate": {"mode": "interval", "seconds": 30},
                    "jpeg_quality": 80,
                    "max_frame_size": "bad",
                },
            },
        })

        self.assertFalse(result["audio"]["enabled"])
        self.assertEqual([(60.0, {"mode": "interval", "seconds": 30}, 80, "original")], frame_calls)
        self.assertTrue(result["frames"]["enabled"])
        self.assertEqual("original", result["frames"]["max_frame_size"])

    def test_missing_duration_returns_stable_error_code(self) -> None:
        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: {},
            frame_processor=lambda *_args: {},
            duration_reader=lambda _path: None,
            temp_root=self.temp_root,
        )
        with self.assertRaises(RuntimeEstimateError) as context:
            estimator.estimate({
                "source_path": str(self.source),
                "processing_plan": {
                    "audio": {"enabled": True, "model": "small", "device": "auto"},
                    "frames": {"enabled": False},
                },
            })
        self.assertEqual("duration_unavailable", context.exception.code)

    def test_failure_still_cleans_temporary_files(self) -> None:
        def fail_audio(sample: Path, _model: str, _device: str) -> dict:
            (sample.parent / "leftover.tmp").write_bytes(b"scratch")
            raise RuntimeError("sample failed")

        estimator = RuntimeEstimator(
            audio_processor=fail_audio,
            frame_processor=lambda *_args: {},
            duration_reader=lambda _path: 10.0,
            temp_root=self.temp_root,
            clock=SequenceClock(0.0),
        )
        with self.assertRaisesRegex(RuntimeError, "sample failed"):
            estimator.estimate({
                "source_path": str(self.source),
                "processing_plan": {
                    "audio": {"enabled": True, "model": "tiny", "device": "auto"},
                    "frames": {"enabled": False},
                },
            })
        self.assertEqual([], list(self.temp_root.iterdir()))

    def test_url_without_cached_file_requires_download(self) -> None:
        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: {},
            frame_processor=lambda *_args: {},
            temp_root=self.temp_root,
        )
        with self.assertRaises(RuntimeEstimateError) as context:
            estimator.estimate({
                "source_type": "url",
                "source_path": None,
                "processing_plan": {
                    "audio": {"enabled": True, "model": "small", "device": "auto"},
                    "frames": {"enabled": False},
                },
            })
        self.assertEqual("url_download_required", context.exception.code)


class QueueRuntimeEstimateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"queue_runtime_estimate_{uuid4().hex}"
        self.root.mkdir(parents=True, exist_ok=True)
        self.source = self.root / "source.wav"
        self.source.write_bytes(b"audio")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_estimate_keeps_item_pending_and_normal_processing_still_works(self) -> None:
        estimated_plans: list[dict] = []
        processed: list[str] = []

        def estimate_processor(item: dict) -> dict:
            estimated_plans.append(item["processing_plan"])
            return {
                "status": "complete",
                "audio": {"enabled": True, "estimated_full_runtime_sec": 12.0},
                "frames": {"enabled": False},
                "total_estimated_full_runtime_sec": 12.0,
            }

        def processor(item: dict, _model: str, _device: str) -> dict:
            processed.append(item["source_filename"])
            return {"audio_duration_sec": 5, "processing_time_sec": 1}

        manager = QueueManager(
            jobs_dir=self.root,
            processor=processor,
            estimate_processor=estimate_processor,
            duration_reader=lambda _path: 5,
        )
        status = manager.add_files([QueueFile(
            source_path=self.source,
            source_filename=self.source.name,
            processing_plan={
                "audio": {"enabled": True, "model": "base", "device": "cuda"},
                "frames": {"enabled": False},
            },
        )])
        result = manager.estimate_item(status["items"][0]["index"])

        item = result["items"][0]
        self.assertEqual("pending", item["status"])
        self.assertEqual({}, item["outputs"])
        self.assertIsNone(item["transcript_path"])
        self.assertEqual("base", estimated_plans[0]["audio"]["model"])
        self.assertEqual("cuda", estimated_plans[0]["audio"]["device"])

        manager.start("tiny", "cpu")
        manager.wait(timeout=3)
        self.assertEqual([self.source.name], processed)
        self.assertEqual("completed", manager.status()["items"][0]["status"])

    def test_queue_start_is_blocked_while_estimate_is_running(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def estimate_processor(_item: dict) -> dict:
            started.set()
            release.wait(timeout=3)
            return {"status": "complete"}

        manager = QueueManager(
            jobs_dir=self.root,
            processor=lambda _item, _model, _device: {},
            estimate_processor=estimate_processor,
        )
        status = manager.add_files([QueueFile(source_path=self.source, source_filename=self.source.name)])
        worker = threading.Thread(target=manager.estimate_item, args=(status["items"][0]["index"],))
        worker.start()
        self.assertTrue(started.wait(timeout=2))
        self.assertTrue(manager.is_estimating)
        with self.assertRaisesRegex(RuntimeError, "оценки"):
            manager.start("small", "cpu")
        release.set()
        worker.join(timeout=3)
        self.assertFalse(manager.is_estimating)


if __name__ == "__main__":
    unittest.main()
