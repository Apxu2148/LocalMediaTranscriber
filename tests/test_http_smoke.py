import unittest
import shutil
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import PropertyMock, call, patch
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import config
from app import audio_recorder as audio_recorder_module
from app import system_audio_recorder as system_audio_recorder_module
from app import utils as utils_module
from app.audio_recorder import AudioRecorder
from app.system_audio_recorder import SystemAudioRecorder


PROJECT_TMP = Path(__file__).resolve().parents[1] / "tmp"
config.JOBS_DIR = PROJECT_TMP


@contextmanager
def project_temp_dir(prefix: str):
    path = PROJECT_TMP / f"{prefix}_{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


with patch.object(utils_module, "setup_logging"):
    from app import main as main_module  # noqa: E402


class HttpSmokeTests(unittest.TestCase):
    def test_interface_assets_disable_browser_cache(self) -> None:
        with TestClient(main_module.app) as client:
            for url in ["/", "/static/app.js", "/static/style.css", "/static/tour.js", "/static/i18n.js"]:
                response = client.get(url)
                self.assertEqual(200, response.status_code, url)
                self.assertEqual("no-store, no-cache, must-revalidate, max-age=0", response.headers["cache-control"])
                self.assertEqual("no-cache", response.headers["pragma"])
                self.assertEqual("0", response.headers["expires"])

    def test_status_exposes_app_version_and_queue_shape(self) -> None:
        fake_transcriber_status = {
            "configured_device": "auto",
            "configured_compute_type": "auto",
            "in_progress": False,
        }
        with (
            patch.object(main_module.recorder, "microphone_status", return_value={"available": True}),
            patch.object(main_module.system_recorder, "output_status", return_value={"available": True}),
            patch.object(main_module.transcriber, "status", return_value=fake_transcriber_status),
            patch.object(main_module, "model_statuses", return_value=[]),
            TestClient(main_module.app) as client,
        ):
            status_response = client.get("/api/status")
            self.assertEqual(200, status_response.status_code)
            self.assertEqual(config.APP_VERSION, status_response.json()["app_version"])
            self.assertIn(".mp4", status_response.json()["supported_formats"])

            queue_response = client.get("/api/queue/status")
            self.assertEqual(200, queue_response.status_code)
            self.assertEqual("empty", queue_response.json()["status"])
            self.assertIn("progress_percent", queue_response.json())

    def test_new_queue_benchmark_and_storage_endpoints_are_lightweight(self) -> None:
        fake_transcriber_status = {"in_progress": False}
        with (
            patch.object(main_module.queue_manager, "add_urls", return_value={"status": "pending"}) as add_urls,
            patch.object(main_module.queue_manager, "start", return_value={"status": "running"}) as start_queue,
            patch.object(main_module.benchmark_service, "status", return_value={"status": "idle", "running": False}),
            patch.object(main_module.benchmark_service, "start", return_value={"status": "running"}) as start_benchmark,
            patch.object(main_module.storage_manager, "summary", return_value={"total_size_bytes": 0, "folders": []}),
            patch.object(
                main_module.storage_manager,
                "settings",
                return_value={"keep_downloaded_url_media": True, "keep_uploaded_temp_files": True},
            ),
            patch.object(
                main_module.storage_manager,
                "update_settings",
                return_value={"keep_downloaded_url_media": False, "keep_uploaded_temp_files": True},
            ) as update_storage_settings,
            patch.object(
                main_module.storage_manager,
                "cleanup_folder",
                return_value={"folder": "downloads", "deleted_entries": 0, "deleted_bytes": 0, "errors": []},
            ) as cleanup_folder,
            patch.object(main_module.transcriber, "status", return_value=fake_transcriber_status),
            TestClient(main_module.app) as client,
        ):
            add_response = client.post(
                "/api/queue/add-urls",
                json={"urls": ["https://example.test/video"], "queue_folder_name": "smoke_queue"},
            )
            self.assertEqual(200, add_response.status_code)
            self.assertEqual("https://example.test/video", add_urls.call_args.args[0][0].source_url)
            self.assertEqual("smoke_queue", add_urls.call_args.kwargs["queue_folder_name"])

            queue_response = client.post(
                "/api/queue/start",
                json={"model": "small", "device": "cpu", "queue_folder_name": "final_queue"},
            )
            self.assertEqual(200, queue_response.status_code)
            start_queue.assert_called_once_with("small", "cpu", queue_folder_name="final_queue")

            benchmark_response = client.post(
                "/api/benchmark/run",
                json={"source_id": "prepared", "model": "small", "device": "cpu", "mode": "cold"},
            )
            self.assertEqual(200, benchmark_response.status_code)
            self.assertEqual("cpu", start_benchmark.call_args.kwargs["device"])

            self.assertEqual(200, client.get("/api/benchmark/status").status_code)
            storage_payload = client.get("/api/storage").json()
            self.assertIn("free_gb", storage_payload["disk"])
            self.assertEqual(200, client.get("/api/storage/summary").status_code)
            settings_response = client.get("/api/storage/settings")
            self.assertEqual(200, settings_response.status_code)
            self.assertTrue(settings_response.json()["keep_downloaded_url_media"])
            updated_settings_response = client.post(
                "/api/storage/settings",
                json={"keep_downloaded_url_media": False},
            )
            self.assertEqual(200, updated_settings_response.status_code)
            update_storage_settings.assert_called_once_with({"keep_downloaded_url_media": False})
            cleanup_response = client.post("/api/storage/cleanup", json={"folder": "downloads"})
            self.assertEqual(200, cleanup_response.status_code)
            cleanup_folder.assert_called_once_with("downloads")

    def test_queue_runtime_estimate_endpoint_returns_success_noop_and_invalid_item(self) -> None:
        success = {
            "status": "pending",
            "items": [{"index": 1, "estimate": {"status": "complete", "total_estimated_full_runtime_sec": 12}}],
        }
        noop = {
            "status": "pending",
            "items": [{"index": 2, "estimate": {"status": "complete", "no_enabled_operations": True}}],
        }
        with (
            patch.object(
                main_module.queue_manager,
                "estimate_item",
                side_effect=[success, noop, RuntimeError("Queue item was not found.")],
            ) as estimate_item,
            TestClient(main_module.app) as client,
        ):
            success_response = client.post("/api/queue/estimate-item", json={"index": 1})
            noop_response = client.post("/api/queue/estimate-item", json={"index": 2})
            invalid_response = client.post("/api/queue/estimate-item", json={"index": 999})

        self.assertEqual(200, success_response.status_code)
        self.assertEqual(12, success_response.json()["items"][0]["estimate"]["total_estimated_full_runtime_sec"])
        self.assertEqual(200, noop_response.status_code)
        self.assertTrue(noop_response.json()["items"][0]["estimate"]["no_enabled_operations"])
        self.assertEqual(400, invalid_response.status_code)
        self.assertEqual([call(1), call(2), call(999)], estimate_item.call_args_list)

    def test_url_download_settings_endpoints_persist_profile(self) -> None:
        saved = {
            "format_profile": "prefer_webm",
            "custom_format": "",
            "max_video_height": "720",
            "log_media_probe": True,
            "log_extraction_benchmark": True,
        }
        with (
            patch.object(main_module.url_download_settings_manager, "settings", return_value=saved),
            patch.object(main_module.url_download_settings_manager, "update_settings", return_value=saved) as update,
            TestClient(main_module.app) as client,
        ):
            get_response = client.get("/api/url-download/settings")
            post_response = client.post(
                "/api/url-download/settings",
                json={"format_profile": "prefer_webm", "max_video_height": "720", "log_media_probe": True},
            )

        self.assertEqual(200, get_response.status_code)
        self.assertEqual("prefer_webm", get_response.json()["format_profile"])
        self.assertEqual("720", get_response.json()["max_video_height"])
        self.assertEqual(200, post_response.status_code)
        update.assert_called_once_with({
            "format_profile": "prefer_webm",
            "max_video_height": "720",
            "log_media_probe": True,
        })

    def test_frame_settings_endpoints_persist_max_size(self) -> None:
        saved = {"max_frame_size": "width_1280"}
        with (
            patch.object(main_module.frame_settings_manager, "settings", return_value=saved),
            patch.object(main_module.frame_settings_manager, "update_settings", return_value=saved) as update,
            TestClient(main_module.app) as client,
        ):
            get_response = client.get("/api/frames/settings")
            post_response = client.post("/api/frames/settings", json={"max_frame_size": "width_1280"})

        self.assertEqual(200, get_response.status_code)
        self.assertEqual("width_1280", get_response.json()["max_frame_size"])
        self.assertEqual(200, post_response.status_code)
        update.assert_called_once_with({"max_frame_size": "width_1280"})

    def test_ocr_status_settings_and_check_endpoints_are_non_crashing(self) -> None:
        tesseract = {
            "id": "tesseract", "available": True, "status": "available",
            "path": r"C:\Tesseract-OCR\tesseract.exe", "version": "5.3.0",
        }
        backends = {
            "tesseract": tesseract,
            "easyocr": {"id": "easyocr", "available": False, "status": "not_installed"},
            "paddleocr": {"id": "paddleocr", "available": False, "status": "not_installed"},
            "windows_ocr": {"id": "windows_ocr", "available": False, "status": "not_installed"},
        }
        available = {"selected_backend": "easyocr", "backends": backends, "processing_enabled": False}
        invalid_tesseract = {
            **tesseract,
            "available": False,
            "status": "check_failed",
            "path": r"C:\bad\tesseract.exe",
            "error": "invalid_configured_path",
        }
        invalid = {**available, "backends": {**backends, "tesseract": invalid_tesseract}}
        with (
            patch.object(main_module.ocr_manager, "status", side_effect=[available, available, invalid]) as status,
            patch.object(
                main_module.ocr_manager,
                "update_settings",
                return_value={
                    "selected_backend": "easyocr",
                    "tesseract_path": r"C:\Tesseract-OCR\tesseract.exe",
                    "default_languages": ["rus", "eng"],
                },
            ) as update_settings,
            TestClient(main_module.app) as client,
        ):
            status_response = client.get("/api/ocr/status")
            settings_response = client.post(
                "/api/ocr/settings",
                json={
                    "selected_backend": "easyocr",
                    "tesseract_path": r"C:\Tesseract-OCR\tesseract.exe",
                    "default_languages": ["rus", "eng"],
                },
            )
            check_response = client.post(
                "/api/ocr/check",
                json={"backend": "tesseract", "tesseract_path": r"C:\bad\tesseract.exe"},
            )

        self.assertEqual(200, status_response.status_code)
        self.assertEqual({"tesseract", "easyocr", "paddleocr", "windows_ocr"}, set(status_response.json()["backends"]))
        self.assertEqual("easyocr", status_response.json()["selected_backend"])
        self.assertEqual(200, settings_response.status_code)
        self.assertEqual("5.3.0", settings_response.json()["status"]["backends"]["tesseract"]["version"])
        update_settings.assert_called_once_with({
            "selected_backend": "easyocr",
            "tesseract_path": r"C:\Tesseract-OCR\tesseract.exe",
            "default_languages": ["rus", "eng"],
        })
        self.assertEqual(200, check_response.status_code)
        self.assertEqual("invalid_configured_path", check_response.json()["backends"]["tesseract"]["error"])
        self.assertEqual(r"C:\bad\tesseract.exe", status.call_args_list[-1].args[0])
        self.assertEqual("tesseract", status.call_args_list[-1].kwargs["backend"])

    def test_ocr_settings_reject_invalid_backend(self) -> None:
        with (
            patch.object(main_module.ocr_manager, "update_settings", side_effect=ValueError("invalid_ocr_backend")),
            TestClient(main_module.app) as client,
        ):
            response = client.post("/api/ocr/settings", json={"selected_backend": "unknown"})

        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_ocr_backend", response.json()["detail"]["message"])

    def test_recording_queue_and_transcript_reader_are_path_constrained(self) -> None:
        with project_temp_dir("transcript_reader") as root:
            recordings_dir = root / "recordings"
            transcripts_dir = root / "transcripts"
            queues_dir = root / "queues"
            recordings_dir.mkdir()
            transcripts_dir.mkdir()
            queues_dir.mkdir()
            recording_path = recordings_dir / "mic.wav"
            missing_recording_path = recordings_dir / "missing.wav"
            transcript_path = transcripts_dir / "result.txt"
            queue_transcript_path = queues_dir / "queue_a" / "item_001" / "transcript" / "transcript.txt"
            non_txt_transcript_path = transcripts_dir / "result.json"
            outside_transcript_path = root / "outside.txt"
            recording_path.write_bytes(b"audio")
            transcript_path.write_text("recognized text", encoding="utf-8")
            queue_transcript_path.parent.mkdir(parents=True)
            queue_transcript_path.write_text("queue text", encoding="utf-8")
            non_txt_transcript_path.write_text("{}", encoding="utf-8")

            with (
                patch.object(config, "RECORDINGS_DIR", recordings_dir),
                patch.object(config, "TRANSCRIPTS_DIR", transcripts_dir),
                patch.object(config, "QUEUES_DIR", queues_dir),
                patch.object(main_module.queue_manager, "add_files", return_value={"status": "pending"}) as add_files,
                TestClient(main_module.app) as client,
            ):
                response = client.post(
                    "/api/queue/add-recordings",
                    json={"files": [{"file_path": str(recording_path), "source_type": "mic"}]},
                )
                self.assertEqual(200, response.status_code)
                queued_file = add_files.call_args.args[0][0]
                self.assertEqual(recording_path, queued_file.source_path)
                self.assertEqual("mic", queued_file.source_type)

                rejected_recording = client.post(
                    "/api/queue/add-recordings",
                    json={"files": [{"file_path": str(outside_transcript_path), "source_type": "mic"}]},
                )
                self.assertEqual(400, rejected_recording.status_code)
                missing_recording = client.post(
                    "/api/queue/add-recordings",
                    json={"files": [{"file_path": str(missing_recording_path), "source_type": "mic"}]},
                )
                self.assertEqual(400, missing_recording.status_code)
                rejected_source_type = client.post(
                    "/api/queue/add-recordings",
                    json={"files": [{"file_path": str(recording_path), "source_type": "browser"}]},
                )
                self.assertEqual(400, rejected_source_type.status_code)

                read_response = client.get("/api/transcripts/read", params={"file_path": "result.txt"})
                self.assertEqual(200, read_response.status_code)
                read_payload = read_response.json()
                self.assertTrue(read_payload["ok"])
                self.assertEqual(str(transcript_path), read_payload["path"])
                self.assertEqual("recognized text", read_payload["text"])

                read_absolute = client.get("/api/transcripts/read", params={"file_path": str(transcript_path)})
                self.assertEqual(200, read_absolute.status_code)
                self.assertEqual("recognized text", read_absolute.json()["text"])
                read_queue = client.get("/api/transcripts/read", params={"file_path": str(queue_transcript_path)})
                self.assertEqual(200, read_queue.status_code)
                self.assertEqual(str(queue_transcript_path), read_queue.json()["path"])
                self.assertEqual("queue text", read_queue.json()["text"])
                rejected_read = client.get("/api/transcripts/read", params={"file_path": str(outside_transcript_path)})
                self.assertEqual(400, rejected_read.status_code)
                rejected_non_txt = client.get("/api/transcripts/read", params={"file_path": non_txt_transcript_path.name})
                self.assertEqual(400, rejected_non_txt.status_code)
                rejected_traversal = client.get("/api/transcripts/read", params={"file_path": "../outside.txt"})
                self.assertEqual(400, rejected_traversal.status_code)

    def test_transcript_path_helper_reads_only_transcript_outputs(self) -> None:
        with project_temp_dir("transcript_helper") as root:
            transcripts_dir = root / "transcripts"
            queues_dir = root / "queues"
            transcripts_dir.mkdir()
            queues_dir.mkdir()
            transcript_path = transcripts_dir / "result.txt"
            queue_transcript_path = queues_dir / "queue_a" / "item_001" / "transcript" / "transcript.txt"
            outside_path = root / "outside.txt"
            invalid_utf8_path = transcripts_dir / "invalid.txt"
            transcript_path.write_text("recognized text", encoding="utf-8")
            queue_transcript_path.parent.mkdir(parents=True)
            queue_transcript_path.write_text("queue text", encoding="utf-8")
            invalid_utf8_path.write_bytes(b"hello \xff")

            with (
                patch.object(config, "TRANSCRIPTS_DIR", transcripts_dir),
                patch.object(config, "QUEUES_DIR", queues_dir),
            ):
                self.assertEqual(transcript_path.resolve(), main_module.validate_transcript_txt_path("result.txt"))
                self.assertEqual(queue_transcript_path.resolve(), main_module.validate_transcript_txt_path(str(queue_transcript_path)))
                self.assertEqual("hello \ufffd", main_module.read_transcript_text(invalid_utf8_path))
                with self.assertRaises(HTTPException):
                    main_module.validate_transcript_txt_path(str(outside_path))
                with self.assertRaises(HTTPException):
                    main_module.validate_transcript_txt_path("../outside.txt")

    def test_runtime_switch_endpoints_reject_inactive_tracks(self) -> None:
        with TestClient(main_module.app) as client:
            mic_response = client.post("/api/record/switch-microphone", json={"device_id": 1})
            self.assertEqual(400, mic_response.status_code)
            output_response = client.post("/api/record/switch-output-device", json={"output_device_id": "speaker"})
            self.assertEqual(400, output_response.status_code)

    def test_runtime_switch_endpoints_delegate_to_recorders(self) -> None:
        with (
            patch.object(type(main_module.recorder), "is_recording", new_callable=PropertyMock, return_value=True),
            patch.object(
                type(main_module.system_recorder),
                "is_recording",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(
                main_module.recorder,
                "switch_input_device",
                return_value={"track": "mic", "device_id": 2, "device_name": "Mic 2"},
            ) as switch_mic,
            patch.object(
                main_module.system_recorder,
                "switch_output_device",
                return_value={"track": "system", "output_device_id": "speaker-2", "output_device_name": "Speaker 2"},
            ) as switch_output,
            TestClient(main_module.app) as client,
        ):
            mic_response = client.post("/api/record/switch-microphone", json={"device_id": 2})
            self.assertEqual(200, mic_response.status_code)
            self.assertEqual("mic", mic_response.json()["track"])
            switch_mic.assert_called_once_with(2)

            output_response = client.post(
                "/api/record/switch-output-device",
                json={"output_device_id": "speaker-2"},
            )
            self.assertEqual(200, output_response.status_code)
            self.assertEqual("system", output_response.json()["track"])
            switch_output.assert_called_once_with("speaker-2")

    def test_runtime_switch_endpoint_reports_backend_failure(self) -> None:
        with (
            patch.object(type(main_module.recorder), "is_recording", new_callable=PropertyMock, return_value=True),
            patch.object(main_module.recorder, "switch_input_device", side_effect=RuntimeError("device busy")),
            TestClient(main_module.app) as client,
        ):
            response = client.post("/api/record/switch-microphone", json={"device_id": 2})
            self.assertEqual(500, response.status_code)
            self.assertIn("device busy", response.json()["detail"]["message"])

    def test_idle_audio_level_snapshots_do_not_open_capture_streams(self) -> None:
        recorder = AudioRecorder()
        fake_device = {"name": "Mic 1", "default_samplerate": 48000, "max_input_channels": 1}
        with (
            patch.object(recorder, "_resolve_input_device", return_value=(2, fake_device)),
            patch.object(audio_recorder_module.sd, "rec") as record_probe,
        ):
            mic_level = recorder.measure_input_level(2)

        record_probe.assert_not_called()
        self.assertFalse(mic_level["recording"])
        self.assertEqual(0, mic_level["level"])
        self.assertEqual(2, mic_level["device_id"])

        system_recorder = SystemAudioRecorder()
        fake_speaker = SimpleNamespace(id="speaker-1", name="Speaker 1")
        with (
            patch.object(system_audio_recorder_module, "ensure_com_initialized"),
            patch.object(system_recorder, "_resolve_speaker", return_value=fake_speaker),
            patch.object(system_audio_recorder_module.sc, "get_microphone") as loopback_probe,
        ):
            system_level = system_recorder.measure_output_level("speaker-1")

        loopback_probe.assert_not_called()
        self.assertFalse(system_level["recording"])
        self.assertEqual(0, system_level["level"])
        self.assertEqual("speaker-1", system_level["output_device_id"])

    def test_direct_transcription_routes_remain_available(self) -> None:
        paths = {route.path for route in main_module.app.routes}
        self.assertIn("/api/transcribe", paths)
        self.assertIn("/api/transcribe/file", paths)


if __name__ == "__main__":
    unittest.main()
