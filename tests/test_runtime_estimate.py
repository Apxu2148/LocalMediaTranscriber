import shutil
import threading
import unittest
from pathlib import Path
from uuid import uuid4

from app.queue_manager import QueueFile, QueueManager
from app.runtime_estimate import RuntimeEstimateError, RuntimeEstimator, sample_ocr_frame_indices


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
        self.assertFalse(result["ocr"]["enabled"])
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
                "ocr": {"enabled": False, "engine_available": True, "status": "disabled"},
            },
        })

        self.assertEqual("complete", result["status"])
        self.assertTrue(result["no_enabled_operations"])
        self.assertFalse(result["ocr"]["enabled"])
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

    def test_no_audio_stream_estimate_keeps_frames_and_ocr(self) -> None:
        def process_frames(_source: Path, _output: Path, _duration: float, _rate: dict, _quality: int, _max_size: str) -> dict:
            return {"sample_frames": 2}

        def extract_ocr_frames(
            _source: Path,
            output: Path,
            timestamps: list[float],
            _quality: int,
            _max_size: str,
        ) -> dict:
            output.mkdir(parents=True, exist_ok=True)
            paths = []
            for position, _timestamp in enumerate(timestamps, start=1):
                path = output / f"ocr_{position}.jpg"
                path.write_bytes(b"jpeg")
                paths.append(path)
            return {"sample_frames": len(paths), "frame_paths": [str(path) for path in paths]}

        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: self.fail("audio must be skipped when no stream exists"),
            frame_processor=process_frames,
            ocr_frame_processor=extract_ocr_frames,
            ocr_processor=lambda frame_paths, _languages: {
                "sample_frames": len(frame_paths),
                "sample_runtime_sec": 1.5,
                "average_sec_per_frame": 0.5,
            },
            ocr_status_reader=lambda: {"available": True, "status": "available"},
            duration_reader=lambda _path: 90.0,
            audio_stream_reader=lambda _path: False,
            temp_root=self.temp_root,
            clock=SequenceClock(0.0, 1.0),
        )
        result = estimator.estimate({
            "source_path": str(self.source),
            "source_filename": self.source.name,
            "processing_plan": {
                "audio": {"enabled": True, "model": "small", "device": "auto"},
                "frames": {
                    "enabled": True,
                    "rate": {"mode": "interval", "seconds": 30},
                    "jpeg_quality": 80,
                    "max_frame_size": "width_640",
                },
                "ocr": {"enabled": True, "backend": "easyocr", "engine_available": True},
            },
        })

        self.assertEqual("complete", result["status"])
        self.assertEqual("unavailable", result["audio"]["status"])
        self.assertEqual("no_audio_stream", result["audio"]["reason"])
        self.assertFalse(result["audio"]["included_in_total"])
        self.assertTrue(result["total_excludes_audio"])
        self.assertTrue(result["frames"]["enabled"])
        self.assertEqual(2.0, result["frames"]["estimated_full_runtime_sec"])
        self.assertTrue(result["ocr"]["included_in_total"])
        self.assertEqual(2.0, result["ocr"]["estimated_full_runtime_sec"])
        self.assertEqual(4.0, result["total_estimated_full_runtime_sec"])

    def test_no_audio_sample_failure_is_converted_to_unavailable_audio(self) -> None:
        def prepare_sample(_source: Path, _sample_duration: float, _source_duration: float, _workspace: Path) -> Path:
            raise RuntimeEstimateError("sample_preparation_failed", "Output file #0 does not contain any stream")

        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: self.fail("audio must be skipped after no-audio sample failure"),
            frame_processor=lambda *_args: {"sample_frames": 1},
            duration_reader=lambda _path: 90.0,
            audio_stream_reader=lambda _path: None,
            sample_preparer=prepare_sample,
            temp_root=self.temp_root,
            clock=SequenceClock(0.0, 1.0),
        )
        result = estimator.estimate({
            "source_path": str(self.source),
            "processing_plan": {
                "audio": {"enabled": True, "model": "small", "device": "cpu"},
                "frames": {"enabled": True, "rate": {"mode": "interval", "seconds": 30}},
            },
        })

        self.assertEqual("complete", result["status"])
        self.assertEqual("unavailable", result["audio"]["status"])
        self.assertEqual("no_audio_stream", result["audio"]["reason"])
        self.assertTrue(result["frames"]["enabled"])
        self.assertTrue(result["total_excludes_audio"])
        self.assertEqual(result["frames"]["estimated_full_runtime_sec"], result["total_estimated_full_runtime_sec"])

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

    def test_easyocr_estimate_scales_sampled_frames_and_is_included_in_total(self) -> None:
        ocr_calls: dict[str, object] = {}

        def process_frames(_source: Path, output: Path, _duration: float, _rate: dict, _quality: int, _max_size: str) -> dict:
            (output / "sample.jpg").write_bytes(b"jpeg")
            return {"sample_frames": 2}

        def extract_ocr_frames(
            _source: Path,
            output: Path,
            timestamps: list[float],
            _quality: int,
            _max_size: str,
        ) -> dict:
            ocr_calls["timestamps"] = list(timestamps)
            output.mkdir(parents=True, exist_ok=True)
            paths = []
            for position, _timestamp in enumerate(timestamps, start=1):
                path = output / f"ocr_{position}.jpg"
                path.write_bytes(b"jpeg")
                paths.append(path)
            return {"sample_frames": len(paths), "frame_paths": [str(path) for path in paths]}

        def estimate_ocr(frame_paths: list[Path], languages: list[str]) -> dict:
            ocr_calls["frame_paths"] = [path.name for path in frame_paths]
            ocr_calls["languages"] = languages
            return {
                "sample_frames": len(frame_paths),
                "sample_runtime_sec": 6.0,
                "average_sec_per_frame": 2.0,
                "median_sec_per_frame": 2.0,
            }

        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: self.fail("audio must be skipped"),
            frame_processor=process_frames,
            ocr_frame_processor=extract_ocr_frames,
            ocr_processor=estimate_ocr,
            ocr_status_reader=lambda: {"available": True, "status": "available"},
            duration_reader=lambda _path: 90.0,
            temp_root=self.temp_root,
            clock=SequenceClock(0.0, 1.0),
        )
        result = estimator.estimate({
            "index": 7,
            "source_path": str(self.source),
            "source_filename": self.source.name,
            "processing_plan": {
                "audio": {"enabled": False},
                "frames": {
                    "enabled": True,
                    "rate": {"mode": "interval", "seconds": 30},
                    "jpeg_quality": 80,
                    "max_frame_size": "width_640",
                },
                "ocr": {"enabled": True, "backend": "easyocr", "engine_available": True, "languages": ["ru", "en"]},
            },
        })

        self.assertEqual(["ru", "en"], ocr_calls["languages"])
        self.assertLessEqual(len(ocr_calls["timestamps"]), 3)
        self.assertLessEqual(len(ocr_calls["frame_paths"]), 3)
        self.assertEqual(4, result["ocr"]["expected_total_frames"])
        self.assertEqual(8.0, result["ocr"]["estimated_full_runtime_sec"])
        self.assertTrue(result["ocr"]["included_in_total"])
        self.assertEqual(2.0, result["frames"]["estimated_full_runtime_sec"])
        self.assertEqual(10.0, result["total_estimated_full_runtime_sec"])
        self.assertEqual([], list(self.temp_root.iterdir()))

    def test_easyocr_unavailable_marks_ocr_excluded_without_sampling(self) -> None:
        estimator = RuntimeEstimator(
            audio_processor=lambda *_args: self.fail("audio must be skipped"),
            frame_processor=lambda *_args: self.fail("frames must be skipped"),
            ocr_frame_processor=lambda *_args: self.fail("ocr frames must be skipped"),
            ocr_processor=lambda *_args: self.fail("ocr must be skipped"),
            ocr_status_reader=lambda: {"available": False, "status": "not_installed"},
            duration_reader=lambda _path: 60.0,
            temp_root=self.temp_root,
        )
        result = estimator.estimate({
            "source_path": str(self.source),
            "processing_plan": {
                "audio": {"enabled": False},
                "frames": {"enabled": False, "rate": {"mode": "interval", "seconds": 30}},
                "ocr": {"enabled": True, "backend": "easyocr", "engine_available": False},
            },
        })

        self.assertEqual("unavailable", result["ocr"]["status"])
        self.assertEqual("easyocr_unavailable", result["ocr"]["reason"])
        self.assertTrue(result["total_excludes_ocr"])
        self.assertIsNone(result["ocr"]["estimated_full_runtime_sec"])
        self.assertIsNone(result["total_estimated_full_runtime_sec"])

    def test_ocr_sampling_is_deterministic_capped_and_uses_all_small_counts(self) -> None:
        first = sample_ocr_frame_indices(52, "same-source-settings")
        second = sample_ocr_frame_indices(52, "same-source-settings")

        self.assertEqual(first, second)
        self.assertLessEqual(len(first), 3)
        self.assertEqual([0, 1, 2], sample_ocr_frame_indices(3, "small"))


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
