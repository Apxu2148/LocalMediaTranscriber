import json
import re
import unittest
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.screen_recorder import (
    ALLOWED_SCREEN_FPS,
    ScreenRecorder,
    ScreenRecorderValidationError,
    TIMING_MODE_DUPLICATE_FRAMES,
    build_timing_diagnostics,
    create_session_id,
    normalize_display_indices,
    normalize_screen_fps,
    recent_media_sessions,
    screen_video_filename,
    select_displays,
    sort_displays_for_layout,
)

from app import main as main_module


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class ScreenRecorderTests(unittest.TestCase):
    def test_fps_and_display_selection_validation(self) -> None:
        self.assertEqual(3, normalize_screen_fps(None))
        for fps in ALLOWED_SCREEN_FPS:
            self.assertEqual(fps, normalize_screen_fps(str(fps)))
        with self.assertRaises(ScreenRecorderValidationError):
            normalize_screen_fps(60)
        with self.assertRaises(ScreenRecorderValidationError):
            normalize_display_indices([])
        self.assertEqual([1, 2], normalize_display_indices([1, "2", 2]))

        displays = [
            {"index": 1, "name": "Display 1", "width": 1920, "height": 1080, "left": 0, "top": 0},
            {"index": 2, "name": "Display 2", "width": 1280, "height": 720, "left": 1920, "top": 0},
        ]
        self.assertEqual([2], [item["index"] for item in select_displays(displays, [2])])
        with self.assertRaises(ScreenRecorderValidationError):
            select_displays(displays, [3])

    def test_flat_session_json_creation(self) -> None:
        display = {"index": 1, "name": "Display 1", "width": 1920, "height": 1080, "left": 0, "top": 0}
        recordings_dir = Path(mkdtemp(dir=PROJECT_TMP))
        recorder = ScreenRecorder(recordings_dir=recordings_dir)
        session_id, session_dir, session = recorder.create_session(
            [display],
            5,
            source_flags={"mic": True, "system": False},
            timestamp="20260609_001122",
            audio_files={"mic": "mic_20260609_001122.wav", "system": None},
        )

        self.assertEqual("session_20260609_001122", session_id)
        self.assertEqual(recordings_dir, session_dir)
        self.assertTrue((recordings_dir / "session_20260609_001122.json").is_file())
        self.assertFalse((recordings_dir / session_id / "screens").exists())
        payload = json.loads((recordings_dir / "session_20260609_001122.json").read_text(encoding="utf-8"))
        self.assertEqual("recording", payload["status"])
        self.assertTrue(payload["sources"]["mic"])
        self.assertTrue(payload["sources"]["screens"])
        self.assertTrue(payload["recordings_dir"].replace("\\", "/").endswith(recordings_dir.name))
        self.assertEqual("mic_20260609_001122.wav", payload["audio"]["mic"])
        self.assertEqual("screen1_20260609_001122__5fps.mp4", payload["screens"][0]["video_file"])
        self.assertEqual("screen1_20260609_001122__5fps.mp4", payload["screens"][0]["video_path"])
        self.assertEqual(5, payload["screens"][0]["requested_fps"])
        self.assertEqual(5, payload["screens"][0]["written_fps"])
        self.assertEqual(session, payload)

    def test_recent_media_sessions_reads_summaries(self) -> None:
        display = {"index": 1, "name": "Display 1", "width": 1920, "height": 1080, "left": 0, "top": 0}
        root = Path(mkdtemp(dir=PROJECT_TMP))
        recorder = ScreenRecorder(recordings_dir=root)
        session_id, _, _ = recorder.create_session([display], 3, timestamp="20260609_003000")
        sessions = recent_media_sessions(root)
        self.assertEqual(session_id, sessions[0]["session_id"])
        self.assertEqual("recording", sessions[0]["status"])
        self.assertEqual(str(root / "session_20260609_003000.json"), sessions[0]["session_json"])

    def test_filename_and_timing_diagnostics(self) -> None:
        self.assertEqual(
            "screen2_20260609_001122__30fps.mp4",
            screen_video_filename(2, "20260609_001122", 30),
        )
        diagnostics = build_timing_diagnostics(
            requested_fps=30,
            duration_seconds=60,
            captured_frame_count=900,
            written_frame_count=1800,
            duplicated_frame_count=900,
        )
        self.assertEqual(30, diagnostics["requested_fps"])
        self.assertEqual(30, diagnostics["written_fps"])
        self.assertEqual(15.0, diagnostics["actual_capture_fps"])
        self.assertEqual(0.5, diagnostics["duplicate_ratio"])
        self.assertTrue(diagnostics["timing_warning"])
        self.assertEqual(TIMING_MODE_DUPLICATE_FRAMES, diagnostics["timing_mode"])

    def test_display_layout_sort_uses_virtual_desktop_coordinates(self) -> None:
        displays = [
            {"index": 2, "width": 1920, "height": 1080, "left": 0, "top": 0},
            {"index": 1, "width": 1920, "height": 1080, "left": -1920, "top": 0},
            {"index": 3, "width": 1280, "height": 720, "left": 0, "top": 1080},
        ]
        self.assertEqual([1, 2, 3], [display["index"] for display in sort_displays_for_layout(displays)])

    def test_screen_recording_api_validation_and_delegation(self) -> None:
        with TestClient(main_module.app) as client:
            empty_response = client.post("/api/screen-recording/start", json={"display_indices": [], "fps": 3})
            self.assertEqual(400, empty_response.status_code)

            fps_response = client.post("/api/screen-recording/start", json={"display_indices": [1], "fps": 60})
            self.assertEqual(400, fps_response.status_code)

        with (
            patch.object(
                main_module.screen_recorder,
                "start",
                return_value={"session_id": "session_20260609_003000", "recordings_dir": "data/recordings"},
            ) as start,
            TestClient(main_module.app) as client,
        ):
            response = client.post("/api/screen-recording/start", json={"display_indices": [1, 2], "fps": 5})
            self.assertEqual(200, response.status_code)
            start.assert_called_once_with([1, 2], 5)

    def test_displays_and_preview_api_contract(self) -> None:
        displays = [
            {"index": 1, "name": "Display 1", "width": 1920, "height": 1080, "left": -1920, "top": 0},
            {"index": 2, "name": "Display 2", "width": 1920, "height": 1080, "left": 0, "top": 0},
        ]
        preview = {
            "screen_index": 1,
            "mime_type": "image/jpeg",
            "image_base64": "abc",
            "image_data_url": "data:image/jpeg;base64,abc",
            "width": 320,
            "height": 180,
        }
        with (
            patch.object(main_module.screen_recorder, "list_displays", return_value=displays),
            patch.object(main_module.screen_recorder, "capture_display_preview", return_value=preview) as capture_preview,
            TestClient(main_module.app) as client,
        ):
            display_response = client.get("/api/displays")
            self.assertEqual(200, display_response.status_code)
            self.assertEqual(-1920, display_response.json()[0]["left"])

            preview_response = client.post("/api/displays/preview", json={"screen_index": 1, "max_width": 320})
            self.assertEqual(200, preview_response.status_code)
            self.assertEqual("data:image/jpeg;base64,abc", preview_response.json()["image_data_url"])
            capture_preview.assert_called_once_with(1, 320)

        with (
            patch.object(
                main_module.screen_recorder,
                "capture_display_preview",
                side_effect=ScreenRecorderValidationError("invalid display"),
            ),
            TestClient(main_module.app) as client,
        ):
            response = client.post("/api/displays/preview", json={"screen_index": 99})
            self.assertEqual(400, response.status_code)
            self.assertEqual("invalid display", response.json()["detail"]["message"])


class ScreenRecorderIdTests(unittest.TestCase):
    def test_session_id_format(self) -> None:
        self.assertIsNotNone(re.match(r"^session_\d{8}_\d{6}$", create_session_id()))


if __name__ == "__main__":
    unittest.main()
