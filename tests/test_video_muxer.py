import unittest
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from app.video_muxer import VideoMuxer, VideoMuxerDependencyError, VideoMuxerValidationError


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class VideoMuxerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.recordings_dir = Path(mkdtemp(dir=PROJECT_TMP))
        self.video_path = self.recordings_dir / "screen1_20260609_001122__30fps.mp4"
        self.mic_path = self.recordings_dir / "mic_20260609_001122.wav"
        self.system_path = self.recordings_dir / "system_20260609_001122.wav"
        for path in (self.video_path, self.mic_path, self.system_path):
            path.write_bytes(b"test")
        self.muxer = VideoMuxer(recordings_dir=self.recordings_dir)

    def test_builds_command_for_one_audio_file(self) -> None:
        output_path = self.recordings_dir / "merged.mp4"
        command = self.muxer.build_ffmpeg_command("ffmpeg", self.video_path, [self.mic_path], output_path)
        self.assertEqual("ffmpeg", command[0])
        self.assertIn("-map", command)
        self.assertIn("1:a:0", command)
        self.assertIn("-c:v", command)
        self.assertIn("copy", command)
        self.assertNotIn("-filter_complex", command)
        self.assertEqual(str(output_path), command[-1])

    def test_builds_command_for_two_audio_files(self) -> None:
        output_path = self.recordings_dir / "merged.mp4"
        command = self.muxer.build_ffmpeg_command(
            "ffmpeg",
            self.video_path,
            [self.mic_path, self.system_path],
            output_path,
        )
        self.assertIn("-filter_complex", command)
        self.assertIn("[1:a][2:a]amix=inputs=2:duration=longest:normalize=0[a]", command)
        self.assertIn("[a]", command)
        self.assertEqual(str(output_path), command[-1])

    def test_requires_at_least_one_audio_file(self) -> None:
        with self.assertRaises(VideoMuxerValidationError):
            self.muxer.resolve_audio_files(None, None)

    def test_rejects_unsafe_or_wrong_suffix_paths(self) -> None:
        with self.assertRaises(VideoMuxerValidationError):
            self.muxer.resolve_recording_file("..\\outside.mp4", {".mp4"})
        with self.assertRaises(VideoMuxerValidationError):
            self.muxer.resolve_recording_file("session_20260609_001122.json", {".mp4"})

    def test_ffmpeg_missing_is_reported_before_execution(self) -> None:
        with patch("app.video_muxer.shutil.which", return_value=None):
            with self.assertRaises(VideoMuxerDependencyError):
                self.muxer.merge(
                    video_file=self.video_path.name,
                    mic_audio_file=self.mic_path.name,
                )


if __name__ == "__main__":
    unittest.main()
