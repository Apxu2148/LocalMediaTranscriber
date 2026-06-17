import sys
import shutil
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from app.url_downloader import UrlDownloader, get_direct_media_url_extension, is_direct_media_url


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class FakeYoutubeDL:
    last_options = None

    def __init__(self, options: dict) -> None:
        self.options = options
        FakeYoutubeDL.last_options = options
        self.ext = options.get("merge_output_format") or "m4a"
        self.path = Path(options["outtmpl"].replace("%(ext)s", self.ext))

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def extract_info(self, _url: str, download: bool) -> dict:
        self.path.write_bytes(b"media")
        return {"title": "Public lesson", "extractor_key": "Youtube", "duration": 12, "ext": self.ext}

    def prepare_filename(self, _info: dict) -> str:
        return str(self.path)


class CookieErrorYoutubeDL(FakeYoutubeDL):
    def extract_info(self, _url: str, download: bool) -> dict:
        raise RuntimeError("Sign in to confirm your age. Use cookies for authentication.")


class FakeHttpResponse:
    def __init__(self, chunks: list[bytes], *, status: int = 200) -> None:
        self.chunks = list(chunks)
        self.status = status
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def getcode(self) -> int:
        return self.status

    def read(self, _size: int) -> bytes:
        if not self.chunks:
            return b""
        return self.chunks.pop(0)


class UrlDownloaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prefix = f"codex_url_downloader_{uuid4().hex}"
        self.root = PROJECT_TMP / self.prefix
        self.root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_direct_media_url_detection_uses_path_extension_and_ignores_query(self) -> None:
        for extension in (".mp4", ".webm", ".mkv", ".avi", ".mov"):
            self.assertEqual(extension, get_direct_media_url_extension(f"https://example.test/video{extension}?token=abc"))
            self.assertTrue(is_direct_media_url(f"https://example.test/video{extension}"))
        self.assertIsNone(get_direct_media_url_extension("https://example.test/watch?v=clip.mp4"))
        self.assertIsNone(get_direct_media_url_extension("https://example.test/page"))

    def test_download_uses_audio_only_options_and_returns_metadata(self) -> None:
        fake_module = types.SimpleNamespace(YoutubeDL=FakeYoutubeDL)
        downloader = UrlDownloader(self.root)
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with patch("app.url_downloader.timestamp_for_filename", return_value=self.prefix):
                result = downloader.download("https://example.test/public-video")

        self.assertEqual("Public lesson", result["source_title"])
        self.assertEqual("youtube", result["source_platform"])
        self.assertTrue(Path(result["source_path"]).exists())
        self.assertEqual("m4a/bestaudio/best", FakeYoutubeDL.last_options["format"])
        self.assertTrue(FakeYoutubeDL.last_options["noplaylist"])
        self.assertEqual("m4a", FakeYoutubeDL.last_options["postprocessors"][0]["preferredcodec"])

    def test_download_video_uses_video_options_and_returns_media_metadata(self) -> None:
        fake_module = types.SimpleNamespace(YoutubeDL=FakeYoutubeDL)
        downloader = UrlDownloader(self.root)
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with patch("app.url_downloader.timestamp_for_filename", return_value=self.prefix):
                result = downloader.download_video("https://example.test/public-video")

        self.assertEqual("Public lesson", result["source_title"])
        self.assertEqual("youtube", result["source_platform"])
        self.assertTrue(Path(result["source_path"]).exists())
        self.assertEqual("bv*+ba/bestvideo+bestaudio/best", FakeYoutubeDL.last_options["format"])
        self.assertEqual("mkv", FakeYoutubeDL.last_options["merge_output_format"])
        self.assertEqual(result["source_path"], result["downloaded_media_path"])
        self.assertEqual(result["source_path"], result["downloaded_video_path"])

    def test_direct_video_download_bypasses_ytdlp_and_writes_downloaded_media(self) -> None:
        calls: list[tuple[str, int]] = []

        def fake_urlopen(request, timeout: int):
            calls.append((request.full_url, timeout))
            return FakeHttpResponse([b"video-", b"bytes"])

        fake_module = types.SimpleNamespace(YoutubeDL=lambda _options: self.fail("yt-dlp should not be used"))
        downloader = UrlDownloader(self.root)
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with patch("app.url_downloader.urlopen", side_effect=fake_urlopen):
                result = downloader.download_video("https://example.test/files/file_example_MP4_1280_10MG.mp4?token=abc")

        source_path = Path(result["source_path"])
        self.assertEqual([("https://example.test/files/file_example_MP4_1280_10MG.mp4?token=abc", 30)], calls)
        self.assertEqual(b"video-bytes", source_path.read_bytes())
        self.assertEqual("file_example_MP4_1280_10MG.mp4", source_path.name)
        self.assertEqual("direct", result["source_platform"])
        self.assertEqual(result["source_path"], result["downloaded_media_path"])
        self.assertEqual(result["source_path"], result["downloaded_video_path"])

    def test_direct_video_audio_only_download_also_bypasses_ytdlp(self) -> None:
        fake_module = types.SimpleNamespace(YoutubeDL=lambda _options: self.fail("yt-dlp should not be used"))
        downloader = UrlDownloader(self.root)
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with patch("app.url_downloader.urlopen", return_value=FakeHttpResponse([b"mp4"])):
                result = downloader.download("https://example.test/audio-source.mp4")

        self.assertEqual("direct", result["source_platform"])
        self.assertTrue(Path(result["source_path"]).exists())
        self.assertEqual(result["source_path"], result["downloaded_media_path"])

    def test_direct_download_timeout_uses_readable_message_and_technical_details(self) -> None:
        downloader = UrlDownloader(self.root)
        with patch("app.url_downloader.urlopen", side_effect=TimeoutError("timed out")):
            with self.assertRaisesRegex(RuntimeError, "таймаут") as raised:
                downloader.download_video("https://example.test/clip.mp4")

        self.assertEqual("timed out", raised.exception.technical_details)
        self.assertNotIn("Р ", str(raised.exception))

    def test_cookie_or_auth_download_error_uses_readable_message(self) -> None:
        fake_module = types.SimpleNamespace(YoutubeDL=CookieErrorYoutubeDL)
        downloader = UrlDownloader(self.root)
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with self.assertRaisesRegex(RuntimeError, "cookies") as raised:
                downloader.download_video("https://example.test/private-video")

        self.assertIn("Sign in", raised.exception.technical_details)
        self.assertNotIn("Р ", str(raised.exception))

    def test_rejects_non_http_url(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "HTTP"):
            UrlDownloader(self.root).download("file:///private/audio.wav")


if __name__ == "__main__":
    unittest.main()
