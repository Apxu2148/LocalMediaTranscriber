import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from app.transcriber import AudioTranscriber


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class TranscriberCancellationTests(unittest.TestCase):
    def test_cancel_callback_stops_between_segments_and_returns_partial_result(self) -> None:
        source_path = PROJECT_TMP / f"codex_transcriber_cancel_{uuid4().hex}.wav"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(b"audio")
        transcriber = AudioTranscriber()
        segments = [
            SimpleNamespace(start=0.0, end=1.0, text=" first "),
            SimpleNamespace(start=1.0, end=2.0, text=" second "),
        ]
        fake_model = SimpleNamespace(transcribe=lambda *_args, **_kwargs: (iter(segments), object()))
        checks = {"count": 0}

        def should_cancel() -> bool:
            checks["count"] += 1
            return checks["count"] >= 2

        try:
            with (
                patch.object(transcriber, "_check_ffmpeg"),
                patch.object(transcriber, "_get_model", return_value=fake_model),
                patch("app.transcriber.audio_duration_seconds", return_value=10.0),
            ):
                result = transcriber.transcribe(source_path, "small", "cpu", should_cancel=should_cancel)
        finally:
            source_path.unlink(missing_ok=True)

        self.assertTrue(result.cancelled)
        self.assertTrue(result.partial)
        self.assertEqual("Транскрибация отменена пользователем.", result.cancellation_reason)
        self.assertEqual(1, len(result.segments))
        self.assertIn("first", result.text)
        self.assertNotIn("second", result.text)


if __name__ == "__main__":
    unittest.main()
