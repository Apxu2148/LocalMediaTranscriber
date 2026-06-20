import json
import shutil
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from app.queue_manager import QueueFile, QueueManager, QueueUrl
from app.storage_manager import StorageManager
from app.url_downloader import UrlDownloadCancelled, UrlDownloader


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"


class FakeHttpResponse:
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = list(chunks)
        self.status = 200
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


class QueueManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prefix = f"codex_queue_manager_{uuid4().hex}"
        self.root = PROJECT_TMP / self.prefix
        self.root.mkdir(parents=True, exist_ok=True)
        self.managers: list[QueueManager] = []
        self.timestamp_patch = patch("app.queue_manager.timestamp_for_filename", return_value=self.prefix)
        self.timestamp_patch.start()

    def tearDown(self) -> None:
        for manager in self.managers:
            manager.wait(timeout=1)
        self.timestamp_patch.stop()
        shutil.rmtree(self.root, ignore_errors=True)

    def make_file(self, name: str) -> QueueFile:
        path = self.root / name
        path.write_bytes(b"test")
        return QueueFile(source_path=path, source_filename=name)

    def make_manager(self, **kwargs) -> QueueManager:
        manager = QueueManager(jobs_dir=self.root, **kwargs)
        self.managers.append(manager)
        return manager

    def track_job(self, status: dict) -> dict:
        return status

    def test_processes_files_sequentially_and_persists_job_json(self) -> None:
        processed: list[str] = []

        def processor(item: dict, _model: str, _device: str) -> dict:
            processed.append(item["source_filename"])
            return {
                "audio_duration_sec": 10,
                "processing_time_sec": 2,
                "realtime_factor": 5,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        manager = self.make_manager(
            processor=processor,
            duration_reader=lambda _path: 10,
        )
        status = self.track_job(manager.add_files([self.make_file("one.wav"), self.make_file("two.wav")]))
        job_path = Path(status["job_path"])
        manager.start("small", "cpu")
        manager.wait(timeout=3)
        self.assertFalse(manager.is_running)

        status = manager.status()
        self.assertEqual(["one.wav", "two.wav"], processed)
        self.assertEqual("completed", status["status"])
        self.assertEqual(2, status["completed_items"])
        self.assertEqual(100, status["progress_percent"])
        self.assertTrue(job_path.exists())
        payload = json.loads(job_path.read_text(encoding="utf-8"))
        self.assertEqual("completed", payload["status"])
        self.assertEqual(["completed", "completed"], [item["status"] for item in payload["items"]])
        self.assertEqual("cpu", payload["device_preference"])

    def test_continues_after_error_and_retries_failed_items(self) -> None:
        attempts: list[str] = []
        should_fail = {"bad.wav"}

        def processor(item: dict, _model: str, _device: str) -> dict:
            attempts.append(item["source_filename"])
            if item["source_filename"] in should_fail:
                raise RuntimeError("expected failure")
            return {
                "audio_duration_sec": 4,
                "processing_time_sec": 1,
                "realtime_factor": 4,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        manager = self.make_manager(
            processor=processor,
            error_recorder=lambda item, _model, _device, _exc: {"json_path": f"{item['source_path']}.error.json"},
            duration_reader=lambda _path: 4,
        )
        self.track_job(manager.add_files([self.make_file("bad.wav"), self.make_file("good.wav")]))
        manager.start("small")
        manager.wait(timeout=3)
        self.assertFalse(manager.is_running)

        status = manager.status()
        self.assertEqual(["bad.wav", "good.wav"], attempts)
        self.assertEqual(1, status["failed_items"])
        self.assertEqual(1, status["completed_items"])
        self.assertTrue(status["items"][0]["json_path"].endswith(".error.json"))

        should_fail.clear()
        manager.retry_errors()
        manager.start("small")
        manager.wait(timeout=3)
        self.assertFalse(manager.is_running)
        status = manager.status()
        self.assertEqual("completed", status["status"])
        self.assertEqual(2, status["completed_items"])
        self.assertEqual(0, status["failed_items"])

    def test_stop_after_current_cancels_pending_items(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def processor(item: dict, _model: str, _device: str) -> dict:
            started.set()
            release.wait(timeout=3)
            return {
                "audio_duration_sec": 1,
                "processing_time_sec": 1,
                "realtime_factor": 1,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        manager = self.make_manager(
            processor=processor,
            duration_reader=lambda _path: 1,
        )
        self.track_job(manager.add_files([self.make_file("one.wav"), self.make_file("two.wav")]))
        manager.start("small")
        self.assertTrue(started.wait(timeout=2))
        manager.stop_after_current()
        release.set()
        manager.wait(timeout=3)
        self.assertFalse(manager.is_running)

        status = manager.status()
        self.assertEqual("cancelled", status["status"])
        self.assertEqual(["completed", "cancelled"], [item["status"] for item in status["items"]])

    def test_running_audio_transcription_can_be_cancelled_and_queue_continues(self) -> None:
        started = threading.Event()
        cancel_seen = threading.Event()
        allow_cancelled_result = threading.Event()
        processed: list[str] = []

        def processor(item: dict, _model: str, _device: str, cancel_event: threading.Event) -> dict:
            processed.append(item["source_filename"])
            if item["source_filename"] == "long.wav":
                started.set()
                while not cancel_event.is_set():
                    time.sleep(0.01)
                cancel_seen.set()
                allow_cancelled_result.wait(timeout=3)
                partial_txt = self.root / "long__partial_cancelled.txt"
                partial_json = self.root / "long__partial_cancelled.json"
                partial_txt.write_text("partial", encoding="utf-8")
                partial_json.write_text("{}", encoding="utf-8")
                return {
                    "status": "cancelled",
                    "partial": True,
                    "audio_duration_sec": 10,
                    "processing_time_sec": 1,
                    "transcript_path": str(partial_txt),
                    "json_path": str(partial_json),
                    "cancellation_reason": "Транскрибация отменена пользователем.",
                }
            return {
                "audio_duration_sec": 1,
                "processing_time_sec": 1,
                "realtime_factor": 1,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        manager = self.make_manager(
            processor=processor,
            duration_reader=lambda _path: 1,
        )
        self.track_job(manager.add_files([self.make_file("long.wav"), self.make_file("next.wav")]))
        manager.start("small", "cpu")
        self.assertTrue(started.wait(timeout=2))

        snapshot = manager.status()
        self.assertEqual("transcribing_audio", snapshot["current_stage"])
        cancelled_snapshot = manager.cancel_item(1)
        self.assertEqual("cancelling_transcription", cancelled_snapshot["current_stage"])
        self.assertTrue(cancelled_snapshot["current_item"]["cancel_requested"])
        self.assertTrue(cancel_seen.wait(timeout=2))
        allow_cancelled_result.set()
        manager.wait(timeout=3)

        status = manager.status()
        self.assertFalse(manager.is_running)
        self.assertEqual("completed", status["status"])
        self.assertEqual(["long.wav", "next.wav"], processed)
        self.assertEqual(["cancelled", "completed"], [item["status"] for item in status["items"]])
        self.assertEqual(1, status["cancelled_items"])
        self.assertEqual(1, status["completed_items"])
        first = status["items"][0]
        self.assertEqual("cancelled", first["stage"])
        self.assertTrue(first["partial_transcript"])
        self.assertIn("partial_cancelled", first["transcript_path"])
        self.assertTrue(first["outputs"]["transcript_partial"])

    def test_clear_removes_in_memory_queue_but_keeps_job_json(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})
        status = self.track_job(manager.add_files([self.make_file("one.wav")]))
        job_path = Path(status["job_path"])
        manager.clear()

        self.assertTrue(job_path.exists())
        self.assertEqual("empty", manager.status()["status"])
        self.assertEqual([], manager.status()["items"])

    def test_mixed_queue_downloads_url_and_reuses_snapshot(self) -> None:
        downloaded = self.make_file("downloaded.m4a")
        calls: list[tuple[str, str, str]] = []

        def processor(item: dict, model: str, device: str) -> dict:
            calls.append((item["source_type"], model, device))
            return {
                "audio_duration_sec": 2,
                "processing_time_sec": 1,
                "realtime_factor": 2,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        manager = self.make_manager(
            processor=processor,
            downloader=lambda _url: {
                "source_path": str(downloaded.source_path),
                "source_title": "Public lesson",
                "source_platform": "youtube",
                "audio_duration_sec": 2,
            },
            duration_reader=lambda _path: 2,
        )
        self.track_job(manager.add_files([self.make_file("local.wav")]))
        manager.add_urls([QueueUrl("https://example.test/video")])
        manager.start("base", "cuda")
        manager.wait(timeout=3)
        self.assertFalse(manager.is_running)

        status = manager.status()
        self.assertEqual([("local_file", "small", "auto"), ("url", "small", "auto")], calls)
        self.assertEqual("youtube", status["items"][1]["source_platform"])
        self.assertEqual(str(downloaded.source_path), status["items"][1]["downloaded_audio_path"])

    def test_url_item_defaults_to_media_processing_options(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})

        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        item = status["items"][0]

        self.assertEqual("url", item["source_type"])
        self.assertEqual("url", item["media_kind"])
        self.assertEqual("waiting_download", item["stage"])
        self.assertEqual("queueStageWaitingDownload", item["stage_label_key"])
        self.assertTrue(item["operations"]["transcribe_audio"])
        self.assertFalse(item["operations"]["extract_frames"])
        self.assertFalse(item["operations"]["ocr"])
        self.assertFalse(item["operations"]["cv"])
        self.assertEqual({"mode": "interval", "seconds": 10}, item["frame_extraction"]["rate"])
        self.assertEqual(90, item["frame_extraction"]["jpeg_quality"])
        self.assertEqual("auto", item["processing_plan"]["url_download"]["format_profile"])

    def test_new_item_receives_processing_plan_snapshot(self) -> None:
        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_metadata_reader=lambda _path: {"duration_sec": 90, "fps": 30, "width": 320, "height": 180},
        )
        plan = {
            "audio": {"enabled": True, "model": "medium", "device": "cuda"},
            "frames": {
                "enabled": True,
                "rate": {"mode": "interval", "seconds": 30},
                "jpeg_quality": 75,
            },
            "ocr": {"enabled": True, "engine": "tesseract", "languages": ["rus", "eng"], "status": "coming_soon", "engine_available": True},
            "cv": {"enabled": False, "engine": "basic_opencv", "status": "coming_soon"},
        }

        status = self.track_job(manager.add_files([QueueFile(
            source_path=self.make_file("planned.mp4").source_path,
            source_filename="planned.mp4",
            processing_plan=plan,
        )]))
        item = status["items"][0]

        self.assertEqual("medium", item["processing_plan"]["audio"]["model"])
        self.assertEqual("cuda", item["processing_plan"]["audio"]["device"])
        self.assertTrue(item["processing_plan"]["frames"]["enabled"])
        self.assertEqual({"mode": "interval", "seconds": 30}, item["processing_plan"]["frames"]["rate"])
        self.assertEqual(75, item["processing_plan"]["frames"]["jpeg_quality"])
        self.assertFalse(item["processing_plan"]["ocr"]["enabled"])
        self.assertEqual("tesseract", item["processing_plan"]["ocr"]["backend"])
        self.assertTrue(item["processing_plan"]["ocr"]["engine_available"])
        self.assertFalse(item["operations"]["ocr"])
        self.assertTrue(item["operations"]["extract_frames"])
        self.assertEqual(75, item["frame_extraction"]["jpeg_quality"])

    def test_per_item_audio_model_and_device_are_used_for_transcription(self) -> None:
        calls: list[tuple[str, str]] = []

        def processor(_item: dict, model: str, device: str) -> dict:
            calls.append((model, device))
            return {"processing_time_sec": 1}

        manager = self.make_manager(processor=processor, duration_reader=lambda _path: 1)
        manager.add_files([QueueFile(
            source_path=self.make_file("override.wav").source_path,
            source_filename="override.wav",
            processing_plan={"audio": {"enabled": True, "model": "large-v3", "device": "cuda"}},
        )])

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        self.assertEqual([("large-v3", "cuda")], calls)

    def test_per_item_frame_settings_are_passed_to_frame_processor(self) -> None:
        captured_settings: list[dict] = []

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            captured_settings.append(item["frame_extraction"])
            return {"status": "completed", "completed": True, "extracted_frame_count": 2}

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            frame_processor=frame_processor,
            duration_reader=lambda _path: 10,
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 320, "height": 180},
        )
        manager.add_files([QueueFile(
            source_path=self.make_file("frames.mp4").source_path,
            source_filename="frames.mp4",
            processing_plan={
                "audio": {"enabled": False, "model": "small", "device": "auto"},
                "frames": {"enabled": True, "rate": {"mode": "interval", "seconds": 30}, "jpeg_quality": 75},
            },
        )])

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        self.assertEqual({"mode": "interval", "seconds": 30}, captured_settings[0]["rate"])
        self.assertEqual(75, captured_settings[0]["jpeg_quality"])

    def test_changing_defaults_does_not_mutate_existing_items(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})
        first_plan = {"audio": {"enabled": True, "model": "small", "device": "auto"}}
        second_plan = {"audio": {"enabled": True, "model": "medium", "device": "cpu"}}

        manager.add_files([QueueFile(
            source_path=self.make_file("first.wav").source_path,
            source_filename="first.wav",
            processing_plan=first_plan,
        )])
        status = manager.add_files([QueueFile(
            source_path=self.make_file("second.wav").source_path,
            source_filename="second.wav",
            processing_plan=second_plan,
        )])

        self.assertEqual("small", status["items"][0]["processing_plan"]["audio"]["model"])
        self.assertEqual("medium", status["items"][1]["processing_plan"]["audio"]["model"])

    def test_legacy_item_without_processing_plan_uses_start_fallbacks(self) -> None:
        calls: list[tuple[str, str]] = []

        def processor(_item: dict, model: str, device: str) -> dict:
            calls.append((model, device))
            return {"processing_time_sec": 1}

        manager = self.make_manager(processor=processor, duration_reader=lambda _path: 1)
        manager.add_files([self.make_file("legacy.wav")])
        manager._items[0].pop("processing_plan", None)

        manager.start("tiny", "cpu")
        manager.wait(timeout=3)

        self.assertEqual([("tiny", "cpu")], calls)

    def test_ocr_cv_placeholders_are_normalized_to_noop(self) -> None:
        processed: list[str] = []

        def processor(item: dict, _model: str, _device: str) -> dict:
            processed.append(item["source_filename"])
            return {"processing_time_sec": 1}

        manager = self.make_manager(processor=processor, duration_reader=lambda _path: 1)
        status = manager.add_files([QueueFile(
            source_path=self.make_file("placeholder.wav").source_path,
            source_filename="placeholder.wav",
            processing_plan={
                "audio": {"enabled": True, "model": "small", "device": "auto"},
                "ocr": {"enabled": True, "backend": "easyocr", "engine_available": True},
                "cv": {"enabled": True, "engine": "basic_opencv"},
            },
        )])

        item = status["items"][0]
        self.assertFalse(item["processing_plan"]["ocr"]["enabled"])
        self.assertEqual("easyocr", item["processing_plan"]["ocr"]["backend"])
        self.assertEqual(["ru", "en"], item["processing_plan"]["ocr"]["languages"])
        self.assertTrue(item["processing_plan"]["ocr"]["engine_available"])
        self.assertEqual("coming_soon", item["processing_plan"]["ocr"]["status"])
        self.assertFalse(item["processing_plan"]["cv"]["enabled"])
        self.assertFalse(item["operations"]["ocr"])
        self.assertFalse(item["operations"]["cv"])

        manager.start("small", "auto")
        manager.wait(timeout=3)

        self.assertEqual(["placeholder.wav"], processed)

    def test_duplicate_pending_file_add_is_ignored(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})
        queue_file = self.make_file("one.wav")

        self.track_job(manager.add_files([queue_file]))
        status = manager.add_files([queue_file])

        self.assertEqual(1, status["total_items"])
        self.assertEqual(["one.wav"], [item["source_filename"] for item in status["items"]])

    def test_duplicate_pending_url_add_is_ignored(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})

        self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        status = manager.add_urls([QueueUrl("https://example.test/video#again")])

        self.assertEqual(1, status["total_items"])
        self.assertEqual(["https://example.test/video"], [item["source_url"] for item in status["items"]])

    def test_url_video_download_exposes_downloading_video_stage(self) -> None:
        started = threading.Event()
        release = threading.Event()
        video = self.make_file("stage_video.mkv")

        def video_downloader(_url: str) -> dict:
            started.set()
            release.wait(timeout=3)
            return {
                "source_path": str(video.source_path),
                "source_title": "Stage Video",
                "source_platform": "youtube",
                "audio_duration_sec": 5,
                "downloaded_media_path": str(video.source_path),
                "downloaded_video_path": str(video.source_path),
            }

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_downloader=video_downloader,
            frame_processor=lambda _item, _cancel_event, _progress: {"status": "completed", "completed": True},
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        manager.update_item(status["items"][0]["index"], operations={"transcribe_audio": False, "extract_frames": True})

        manager.start("small")
        self.assertTrue(started.wait(timeout=2))
        status = manager.status()
        self.assertEqual("downloading_video", status["current_stage"])
        self.assertEqual("queueStageDownloadingVideo", status["current_stage_label_key"])
        self.assertEqual("downloading_video", status["current_item"]["stage"])
        release.set()
        manager.wait(timeout=3)

    def test_audio_transcription_exposes_transcribing_audio_stage(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def processor(_item: dict, _model: str, _device: str) -> dict:
            started.set()
            release.wait(timeout=3)
            return {"processing_time_sec": 1}

        manager = self.make_manager(processor=processor, duration_reader=lambda _path: 1)
        self.track_job(manager.add_files([self.make_file("speech.wav")]))

        manager.start("small")
        self.assertTrue(started.wait(timeout=2))
        status = manager.status()
        self.assertEqual("transcribing_audio", status["current_stage"])
        self.assertEqual("queueStageTranscribingAudio", status["current_stage_label_key"])
        release.set()
        manager.wait(timeout=3)

    def test_url_download_progress_and_cancellation_continue_queue(self) -> None:
        download_started = threading.Event()
        processed: list[str] = []

        def downloader(_url: str, cancel_event: threading.Event, progress_callback) -> dict:
            progress_callback({
                "mode": "determinate",
                "percent": 43.2,
                "downloaded_bytes": 432,
                "total_bytes": 1000,
                "speed_bytes_per_sec": 100,
                "eta_sec": 6,
                "source": "direct",
            })
            download_started.set()
            cancel_event.wait(timeout=3)
            raise UrlDownloadCancelled()

        def processor(item: dict, _model: str, _device: str) -> dict:
            processed.append(item["source_filename"])
            return {"processing_time_sec": 1, "audio_duration_sec": 1}

        manager = self.make_manager(
            processor=processor,
            downloader=downloader,
            duration_reader=lambda _path: 1,
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/slow")]))
        manager.add_files([self.make_file("after.wav")])

        manager.start("small", "cpu")
        self.assertTrue(download_started.wait(timeout=2))
        active = manager.status()["current_item"]
        self.assertEqual("downloading_media", active["stage"])
        self.assertEqual("determinate", active["stage_progress"]["mode"])
        self.assertEqual(43.2, active["stage_progress"]["percent"])

        cancelling = manager.cancel_item(status["items"][0]["index"])
        self.assertEqual("cancelling_download", cancelling["current_stage"])
        self.assertTrue(cancelling["current_item"]["cancel_requested"])
        manager.wait(timeout=3)

        result = manager.status()
        self.assertEqual("completed", result["status"])
        self.assertEqual(["cancelled", "completed"], [item["status"] for item in result["items"]])
        self.assertEqual("download_cancelled", result["items"][0]["stage"])
        self.assertEqual(["after.wav"], processed)

    def test_frame_extraction_progress_updates_stage_percent(self) -> None:
        progress_seen = threading.Event()
        release = threading.Event()

        def frame_processor(_item: dict, _cancel_event: threading.Event, progress_callback) -> dict:
            progress_callback({"estimated_frame_count": 10, "extracted_frame_count": 4})
            progress_seen.set()
            release.wait(timeout=3)
            return {"status": "completed", "completed": True, "estimated_frame_count": 10, "extracted_frame_count": 10}

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            frame_processor=frame_processor,
            duration_reader=lambda _path: 10,
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        manager.add_files([QueueFile(
            source_path=self.make_file("progress.mp4").source_path,
            source_filename="progress.mp4",
            operations={"transcribe_audio": False, "extract_frames": True},
        )])
        manager.start("small", "cpu")
        self.assertTrue(progress_seen.wait(timeout=2))

        active = manager.status()["current_item"]
        self.assertEqual("extracting_frames", active["stage"])
        self.assertEqual(40.0, active["stage_progress"]["percent"])
        self.assertEqual(4, active["stage_progress"]["completed_units"])
        release.set()
        manager.wait(timeout=3)

    def test_frame_extraction_exposes_stage_and_terminal_cancel_stage(self) -> None:
        started = threading.Event()

        def frame_processor(item: dict, cancel_event: threading.Event, _progress) -> dict:
            started.set()
            cancel_event.wait(timeout=3)
            return {
                "status": "cancelled",
                "completed": False,
                "cancelled": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 1,
            }

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            frame_processor=frame_processor,
            duration_reader=lambda _path: 1,
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        self.track_job(manager.add_files([
            QueueFile(
                source_path=self.make_file("frames.mp4").source_path,
                source_filename="frames.mp4",
                operations={"transcribe_audio": False, "extract_frames": True},
            )
        ]))

        manager.start("small")
        self.assertTrue(started.wait(timeout=2))
        status = manager.status()
        self.assertEqual("extracting_frames", status["current_stage"])
        cancelling = manager.cancel_item(1)
        self.assertEqual("cancelling", cancelling["current_stage"])
        manager.wait(timeout=3)
        item = manager.status()["items"][0]
        self.assertEqual("cancelled", item["status"])
        self.assertEqual("cancelled", item["stage"])

    def test_url_item_without_executable_operation_is_rejected(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": False, "extract_frames": False},
        )

        with self.assertRaisesRegex(RuntimeError, "ссылки"):
            manager.start("small")

    def test_url_extract_frames_uses_video_download_and_frame_processor(self) -> None:
        video = self.make_file("downloaded_video.mkv")
        audio_downloads: list[str] = []
        video_downloads: list[str] = []
        download_settings_seen: list[dict] = []
        frame_sources: list[str] = []

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            frame_sources.append(item["source_path"])
            return {
                "status": "completed",
                "completed": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 2,
            }

        def video_downloader(url: str, download_settings: dict) -> dict:
            video_downloads.append(url)
            download_settings_seen.append(download_settings)
            return {
                "source_path": str(video.source_path),
                "source_title": "Downloaded URL Video",
                "source_platform": "youtube",
                "audio_duration_sec": 10,
                "downloaded_media_path": str(video.source_path),
                "downloaded_video_path": str(video.source_path),
                "url_download_diagnostics": {
                    "url_download_format_profile": download_settings["format_profile"],
                    "yt_dlp_format_string_used": "webm-format",
                },
            }

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            downloader=lambda url: audio_downloads.append(url) or {},
            video_downloader=video_downloader,
            frame_processor=frame_processor,
            duration_reader=lambda _path: 10,
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl(
            "https://example.test/video",
            processing_plan={
                "url_download": {
                    "format_profile": "prefer_webm",
                    "log_media_probe": True,
                    "log_extraction_benchmark": True,
                }
            },
        )]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": False, "extract_frames": True},
        )
        manager.start("small")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual([], audio_downloads)
        self.assertEqual(["https://example.test/video"], video_downloads)
        self.assertEqual("prefer_webm", download_settings_seen[0]["format_profile"])
        self.assertEqual([str(video.source_path)], frame_sources)
        self.assertEqual(str(video.source_path), item["downloaded_media_path"])
        self.assertTrue(item["frames_index_path"].endswith("frames_index.json"))
        self.assertEqual("prefer_webm", item["processing_plan"]["url_download"]["format_profile"])
        self.assertEqual(2, item["url_download_diagnostics"]["frames_extracted"])
        self.assertIn("frame_extraction_time_sec", item["url_download_diagnostics"])
        self.assertIn("sec_per_frame", item["url_download_diagnostics"])

    def test_direct_mp4_url_extract_frames_downloads_directly_without_ytdlp(self) -> None:
        url_downloader = UrlDownloader(self.root / "downloads")
        frame_sources: list[str] = []

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            frame_sources.append(item["source_path"])
            return {
                "status": "completed",
                "completed": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 2,
            }

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_downloader=url_downloader.download_video,
            frame_processor=frame_processor,
            duration_reader=lambda _path: 10,
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/media/direct.mp4?token=abc")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": False, "extract_frames": True},
        )
        fake_module = types.SimpleNamespace(YoutubeDL=lambda _options: self.fail("yt-dlp should not be used"))
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with patch("app.url_downloader.urlopen", return_value=FakeHttpResponse([b"video"])):
                manager.start("small")
                manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("completed", item["status"])
        self.assertEqual("direct", item["source_platform"])
        self.assertTrue(Path(item["downloaded_media_path"]).exists())
        self.assertEqual([item["downloaded_media_path"]], frame_sources)

    def test_url_item_with_both_operations_preserves_transcript_and_frames(self) -> None:
        video = self.make_file("both_url.mkv")

        def processor(item: dict, _model: str, _device: str) -> dict:
            return {
                "audio_duration_sec": 5,
                "processing_time_sec": 2,
                "realtime_factor": 2.5,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            return {
                "status": "completed",
                "completed": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 3,
            }

        manager = self.make_manager(
            processor=processor,
            video_downloader=lambda _url: {
                "source_path": str(video.source_path),
                "source_title": "Both URL",
                "source_platform": "youtube",
                "audio_duration_sec": 5,
                "downloaded_media_path": str(video.source_path),
                "downloaded_video_path": str(video.source_path),
            },
            frame_processor=frame_processor,
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": True, "extract_frames": True},
        )
        manager.start("small")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("completed", item["status"])
        self.assertTrue(item["transcript_path"].endswith(".txt"))
        self.assertTrue(item["frames_index_path"].endswith("frames_index.json"))
        self.assertEqual(str(video.source_path), item["downloaded_media_path"])

    def test_url_transcription_failure_still_runs_selected_frame_extraction(self) -> None:
        video = self.make_file("frames_after_transcript_error.mkv")
        frame_calls: list[str] = []

        def processor(_item: dict, _model: str, _device: str) -> dict:
            raise RuntimeError("transcript failed")

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            frame_calls.append(item["source_path"])
            return {
                "status": "completed",
                "completed": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 4,
            }

        manager = self.make_manager(
            processor=processor,
            error_recorder=lambda _item, _model, _device, _exc: {"json_path": str(self.root / "transcript_error.json")},
            video_downloader=lambda _url: {
                "source_path": str(video.source_path),
                "source_title": "Frames After Error",
                "source_platform": "youtube",
                "downloaded_media_path": str(video.source_path),
                "downloaded_video_path": str(video.source_path),
            },
            frame_processor=frame_processor,
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": True, "extract_frames": True},
        )
        manager.start("small")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("error", item["status"])
        self.assertEqual([str(video.source_path)], frame_calls)
        self.assertTrue(item["frames_index_path"].endswith("frames_index.json"))
        self.assertIn("transcript failed", item["error_message"])

    def test_url_frame_failure_after_transcription_preserves_transcript(self) -> None:
        video = self.make_file("url_frame_error.mkv")

        def processor(item: dict, _model: str, _device: str) -> dict:
            return {
                "audio_duration_sec": 5,
                "processing_time_sec": 2,
                "realtime_factor": 2.5,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            return {
                "status": "failed",
                "completed": False,
                "error_message": "Could not write JPEG frame: frame_000001__t000000.000.jpg",
                "error_code": "frame_write_failed",
                "error_filename": "frame_000001__t000000.000.jpg",
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 0,
            }

        manager = self.make_manager(
            processor=processor,
            video_downloader=lambda _url: {
                "source_path": str(video.source_path),
                "source_title": "URL Frame Error",
                "source_platform": "youtube",
                "downloaded_media_path": str(video.source_path),
                "downloaded_video_path": str(video.source_path),
            },
            frame_processor=frame_processor,
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": True, "extract_frames": True},
        )
        manager.start("small")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("error", item["status"])
        self.assertTrue(item["transcript_path"].endswith(".txt"))
        self.assertEqual("frame_write_failed", item["frame_extraction_result"]["error_code"])

    def test_output_artifacts_include_transcript_frames_index_and_downloaded_media(self) -> None:
        video = self.make_file("artifact_video.mkv")
        frames_dir = self.root / "artifact_frames"
        frames_index = frames_dir / "frames_index.json"

        def processor(item: dict, _model: str, _device: str) -> dict:
            transcript_path = Path(f"{item['source_path']}.txt")
            json_path = Path(f"{item['source_path']}.json")
            transcript_path.write_text("hello", encoding="utf-8")
            json_path.write_text("{}", encoding="utf-8")
            return {
                "audio_duration_sec": 5,
                "processing_time_sec": 2,
                "realtime_factor": 2.5,
                "transcript_path": str(transcript_path),
                "json_path": str(json_path),
            }

        def frame_processor(_item: dict, _cancel_event: threading.Event, _progress) -> dict:
            frames_dir.mkdir(parents=True, exist_ok=True)
            frames_index.write_text("{}", encoding="utf-8")
            return {
                "status": "completed",
                "completed": True,
                "frames_dir": frames_dir.name,
                "frames_path": str(frames_dir),
                "frames_index_path": str(frames_index),
                "extracted_frame_count": 2,
            }

        manager = self.make_manager(
            processor=processor,
            video_downloader=lambda _url: {
                "source_path": str(video.source_path),
                "source_title": "Artifact URL",
                "source_platform": "direct",
                "downloaded_media_path": str(video.source_path),
                "downloaded_video_path": str(video.source_path),
            },
            frame_processor=frame_processor,
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/video")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": True, "extract_frames": True},
        )

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        outputs = manager.status()["items"][0]["outputs"]
        self.assertTrue(outputs["transcript_path"].endswith(".txt"))
        self.assertTrue(outputs["transcript_exists"])
        self.assertTrue(outputs["json_path"].endswith(".json"))
        self.assertTrue(outputs["json_exists"])
        self.assertEqual(str(frames_dir.resolve()), outputs["frames_dir"])
        self.assertTrue(outputs["frames_dir_exists"])
        self.assertEqual(str(frames_index.resolve()), outputs["frames_index_path"])
        self.assertTrue(outputs["frames_index_exists"])
        self.assertEqual(str(video.source_path), outputs["downloaded_media_path"])
        self.assertTrue(outputs["downloaded_media_exists"])
        self.assertFalse(outputs["downloaded_media_deleted"])

    def test_success_retention_cleanup_can_mark_downloaded_media_deleted(self) -> None:
        video = self.make_file("delete_after_success.mp4")

        def processor(item: dict, _model: str, _device: str) -> dict:
            transcript_path = Path(f"{item['source_path']}.txt")
            transcript_path.write_text("hello", encoding="utf-8")
            return {"processing_time_sec": 1, "transcript_path": str(transcript_path)}

        def retention_cleaner(item: dict) -> dict:
            Path(item["downloaded_media_path"]).unlink()
            return {"downloaded_media_deleted": True}

        manager = self.make_manager(
            processor=processor,
            downloader=lambda _url: {
                "source_path": str(video.source_path),
                "source_title": "Delete After Success",
                "source_platform": "direct",
                "downloaded_media_path": str(video.source_path),
                "downloaded_audio_path": str(video.source_path),
            },
            duration_reader=lambda _path: 5,
            retention_cleaner=retention_cleaner,
        )
        self.track_job(manager.add_urls([QueueUrl("https://example.test/audio.mp4")]))

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        outputs = manager.status()["items"][0]["outputs"]
        self.assertEqual("completed", manager.status()["items"][0]["status"])
        self.assertFalse(video.source_path.exists())
        self.assertTrue(outputs["downloaded_media_deleted"])
        self.assertFalse(outputs["downloaded_media_exists"])

    def test_url_download_is_deleted_after_frame_extraction_cancellation(self) -> None:
        storage = StorageManager(data_dir=self.root / "data")
        storage.update_settings({"keep_downloaded_url_media": False})
        downloaded = self.root / "data" / "downloads" / "cancel-frames.mp4"
        downloaded.parent.mkdir(parents=True)
        downloaded.write_bytes(b"video")

        def frame_processor(_item: dict, _cancel_event: threading.Event, _progress) -> dict:
            self.assertTrue(downloaded.exists())
            return {"status": "cancelled", "cancelled": True, "extracted_frame_count": 1}

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_downloader=lambda _url: {
                "source_path": str(downloaded),
                "downloaded_media_path": str(downloaded),
                "downloaded_video_path": str(downloaded),
                "source_title": "Cancel Frames",
            },
            frame_processor=frame_processor,
            duration_reader=lambda _path: 1,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
            retention_cleaner=storage.apply_retention_cleanup,
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/cancel-frames")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": False, "extract_frames": True},
        )

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("cancelled", item["status"])
        self.assertFalse(downloaded.exists())
        self.assertTrue(item["outputs"]["downloaded_media_deleted"])

    def test_url_download_is_deleted_after_transcription_cancellation(self) -> None:
        storage = StorageManager(data_dir=self.root / "data")
        storage.update_settings({"keep_downloaded_url_media": False})
        downloaded = self.root / "data" / "downloads" / "cancel-transcription.m4a"
        downloaded.parent.mkdir(parents=True)
        downloaded.write_bytes(b"audio")
        started = threading.Event()

        def processor(_item: dict, _model: str, _device: str, cancel_event: threading.Event) -> dict:
            self.assertTrue(downloaded.exists())
            started.set()
            cancel_event.wait(timeout=3)
            self.assertTrue(downloaded.exists())
            return {"status": "cancelled", "cancellation_reason": "cancelled"}

        manager = self.make_manager(
            processor=processor,
            downloader=lambda _url: {
                "source_path": str(downloaded),
                "downloaded_media_path": str(downloaded),
                "downloaded_audio_path": str(downloaded),
                "source_title": "Cancel Transcription",
            },
            duration_reader=lambda _path: 1,
            retention_cleaner=storage.apply_retention_cleanup,
        )
        status = self.track_job(manager.add_urls([QueueUrl("https://example.test/cancel-transcription")]))

        manager.start("small", "cpu")
        self.assertTrue(started.wait(timeout=2))
        manager.cancel_item(status["items"][0]["index"])
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("cancelled", item["status"])
        self.assertFalse(downloaded.exists())
        self.assertTrue(item["outputs"]["downloaded_media_deleted"])

    def test_cancelled_url_download_is_kept_when_setting_is_enabled(self) -> None:
        storage = StorageManager(data_dir=self.root / "data")
        downloaded = self.root / "data" / "downloads" / "keep-cancelled.m4a"
        downloaded.parent.mkdir(parents=True)
        downloaded.write_bytes(b"audio")

        manager = self.make_manager(
            processor=lambda _item, _model, _device: {"status": "cancelled"},
            downloader=lambda _url: {
                "source_path": str(downloaded),
                "downloaded_media_path": str(downloaded),
                "downloaded_audio_path": str(downloaded),
                "source_title": "Keep Cancelled",
            },
            duration_reader=lambda _path: 1,
            retention_cleaner=storage.apply_retention_cleanup,
        )
        self.track_job(manager.add_urls([QueueUrl("https://example.test/keep-cancelled")]))

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        self.assertEqual("cancelled", manager.status()["items"][0]["status"])
        self.assertTrue(downloaded.exists())

    def test_url_download_is_deleted_after_controlled_failure(self) -> None:
        storage = StorageManager(data_dir=self.root / "data")
        storage.update_settings({"keep_downloaded_url_media": False})
        downloaded = self.root / "data" / "downloads" / "failed.m4a"
        downloaded.parent.mkdir(parents=True)
        downloaded.write_bytes(b"audio")

        manager = self.make_manager(
            processor=lambda _item, _model, _device: (_ for _ in ()).throw(RuntimeError("processing failed")),
            downloader=lambda _url: {
                "source_path": str(downloaded),
                "downloaded_media_path": str(downloaded),
                "downloaded_audio_path": str(downloaded),
                "source_title": "Failed URL",
            },
            duration_reader=lambda _path: 1,
            retention_cleaner=storage.apply_retention_cleanup,
        )
        self.track_job(manager.add_urls([QueueUrl("https://example.test/failed")]))

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("error", item["status"])
        self.assertEqual("processing failed", item["error_message"])
        self.assertFalse(downloaded.exists())
        self.assertTrue(item["outputs"]["downloaded_media_deleted"])

    def test_url_failure_cleanup_error_does_not_hide_original_status(self) -> None:
        downloaded = self.root / "cleanup-failure.m4a"
        downloaded.write_bytes(b"audio")

        def retention_cleaner(_item: dict) -> dict:
            raise OSError("cleanup failed")

        manager = self.make_manager(
            processor=lambda _item, _model, _device: (_ for _ in ()).throw(RuntimeError("original failure")),
            downloader=lambda _url: {
                "source_path": str(downloaded),
                "downloaded_media_path": str(downloaded),
                "downloaded_audio_path": str(downloaded),
                "source_title": "Failure Cleanup",
            },
            duration_reader=lambda _path: 1,
            retention_cleaner=retention_cleaner,
        )
        self.track_job(manager.add_urls([QueueUrl("https://example.test/failure-cleanup")]))

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("error", item["status"])
        self.assertEqual("original failure", item["error_message"])
        self.assertEqual("cleanup failed", item["outputs"]["retention_cleanup_error"])
        self.assertTrue(downloaded.exists())

    def test_failed_and_cancelled_local_jobs_do_not_run_retention_cleanup(self) -> None:
        cleanup_calls: list[str] = []

        def retention_cleaner(item: dict) -> dict:
            cleanup_calls.append(item["source_filename"])
            return {}

        failed_manager = self.make_manager(
            processor=lambda _item, _model, _device: (_ for _ in ()).throw(RuntimeError("boom")),
            duration_reader=lambda _path: 1,
            retention_cleaner=retention_cleaner,
        )
        self.track_job(failed_manager.add_files([self.make_file("fails.wav")]))
        failed_manager.start("small")
        failed_manager.wait(timeout=3)

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            return {
                "status": "cancelled",
                "completed": False,
                "cancelled": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "extracted_frame_count": 0,
            }

        cancelled_manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            frame_processor=frame_processor,
            duration_reader=lambda _path: 1,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
            retention_cleaner=retention_cleaner,
        )
        self.track_job(cancelled_manager.add_files([
            QueueFile(
                source_path=self.make_file("cancelled.mp4").source_path,
                source_filename="cancelled.mp4",
                operations={"transcribe_audio": False, "extract_frames": True},
            )
        ]))
        cancelled_manager.start("small")
        cancelled_manager.wait(timeout=3)

        self.assertEqual("error", failed_manager.status()["items"][0]["status"])
        self.assertEqual("cancelled", cancelled_manager.status()["items"][0]["status"])
        self.assertEqual([], cleanup_calls)

    def test_preserves_recording_source_type(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})
        status = self.track_job(manager.add_files([
            QueueFile(
                source_path=self.make_file("mic.wav").source_path,
                source_filename="mic.wav",
                source_type="mic",
            )
        ]))
        self.assertEqual("mic", status["items"][0]["source_type"])

    def test_video_item_includes_operations_and_frame_estimate(self) -> None:
        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_metadata_reader=lambda _path: {
                "duration_sec": 31,
                "fps": 30,
                "width": 100,
                "height": 50,
                "frame_count": 930,
            },
        )
        status = self.track_job(manager.add_files([self.make_file("clip.avi")]))
        item = status["items"][0]

        self.assertEqual("video", item["media_kind"])
        self.assertTrue(item["operations"]["transcribe_audio"])
        self.assertFalse(item["operations"]["extract_frames"])
        self.assertEqual({"mode": "interval", "seconds": 10}, item["frame_extraction"]["rate"])
        self.assertEqual(90, item["frame_extraction"]["jpeg_quality"])
        self.assertEqual(4, item["frame_extraction"]["estimated_frame_count"])

    def test_video_item_accepts_jpeg_quality_100_without_changing_default(self) -> None:
        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_files([self.make_file("clip.avi")]))
        item = status["items"][0]
        self.assertEqual(90, item["frame_extraction"]["jpeg_quality"])

        updated = manager.update_item(
            item["index"],
            operations={"transcribe_audio": False, "extract_frames": True},
            frame_extraction={"rate": {"mode": "interval", "seconds": 10}, "jpeg_quality": 100},
        )

        self.assertEqual(100, updated["items"][0]["frame_extraction"]["jpeg_quality"])

    def test_video_item_without_executable_operation_is_rejected(self) -> None:
        manager = self.make_manager(
            processor=lambda _item, _model, _device: {},
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        status = self.track_job(manager.add_files([self.make_file("clip.mp4")]))
        manager.update_item(
            status["items"][0]["index"],
            operations={"transcribe_audio": False, "extract_frames": False},
        )

        with self.assertRaises(RuntimeError):
            manager.start("small")

    def test_pending_item_can_be_removed(self) -> None:
        manager = self.make_manager(processor=lambda _item, _model, _device: {})
        status = self.track_job(manager.add_files([self.make_file("one.wav"), self.make_file("two.wav")]))

        status = manager.remove_item(status["items"][1]["index"])

        self.assertEqual(1, status["total_items"])
        self.assertEqual(["one.wav"], [item["source_filename"] for item in status["items"]])

    def test_pending_item_can_be_removed_while_another_item_is_running(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def processor(_item: dict, _model: str, _device: str) -> dict:
            started.set()
            release.wait(timeout=3)
            return {"processing_time_sec": 1}

        manager = self.make_manager(processor=processor, duration_reader=lambda _path: 1)
        status = self.track_job(manager.add_files([self.make_file("one.wav"), self.make_file("two.wav")]))
        manager.start("small")
        self.assertTrue(started.wait(timeout=2))
        manager.remove_item(status["items"][1]["index"])
        release.set()
        manager.wait(timeout=3)

        status = manager.status()
        self.assertEqual("completed", status["status"])
        self.assertEqual(["completed"], [item["status"] for item in status["items"]])
        self.assertEqual(["one.wav"], [item["source_filename"] for item in status["items"]])

    def test_running_frame_extraction_can_be_cancelled_and_queue_continues(self) -> None:
        frame_started = threading.Event()
        processed: list[str] = []

        def processor(item: dict, _model: str, _device: str) -> dict:
            processed.append(item["source_filename"])
            return {"processing_time_sec": 1}

        def frame_processor(item: dict, cancel_event: threading.Event, _progress) -> dict:
            frame_started.set()
            cancel_event.wait(timeout=3)
            return {
                "status": "cancelled",
                "completed": False,
                "cancelled": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "estimated_frame_count": 10,
                "extracted_frame_count": 1,
            }

        manager = self.make_manager(
            processor=processor,
            frame_processor=frame_processor,
            duration_reader=lambda _path: 1,
            video_metadata_reader=lambda _path: {"duration_sec": 10, "fps": 30, "width": 100, "height": 50},
        )
        self.track_job(manager.add_files([
            QueueFile(
                source_path=self.make_file("video.mp4").source_path,
                source_filename="video.mp4",
                operations={"transcribe_audio": False, "extract_frames": True},
            ),
            self.make_file("after.wav"),
        ]))

        manager.start("small", "cpu")
        self.assertTrue(frame_started.wait(timeout=2))
        cancelling = manager.cancel_item(1)
        self.assertTrue(cancelling["current_item"]["cancel_requested"])
        manager.cancel_item(1)
        manager.wait(timeout=3)

        status = manager.status()
        self.assertEqual("completed", status["status"])
        self.assertEqual(["cancelled", "completed"], [item["status"] for item in status["items"]])
        self.assertEqual(["after.wav"], processed)
        self.assertEqual(1, status["items"][0]["extracted_frame_count"])

    def test_video_item_with_both_operations_records_transcript_and_frames(self) -> None:
        def processor(item: dict, _model: str, _device: str) -> dict:
            return {
                "audio_duration_sec": 5,
                "processing_time_sec": 2,
                "realtime_factor": 2.5,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            return {
                "status": "completed",
                "completed": True,
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "estimated_frame_count": 3,
                "extracted_frame_count": 3,
            }

        manager = self.make_manager(
            processor=processor,
            frame_processor=frame_processor,
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        self.track_job(manager.add_files([
            QueueFile(
                source_path=self.make_file("both.webm").source_path,
                source_filename="both.webm",
                operations={"transcribe_audio": True, "extract_frames": True},
            )
        ]))

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        item = manager.status()["items"][0]
        self.assertEqual("completed", item["status"])
        self.assertTrue(item["transcript_path"].endswith(".txt"))
        self.assertTrue(item["json_path"].endswith(".json"))
        self.assertTrue(item["frames_index_path"].endswith("frames_index.json"))
        self.assertEqual(3, item["extracted_frame_count"])

    def test_frame_failure_after_audio_transcription_preserves_transcript_result(self) -> None:
        def processor(item: dict, _model: str, _device: str) -> dict:
            return {
                "audio_duration_sec": 5,
                "processing_time_sec": 2,
                "realtime_factor": 2.5,
                "transcript_path": f"{item['source_path']}.txt",
                "json_path": f"{item['source_path']}.json",
            }

        def frame_processor(item: dict, _cancel_event: threading.Event, _progress) -> dict:
            return {
                "status": "failed",
                "completed": False,
                "error_message": "Could not write JPEG frame: frame_000001__t000000.000.jpg",
                "error_code": "frame_write_failed",
                "error_filename": "frame_000001__t000000.000.jpg",
                "frames_dir": f"{item['output_base']}__frames",
                "frames_path": f"data/recordings/{item['output_base']}__frames",
                "frames_index_path": f"data/recordings/{item['output_base']}__frames/frames_index.json",
                "estimated_frame_count": 3,
                "extracted_frame_count": 0,
            }

        manager = self.make_manager(
            processor=processor,
            frame_processor=frame_processor,
            duration_reader=lambda _path: 5,
            video_metadata_reader=lambda _path: {"duration_sec": 5, "fps": 30, "width": 100, "height": 50},
        )
        self.track_job(manager.add_files([
            QueueFile(
                source_path=self.make_file("partial.webm").source_path,
                source_filename="partial.webm",
                operations={"transcribe_audio": True, "extract_frames": True},
            ),
            self.make_file("after.wav"),
        ]))

        manager.start("small", "cpu")
        manager.wait(timeout=3)

        status = manager.status()
        first = status["items"][0]
        self.assertEqual("completed", status["status"])
        self.assertEqual("error", first["status"])
        self.assertEqual(1, status["failed_items"])
        self.assertTrue(first["transcript_path"].endswith(".txt"))
        self.assertTrue(first["json_path"].endswith(".json"))
        self.assertEqual("failed", first["frame_extraction_result"]["status"])
        self.assertEqual("frame_write_failed", first["frame_extraction_result"]["error_code"])
        self.assertEqual("completed", status["items"][1]["status"])

    def test_url_download_error_does_not_stop_queue(self) -> None:
        processed: list[str] = []

        def processor(item: dict, _model: str, _device: str) -> dict:
            processed.append(item["source_filename"])
            return {"processing_time_sec": 1}

        manager = self.make_manager(
            processor=processor,
            downloader=lambda _url: (_ for _ in ()).throw(RuntimeError("download failed")),
            duration_reader=lambda _path: 1,
        )
        self.track_job(manager.add_urls([QueueUrl("https://example.test/bad")]))
        manager.add_files([self.make_file("good.wav")])
        manager.start("small", "auto")
        manager.wait(timeout=3)
        self.assertFalse(manager.is_running)
        status = manager.status()
        self.assertEqual(1, status["failed_items"])
        self.assertEqual(1, status["completed_items"])
        self.assertEqual(["good.wav"], processed)


if __name__ == "__main__":
    unittest.main()
