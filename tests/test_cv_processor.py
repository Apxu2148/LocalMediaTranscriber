import json
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from app import cv_processor


try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


@unittest.skipUnless(Image is not None, "Pillow is required for CV metadata processor tests")
class CvProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = PROJECT_TMP / f"cv_processor_{uuid4().hex}"
        self.frames_dir = self.root / "frames"
        self.output_dir = self.root / "cv"
        self.frames_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def make_frame(self, name: str, color: tuple[int, int, int]) -> Path:
        path = self.frames_dir / name
        Image.new("RGB", (8, 8), color).save(path, format="JPEG")
        return path

    def read_jsonl(self) -> list[dict]:
        path = self.output_dir / "frames_cv.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_cv_processor_writes_jsonl_and_txt_with_expected_keys(self) -> None:
        self.make_frame("frame_000001__t000000.000.jpg", (20, 20, 20))
        self.make_frame("frame_000002__t000005.250.jpg", (21, 21, 21))

        result = cv_processor.analyze_frames(frames_dir=self.frames_dir, output_dir=self.output_dir)
        records = self.read_jsonl()
        summary = (self.output_dir / "frames_cv.txt").read_text(encoding="utf-8")

        self.assertEqual("completed", result["status"])
        self.assertTrue((self.output_dir / "frames_cv.jsonl").exists())
        self.assertTrue((self.output_dir / "frames_cv.txt").exists())
        self.assertEqual(2, len(records))
        self.assertEqual(
            {
                "frame_index",
                "frame_file",
                "timestamp_sec",
                "width",
                "height",
                "brightness",
                "contrast",
                "blur_score",
                "visual_hash",
                "diff_score_vs_previous",
                "near_duplicate",
                "scene_change",
            },
            set(records[0]),
        )
        self.assertIn("CV metadata summary", summary)
        self.assertIn("Frames analyzed: 2", summary)

    def test_first_frame_and_near_duplicate_behavior_are_stable(self) -> None:
        self.make_frame("frame_000001__t000000.000.jpg", (40, 40, 40))
        self.make_frame("frame_000002__t000001.000.jpg", (40, 40, 40))

        cv_processor.analyze_frames(frames_dir=self.frames_dir, output_dir=self.output_dir)
        first, second = self.read_jsonl()

        self.assertIsNone(first["diff_score_vs_previous"])
        self.assertFalse(first["near_duplicate"])
        self.assertTrue(first["scene_change"])
        self.assertEqual(1.0, second["timestamp_sec"])
        self.assertLess(second["diff_score_vs_previous"], cv_processor.NEAR_DUPLICATE_DIFF_THRESHOLD)
        self.assertTrue(second["near_duplicate"])
        self.assertFalse(second["scene_change"])

    def test_different_frame_produces_higher_diff_and_scene_change(self) -> None:
        self.make_frame("frame_000001__t000000.000.jpg", (0, 0, 0))
        self.make_frame("frame_000002__t000002.000.jpg", (255, 255, 255))

        cv_processor.analyze_frames(frames_dir=self.frames_dir, output_dir=self.output_dir)
        records = self.read_jsonl()

        self.assertGreater(records[1]["diff_score_vs_previous"], cv_processor.SCENE_CHANGE_DIFF_THRESHOLD)
        self.assertFalse(records[1]["near_duplicate"])
        self.assertTrue(records[1]["scene_change"])

    def test_empty_frames_directory_returns_empty_result_and_summary(self) -> None:
        result = cv_processor.analyze_frames(frames_dir=self.frames_dir, output_dir=self.output_dir)
        summary = (self.output_dir / "frames_cv.txt").read_text(encoding="utf-8")

        self.assertEqual("empty", result["status"])
        self.assertEqual(0, result["frames_analyzed"])
        self.assertEqual([], self.read_jsonl())
        self.assertIn("Frames analyzed: 0", summary)

    def test_invalid_frame_is_reported_without_crashing_processor(self) -> None:
        self.make_frame("frame_000001__t000000.000.jpg", (10, 10, 10))
        (self.frames_dir / "frame_000002__t000001.000.jpg").write_text("not an image", encoding="utf-8")
        self.make_frame("frame_000003__t000002.000.jpg", (200, 200, 200))

        result = cv_processor.analyze_frames(frames_dir=self.frames_dir, output_dir=self.output_dir)
        records = self.read_jsonl()

        self.assertEqual("completed", result["status"])
        self.assertEqual(2, result["frames_analyzed"])
        self.assertEqual(1, result["frames_skipped"])
        self.assertEqual(1, len(result["frame_errors"]))
        self.assertEqual(["frame_000001__t000000.000.jpg", "frame_000003__t000002.000.jpg"], [record["frame_file"] for record in records])


if __name__ == "__main__":
    unittest.main()
