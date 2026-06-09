import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app import config
from app import utils as utils_module


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_TMP = PROJECT_ROOT / "tmp"
PROJECT_TMP.mkdir(parents=True, exist_ok=True)
config.JOBS_DIR = PROJECT_TMP

with patch.object(utils_module, "setup_logging"):
    from app import main as main_module  # noqa: E402


class FileListingTests(unittest.TestCase):
    def test_recording_suffixes_match_user_facing_media_contract(self) -> None:
        self.assertEqual(
            {".wav", ".mp3", ".m4a", ".mp4", ".avi", ".mkv", ".webm", ".flac", ".ogg"},
            main_module.RECORDING_FILE_SUFFIXES,
        )
        for hidden_suffix in (".json", ".log", ".tmp", ".pyc"):
            self.assertNotIn(hidden_suffix, main_module.RECORDING_FILE_SUFFIXES)

    def test_recent_recordings_filter_includes_media_and_hides_service_files(self) -> None:
        root = PROJECT_TMP / "test_file_listing_media"
        root.mkdir(parents=True, exist_ok=True)
        media_names = [
            "mic_20260609_001122.wav",
            "music_20260609_001122.mp3",
            "voice_20260609_001122.m4a",
            "screen1_20260609_001122.mp4",
            "screen2_20260609_001122.avi",
            "merged_20260609_001122.mkv",
            "capture_20260609_001122.webm",
            "audio_20260609_001122.flac",
            "audio_20260609_001122.ogg",
        ]
        service_names = [
            "session_20260609_001122.json",
            "debug.log",
            "temp.tmp",
            "module.pyc",
        ]

        for index, name in enumerate(media_names + service_names):
            path = root / name
            path.write_bytes(b"media")
            os.utime(path, (index + 1, index + 1))

        files = main_module.recent_files(
            root,
            limit=20,
            allowed_suffixes=main_module.RECORDING_FILE_SUFFIXES,
        )
        listed_names = {file["name"] for file in files}

        for name in media_names:
            self.assertIn(name, listed_names)
        for name in service_names:
            self.assertNotIn(name, listed_names)


if __name__ == "__main__":
    unittest.main()
