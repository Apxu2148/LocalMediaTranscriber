import json
import shutil
import threading
import unittest
from pathlib import Path
from uuid import uuid4

from app.frame_extractor import (
    ALLOWED_JPEG_QUALITIES,
    VideoFrameExtractor,
    estimate_frame_count,
    frame_timestamps,
    normalize_jpeg_quality,
    read_video_metadata,
)


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None


class FrameExtractorSettingsTests(unittest.TestCase):
    def test_jpeg_quality_100_is_allowed_and_default_stays_90(self) -> None:
        self.assertEqual((75, 80, 85, 90, 95, 100), ALLOWED_JPEG_QUALITIES)
        self.assertIn(80, ALLOWED_JPEG_QUALITIES)
        self.assertIn(100, ALLOWED_JPEG_QUALITIES)
        self.assertEqual(90, normalize_jpeg_quality(None))
        self.assertEqual(90, normalize_jpeg_quality(""))
        self.assertEqual(80, normalize_jpeg_quality(80))
        self.assertEqual(100, normalize_jpeg_quality(100))


@unittest.skipUnless(cv2 is not None and np is not None, "opencv-python is required for frame extractor fixtures")
class FrameExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prefix = f"cfe_{uuid4().hex[:8]}"
        self.root = PROJECT_TMP / self.prefix
        self.recordings_dir = self.root / "recordings"
        self.root.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = VideoFrameExtractor(recordings_dir=self.recordings_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def make_video(self, name: str, *, fps: float = 5.0, frames: int = 10, size: tuple[int, int] = (64, 48)) -> Path:
        path = self.root / name
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(str(path), fourcc, fps, size)
        self.assertTrue(writer.isOpened())
        try:
            for index in range(frames):
                frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
                frame[:, :, 0] = (index * 30) % 255
                frame[:, :, 1] = 80
                frame[:, :, 2] = 200
                writer.write(frame)
        finally:
            writer.release()
        return path

    def test_metadata_and_estimates_for_interval_and_fps_modes(self) -> None:
        path = self.make_video("metadata.avi", fps=5, frames=10)
        metadata = read_video_metadata(path)

        self.assertEqual(64, metadata["width"])
        self.assertEqual(48, metadata["height"])
        self.assertGreater(metadata["duration_sec"], 0)
        self.assertEqual(1, estimate_frame_count(0, {"mode": "interval", "seconds": 10}))
        self.assertEqual(4, estimate_frame_count(30, {"mode": "interval", "seconds": 10}))
        self.assertEqual(11, estimate_frame_count(5, {"mode": "fps", "fps": 2}))

    def test_timestamps_always_include_zero(self) -> None:
        self.assertEqual(0.0, frame_timestamps(2.1, {"mode": "interval", "seconds": 1})[0])
        self.assertEqual([0.0], frame_timestamps(0, {"mode": "fps", "fps": 30}))

    def test_extracts_jpegs_and_writes_index(self) -> None:
        path = self.make_video("extract.avi", fps=5, frames=15)
        result = self.extractor.extract_frames(
            source_path=path,
            source_filename="extract.avi",
            output_base="extract",
            rate={"mode": "interval", "seconds": 1},
            jpeg_quality=85,
        )

        self.assertEqual("completed", result["status"])
        frames_dir = self.recordings_dir / result["frames_dir"]
        index_path = frames_dir / "frames_index.json"
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertTrue(payload["completed"])
        self.assertEqual(85, payload["extraction"]["jpeg_quality"])
        self.assertGreaterEqual(payload["extracted_frame_count"], 1)
        self.assertEqual(0.0, payload["frames"][0]["t"])
        self.assertTrue((frames_dir / payload["frames"][0]["file"]).is_file())
        self.assertEqual(payload["extracted_frame_count"], len(list(frames_dir.glob("*.jpg"))))

    def test_extract_sample_writes_only_to_requested_temporary_directory(self) -> None:
        path = self.make_video("sample.avi", fps=5, frames=15)
        output_dir = self.root / "estimate_sample"

        result = self.extractor.extract_sample(
            source_path=path,
            output_dir=output_dir,
            sample_duration_sec=1,
            rate={"mode": "interval", "seconds": 1},
            jpeg_quality=75,
        )

        self.assertGreaterEqual(result["sample_frames"], 1)
        self.assertEqual(result["sample_frames"], len(list(output_dir.glob("*.jpg"))))
        self.assertFalse((output_dir / "frames_index.json").exists())
        self.assertEqual([], list(self.recordings_dir.iterdir()))

    def test_unicode_output_base_writes_jpegs_and_index(self) -> None:
        path = self.make_video("unicode.avi", fps=5, frames=8)
        result = self.extractor.extract_frames(
            source_path=path,
            source_filename="\u0427\u0430\u0441\u0442\u044c 1.webm",
            output_base="\u0427\u0430\u0441\u0442\u044c 1",
            rate={"mode": "interval", "seconds": 1},
            jpeg_quality=90,
        )

        self.assertEqual("completed", result["status"])
        self.assertIn("\u0427\u0430\u0441\u0442\u044c 1", result["frames_dir"])
        frames_dir = self.recordings_dir / result["frames_dir"]
        payload = json.loads((frames_dir / "frames_index.json").read_text(encoding="utf-8"))
        self.assertGreater(payload["extracted_frame_count"], 0)
        self.assertTrue((frames_dir / payload["frames"][0]["file"]).is_file())

    def test_requested_fps_above_source_fps_does_not_crash(self) -> None:
        path = self.make_video("slow.avi", fps=3, frames=6)
        result = self.extractor.extract_frames(
            source_path=path,
            source_filename="slow.avi",
            output_base="slow",
            rate={"mode": "fps", "fps": 30},
            jpeg_quality=90,
        )

        self.assertEqual("completed", result["status"])
        self.assertTrue(result["requested_fps_exceeds_source_fps"])
        self.assertGreater(result["extracted_frame_count"], 0)

    def test_cancellation_writes_incomplete_index_and_keeps_partial_frames(self) -> None:
        path = self.make_video("cancel.avi", fps=5, frames=20)
        cancel_event = threading.Event()

        def cancel_after_first(_progress: dict) -> None:
            cancel_event.set()

        result = self.extractor.extract_frames(
            source_path=path,
            source_filename="cancel.avi",
            output_base="cancel",
            rate={"mode": "interval", "seconds": 1},
            jpeg_quality=90,
            cancel_event=cancel_event,
            progress_callback=cancel_after_first,
        )

        self.assertEqual("cancelled", result["status"])
        self.assertFalse(result["completed"])
        self.assertEqual(1, result["extracted_frame_count"])
        payload = json.loads((self.recordings_dir / result["frames_dir"] / "frames_index.json").read_text(encoding="utf-8"))
        self.assertTrue(payload["cancelled"])
        self.assertFalse(payload["completed"])
        self.assertEqual(1, payload["extracted_frame_count"])
        self.assertEqual(1, len(list((self.recordings_dir / result["frames_dir"]).glob("*.jpg"))))

    def test_invalid_video_returns_structured_failure(self) -> None:
        path = self.root / "bad.avi"
        path.write_bytes(b"not a video")
        result = self.extractor.extract_frames(
            source_path=path,
            source_filename="bad.avi",
            output_base="bad",
            rate={"mode": "interval", "seconds": 1},
            jpeg_quality=90,
        )

        self.assertEqual("failed", result["status"])
        self.assertFalse(result["completed"])
        self.assertIn("error_message", result)
        payload = json.loads((self.recordings_dir / result["frames_dir"] / "frames_index.json").read_text(encoding="utf-8"))
        self.assertEqual("failed", payload["status"])


if __name__ == "__main__":
    unittest.main()
