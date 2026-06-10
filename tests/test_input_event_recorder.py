import json
import unittest
from pathlib import Path
from tempfile import mkdtemp

from app.input_event_recorder import InputEventRecorder


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class FakeListener:
    def __init__(self, **_callbacks):
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def join(self, timeout=None):
        return None


class FailingListener:
    def __init__(self, **_callbacks):
        pass

    def start(self):
        raise RuntimeError("listener blocked by security policy\nwith noisy details")

    def stop(self):
        return None


class InputEventRecorderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.recordings_dir = Path(mkdtemp(dir=PROJECT_TMP))
        self.screens = [
            {"index": 1, "width": 100, "height": 100, "left": 0, "top": 0},
            {"index": 2, "width": 100, "height": 100, "left": -100, "top": 0},
        ]

    def test_mouse_position_down_up_and_scroll_jsonl_schema(self) -> None:
        recorder = self.create_recorder(record_mouse=True)
        metadata = recorder.start(started_at=10.0)
        recorder.record_mouse_position(20, 30, t=0.2)
        recorder.handle_mouse_click(22, 31, "left", True)
        recorder.handle_mouse_click(24, 35, "left", False)
        recorder.handle_mouse_scroll(24, 35, 0, -3)
        recorder.stop()

        self.assertEqual("mouse_events_20260610_143000.jsonl", metadata["events"]["mouse"])
        events = self.read_jsonl("mouse_events_20260610_143000.jsonl")
        self.assertEqual(
            {
                "t": 0.2,
                "type": "position",
                "x": 20,
                "y": 30,
                "screen_index": 1,
                "screen_status": "recorded_screen",
            },
            events[0],
        )
        self.assertEqual("down", events[1]["type"])
        self.assertEqual("left", events[1]["button"])
        self.assertEqual("up", events[2]["type"])
        self.assertEqual({"dx": 0, "dy": -3}, {"dx": events[3]["dx"], "dy": events[3]["dy"]})

    def test_mouse_outside_recorded_screens_uses_null_screen_index(self) -> None:
        recorder = self.create_recorder(record_mouse=True)
        recorder.start(started_at=10.0)
        recorder.record_mouse_position(250, 30, t=1.0)
        recorder.stop()

        event = self.read_jsonl("mouse_events_20260610_143000.jsonl")[0]
        self.assertIsNone(event["screen_index"])
        self.assertEqual("outside_recorded_screens", event["screen_status"])

    def test_keyboard_special_key_and_ctrl_letter_hotkey_are_logged(self) -> None:
        recorder = self.create_recorder(record_keyboard=True)
        recorder.start(started_at=10.0)
        recorder.handle_key_press("enter")
        recorder.handle_key_release("enter")
        recorder.handle_key_press("ctrl_l")
        recorder.handle_key_press("c")
        recorder.handle_key_release("c")
        recorder.handle_key_release("ctrl_l")
        recorder.stop()

        events = self.read_jsonl("keyboard_events_20260610_143000.jsonl")
        self.assertEqual("key_down", events[0]["type"])
        self.assertEqual("Enter", events[0]["key"])
        self.assertEqual("key_up", events[1]["type"])
        self.assertEqual("Enter", events[1]["key"])
        self.assertIn({"t": 0.0, "type": "hotkey", "keys": ["Ctrl", "C"]}, events)

    def test_keyboard_plain_typed_letter_is_not_logged(self) -> None:
        recorder = self.create_recorder(record_keyboard=True)
        recorder.start(started_at=10.0)
        recorder.handle_key_press("a")
        recorder.handle_key_release("a")
        recorder.stop()

        self.assertEqual([], self.read_jsonl("keyboard_events_20260610_143000.jsonl"))

    def test_listener_failure_sets_failed_status_and_writes_diagnostic(self) -> None:
        recorder = InputEventRecorder(
            recordings_dir=self.recordings_dir,
            timestamp="20260610_143000",
            screens=self.screens,
            fps=5,
            record_keyboard=True,
            keyboard_listener_factory=FailingListener,
        )
        metadata = recorder.start(started_at=10.0)
        recorder.stop()

        event_logging = metadata["event_logging"]
        self.assertEqual("failed", event_logging["keyboard_status"])
        self.assertIn("listener blocked by security policy", event_logging["keyboard_error"])
        self.assertNotIn("\n", event_logging["keyboard_error"])
        events = self.read_jsonl("keyboard_events_20260610_143000.jsonl")
        self.assertEqual("diagnostic", events[0]["type"])
        self.assertEqual("failed", events[0]["status"])

    def create_recorder(self, *, record_mouse: bool = False, record_keyboard: bool = False) -> InputEventRecorder:
        return InputEventRecorder(
            recordings_dir=self.recordings_dir,
            timestamp="20260610_143000",
            screens=self.screens,
            fps=5,
            record_mouse=record_mouse,
            record_keyboard=record_keyboard,
            mouse_listener_factory=FakeListener,
            keyboard_listener_factory=FakeListener,
            mouse_position_provider=lambda: (20, 30),
            start_mouse_sampler=False,
            time_fn=lambda: 10.0,
        )

    def read_jsonl(self, filename: str) -> list[dict]:
        path = self.recordings_dir / filename
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
