# Developer's Guide

This guide is the technical handoff for future LocalMediaTranscriber iterations. It describes the current fork, the existing audio/transcription architecture, and the rules for safe development.

## Project Purpose

LocalMediaTranscriber is a local Windows app for recording and processing media. Today it is still close to its source fork, LocalAudioTranscriber: it records microphone audio, records system audio through WASAPI loopback, transcribes audio or audio tracks from supported media files with `faster-whisper`, and can extract JPEG frames from video queue items.

The product direction is broader than audio-only transcription. Future iterations should evolve toward media sessions that can combine microphone audio, system audio, screen video, extracted frames, OCR, and VLM analysis while preserving the stable audio recording and queue behavior already present.

## Current Architecture

The app is a FastAPI backend plus static frontend:

- `app/main.py` creates the FastAPI app, mounts `/static`, exposes API endpoints, and coordinates recorder, queue, transcriber, benchmark, and transcript store services.
- `static/index.html`, `static/app.js`, `static/i18n.js`, `static/style.css`, and `static/tour.js` implement the web UI served by FastAPI.
- Runtime data lives under `data`.
- Whisper model caches live under `models`.
- Temporary files and process temp paths are redirected to `tmp`.

The current backend is mostly service-object based. `app/main.py` owns long-lived instances:

```python
recorder = AudioRecorder()
system_recorder = SystemAudioRecorder()
screen_recorder = ScreenRecorder()
video_muxer = VideoMuxer()
frame_extractor = VideoFrameExtractor()
transcriber = AudioTranscriber()
model_manager = WhisperModelManager()
transcript_store = TranscriptStore()
storage_manager = StorageManager()
```

Queue and benchmark services use these shared objects. This keeps model caching and recording state centralized, but it also means future changes should be careful with threading, locks, and shared mutable state.

## Important Folders and Files

- `app`: Python backend modules.
- `static`: Browser UI assets.
- `tests`: Focused unit and contract tests.
- `data\recordings`: WAV files created by microphone and system audio recording, screen video files, flat screen `session_*.json` files, merged video outputs, and `<base>__frames` frame extraction folders.
- `data\media_sessions`: Legacy screen recording MVP session folders from earlier builds.
- `data\uploads`: Files uploaded through the UI for transcription or benchmarks.
- `data\downloads`: Audio extracted or downloaded from public URLs.
- `data\transcripts`: TXT transcripts and JSON metadata.
- `data\jobs`: Queue job JSON snapshots.
- `data\logs`: Runtime logs.
- `models`: Local model/cache directory, including Hugging Face and faster-whisper caches.
- `static\icons`: Browser tab/app icon assets. The current favicon is `favicon.svg`.
- `tmp`: Project-local temporary directory.
- `requirements-cpu.txt`: Base dependencies for CPU/local runtime.
- `requirements-gpu.txt`: GPU add-ons plus mirrored screen-recording runtime dependencies.
- `run.bat`: Windows launcher that uses `.venv\Scripts\python.exe`.
- `stop.bat`: Project-scoped development stop script for Python/uvicorn server processes.
- `cleanup-dev.bat`: Developer cleanup entrypoint that calls `scripts\cleanup_dev.ps1`.
- `scripts\cleanup_dev.ps1`: Stops project-scoped server processes, removes source/test/script caches, safely handles stale `.git\index.lock`, and prints short Git status.
- `README.md`: Short user-facing documentation.
- `docs\DEVELOPERS.md`: This technical guide.

Runtime output under `data` is ignored by Git. Keep `data\recordings` available for audio/video output and screen session JSON, but do not treat those runtime files as source artifacts.

## Backend Modules

### `app/main.py`

Primary responsibilities:

- Create the FastAPI app with title `Local Media Transcriber`.
- Serve `static/index.html` at `/`.
- Mount static assets with no-cache headers.
- Expose status, storage, model, recording, screen recording, transcription, queue, folder, video mux, and benchmark endpoints.
- Validate uploaded files, local paths, recording paths, transcript paths, model names, devices, and recording modes.
- Coordinate mutually exclusive operations, such as preventing benchmark work during recording or queue execution.
- Save direct transcription errors through `TranscriptStore`.

Important endpoints include:

- `GET /api/status`
- `GET /api/models`
- `POST /api/models/download`
- `GET /api/models/download-status`
- `POST /api/models/verify`
- `POST /api/models/delete`
- `GET /api/models/info`
- `GET /api/storage`
- `GET /api/storage/summary`
- `GET /api/storage/settings`
- `POST /api/storage/settings`
- `POST /api/storage/cleanup`
- `GET /api/audio/devices`
- `GET /api/audio/output-devices`
- `GET /api/audio/level`
- `GET /api/audio/output-level`
- `GET /api/displays`
- `POST /api/displays/preview`
- `POST /api/screen-recording/start`
- `POST /api/screen-recording/stop`
- `GET /api/screen-recording/status`
- `GET /api/media-sessions/recent`
- `POST /api/video-mux/merge`
- `POST /api/record/start`
- `POST /api/record/stop`
- `POST /api/record/switch-microphone`
- `POST /api/record/switch-output-device`
- `POST /api/queue/add-files`
- `POST /api/queue/add-recordings`
- `POST /api/queue/add-urls`
- `POST /api/queue/update-item`
- `POST /api/queue/remove-item`
- `POST /api/queue/cancel-item`
- `POST /api/queue/estimate-item`
- `POST /api/queue/start`
- `POST /api/queue/stop-after-current`
- `POST /api/queue/clear`
- `POST /api/queue/retry-errors`
- `GET /api/queue/status`
- `POST /api/benchmark/upload`
- `POST /api/benchmark/run`
- `GET /api/benchmark/status`

The older direct transcription endpoints still exist in the backend, but the current UI uses the queue endpoints for normal transcription work.

### `app/storage_manager.py`

Storage visibility and conservative cleanup service.

Key behavior:

- `summary()` returns sizes for known data folders: `downloads`, `uploads`, `recordings`, `transcripts`, `logs`, and `jobs`, plus total data size. Missing folders report `0` bytes.
- `settings()` and `update_settings()` persist retention flags in `data\settings.json`.
- Default retention is conservative: `keep_downloaded_url_media=true` and `keep_uploaded_temp_files=true`.
- `cleanup_folder()` accepts only `downloads` and `uploads`. It deletes entries inside the known folder, ignores missing folders, catches per-entry deletion failures, and returns clear error strings instead of crashing the app.
- `apply_retention_cleanup()` is called by `QueueManager` only after successful processing. It may delete downloaded URL media under `data\downloads` or uploaded temp files under `data\uploads` when the matching keep flag is disabled.

Safe deletion rules:

- Never delete paths outside `config.DATA_DIR`.
- Never delete `data\recordings`, `data\transcripts`, extracted frame folders, screen recordings, or `frames_index.json` from retention cleanup.
- Never delete the user's original local file outside the project data folder.
- If a path is ambiguous, outside the expected known folder, missing, locked, or otherwise unsafe, do not delete it; return an error marker where appropriate.

Future OCR/CV cleanup should extend the same model with explicit artifact keys and dedicated cleanup controls. Expected future artifacts include `ocr_timeline.json` and `ocr_text.txt`, but OCR is not implemented yet.

### `app/audio_recorder.py`

Microphone recorder service.

Key behavior:

- Lists input devices.
- Starts microphone capture into `data\recordings`.
- Writes WAV chunks through a writer queue.
- Tracks RMS/peak level, silence warnings, duration, dropped chunks, and stream status.
- Supports microphone switching during recording.
- Reports levels from the active recording stream. When idle, level calls return a zero snapshot and must not open a microphone probe.

Do not change this module casually. Recording correctness depends on stream lifecycle, writer thread shutdown, queue limits, and locking.

### `app/system_audio_recorder.py`

Windows system audio recorder service using WASAPI loopback through `soundcard`.

Key behavior:

- Lists output devices.
- Starts system audio recording into `data\recordings`.
- Records in a worker thread.
- Supports output device switching while recording.
- Reports output level and silence warnings from the active recording stream. When idle, level calls return a zero snapshot and must not open a loopback probe.
- Initializes COM for loopback recording where needed.

This module is Windows-specific. Future screen recording work should not be mixed into this module; keep system audio capture and screen capture separate unless a later design explicitly merges them through a media session coordinator.

### `app/screen_recorder.py`

Screen recorder service for the Screen source MVP.

Key behavior:

- Lists physical displays through `mss.monitors[1:]`; `mss.monitors[0]` is the virtual all-monitor bounding box and is not treated as Display 1.
- Validates selected display indices and allowed FPS values: `1, 2, 3, 5, 10, 15, 20, 30`.
- Creates flat `data\recordings\session_YYYYMMDD_HHMMSS.json`.
- Starts capture in a background thread and rejects a second simultaneous screen recording.
- Writes one video file per selected display into `data\recordings`, trying MP4/`mp4v` first and falling back to AVI/`XVID` or AVI/`MJPG`.
- Uses output frame slots based on the selected FPS. If fresh capture cannot keep up, it writes the latest available frame again instead of lowering FPS or creating a shorter accelerated video.
- Draws a simple visible cursor marker into the video for the display containing the current cursor position. Cursor lookup failures are diagnostic warnings, not recording failures.
- Updates `session_*.json` from `recording` to `completed` or `failed`, including duration, codec, video filename, requested/written FPS, captured/written/duplicated frame counts, duplicate ratio, actual capture FPS, timing mode, timing warning, and cursor warning fields.
- References actual audio filenames when the screen recording was started with microphone and/or system audio.

The module lazy-imports `mss`, `cv2`, and `numpy` inside runtime capture paths so unit tests and basic app import do not require an active screen capture environment.

### Display Selection and Preview

Display enumeration comes from `mss.mss().monitors[1:]`. `mss.mss().monitors[0]` is the virtual all-monitor bounding box and is not exposed as a selectable physical display. The app stores and sends display metadata with:

- `index`: the screen/display identifier used by screen recording APIs and session `screen_index`;
- `width` and `height`: physical display capture size;
- `left` and `top`: virtual desktop coordinates, which can be negative on Windows multi-monitor layouts;
- `is_primary`: best-effort primary display marker.

The UI orders display cards by virtual desktop layout: first `top`, then `left`, then `index`. In a common two-monitor setup where the left monitor is `left=-1920, top=0` and the main/right monitor is `left=0, top=0`, the left monitor appears first and visually on the left side of the card grid.

`screen_index` in session JSON, video filenames, and mouse event metadata always refers to the display `index` from `/api/displays`, not the card's visual position after sorting. Mouse event `screen_index` uses the same coordinate bounds (`left`, `top`, `width`, `height`) to decide which recorded screen contains the cursor.

Preview thumbnails are manual and off by default. `POST /api/displays/preview` accepts:

```json
{
  "screen_index": 1,
  "max_width": 320
}
```

The endpoint captures the requested display with `mss`, resizes the image on the backend with OpenCV, encodes JPEG, and returns:

```json
{
  "screen_index": 1,
  "mime_type": "image/jpeg",
  "image_base64": "...",
  "image_data_url": "data:image/jpeg;base64,...",
  "width": 320,
  "height": 180,
  "source_width": 1920,
  "source_height": 1080
}
```

Preview screenshots are not written to `data\recordings`. Capture runs only when the user enables preview or presses Refresh preview. The endpoint clamps thumbnail width to a small range to avoid expensive large previews. Capture errors return structured API errors and should not crash the recording UI.

Future display identification improvements may include clearer physical monitor identification, temporary on-screen labels, slow live preview mode, and OS-provided monitor names when available.

### `app/input_event_recorder.py`

Input event recorder for screen media sessions.

Key behavior:

- Uses `pynput` for global mouse and keyboard listeners.
- Writes line-delimited UTF-8 JSON into `data\recordings`.
- Creates `mouse_events_YYYYMMDD_HHMMSS.jsonl` and `keyboard_events_YYYYMMDD_HHMMSS.jsonl` using the same timestamp as `session_YYYYMMDD_HHMMSS.json`.
- Keeps mouse and keyboard logging optional and tied to screen recording.
- Maps virtual desktop coordinates to selected recorded displays without assuming monitor coordinates start at `(0, 0)`.
- Records mouse positions at the selected screen FPS.
- Records mouse button down/up and scroll events as event-based callbacks.
- Records keyboard special keys, modifier keys, and hotkeys while suppressing ordinary typed text.
- Sanitizes listener startup errors for session JSON and never raises fatal errors back into screen/audio recording.

The module lazy-imports `pynput` only when logging is requested so the app and tests can import normally without active global hook support.

### Input Event Logging

Input event logging is an MVP metadata layer for screen recording sessions. It does not draw cursor trails, click pulses, OCR, CV, VLM analysis, or typed text.

#### Event Files

Event files live beside screen videos and session JSON in `data\recordings`:

- `mouse_events_YYYYMMDD_HHMMSS.jsonl`
- `keyboard_events_YYYYMMDD_HHMMSS.jsonl`

The timestamp is reused from the media session. Session JSON references these files:

```json
{
  "events": {
    "mouse": "mouse_events_20260610_143000.jsonl",
    "keyboard": "keyboard_events_20260610_143000.jsonl"
  },
  "event_logging": {
    "mouse_enabled": true,
    "keyboard_enabled": true,
    "mouse_status": "ok",
    "keyboard_status": "ok",
    "mouse_error": null,
    "keyboard_error": null
  }
}
```

When a source is disabled, its event file reference is `null` and its status is `disabled`. If a listener cannot start, the status is `failed`, the error is a short sanitized message, and any diagnostic JSONL event is best-effort only.

#### Timestamp Semantics

Every input event has `t`, a float number of seconds from the common screen recording/session start. This timeline is intended to be comparable to:

- screen video playback time;
- microphone/system audio timelines in the same session;
- future transcript, OCR, CV, and derived visual timelines.

#### Mouse Synchronization

Mouse position events are frame-based and sampled at the selected screen FPS:

```json
{"t":12.4,"type":"position","x":842,"y":514,"screen_index":1,"screen_status":"recorded_screen"}
```

Mouse button and scroll events are event-based and must preserve multiple actions between two frame samples:

```json
{"t":12.455,"type":"down","x":842,"y":514,"screen_index":1,"screen_status":"recorded_screen","button":"left"}
{"t":12.7,"type":"up","x":900,"y":514,"screen_index":1,"screen_status":"recorded_screen","button":"left"}
{"t":13.12,"type":"scroll","x":920,"y":600,"screen_index":1,"screen_status":"recorded_screen","dx":0,"dy":-3}
```

The MVP does not emit exact `frame_index` because screen frame writing and input sampling are separate threads. Future work can add exact frame IDs if the screen recorder exposes a safe shared frame clock.

#### Keyboard Synchronization

Keyboard events are event-based. The MVP records only:

- special keys such as Enter, Esc, Tab, Backspace, Delete, arrows, Home/End, PageUp/PageDown, and F1-F12;
- modifier key down/up events for Ctrl, Alt, Shift, and Win;
- hotkeys such as Ctrl+C, Ctrl+V, Ctrl+L, Ctrl+S, Alt+Tab, and Ctrl+Alt+Delete when detectable.

Ordinary typed text is not recorded. Plain letters, digits, and normal text input are suppressed. A letter or digit is logged only when combined with Ctrl, Alt, or Win, for example:

```json
{"t":2.135,"type":"hotkey","keys":["Ctrl","L"]}
{"t":2.84,"type":"hotkey","keys":["Ctrl","V"]}
{"t":3.2,"type":"key_down","key":"Enter"}
{"t":3.26,"type":"key_up","key":"Enter"}
```

Shift plus a plain letter is treated as text input and is not logged as a hotkey.

#### Multiple Screens

Mouse events include:

- `screen_index`: the recorded display index that contains the cursor, or `null`;
- `screen_status`: `recorded_screen` or `outside_recorded_screens`.

If the cursor is outside all selected displays, the event is still written and must not crash logging:

```json
{"t":20.2,"type":"position","x":-400,"y":500,"screen_index":null,"screen_status":"outside_recorded_screens"}
```

Display bounds use the monitor `left` and `top` values reported by `mss`, so negative virtual desktop coordinates are valid.

#### Future Derived Analysis

Click vs drag can be inferred from mouse `down`/`up` duration and cursor movement between those timestamps. A future analysis layer may derive a separate `visual_events.json` timeline from the raw JSONL inputs and screen video.

#### Future Backlog

- Cursor trail overlay:
  - draw a polyline over the last 1.0-1.5 seconds;
  - use actual mouse position snapshots;
  - make older segments more transparent;
  - add a click marker or pulse for 0.3-0.5 seconds.
- Pause/resume hotkeys:
  - Ctrl+Alt+F9;
  - Ctrl+Alt+F10.
- Optional typed text logging only as an explicit opt-in feature with separate UI consent and storage labeling.

#### Security and Fallback

Corporate security tools, antivirus, or EDR policies may block global input listeners. The app must continue recording screen/audio if mouse or keyboard listener startup fails. The short sanitized error belongs in `session_*.json` under `event_logging`; long stack traces should stay out of session metadata.

### `app/video_muxer.py`

Small FFmpeg wrapper for the manual "Merge video with audio" MVP.

Key behavior:

- Accepts one video filename and one or two optional audio filenames from `data\recordings`.
- Requires at least one audio file.
- Rejects path traversal, absolute paths, drive-letter paths, missing files, and unsupported suffixes.
- Uses `ffmpeg` from `PATH`; binaries are not bundled into the repository.
- Copies the video stream and encodes the output audio as AAC.
- For one audio file, maps that file as the output audio track.
- For two audio files, mixes mic/system into one track with `amix=inputs=2:duration=longest:normalize=0`.
- Saves `merged_<source>_YYYYMMDD_HHMMSS.mp4` into `data\recordings`.

### `app/queue_manager.py`

Sequential media processing queue.

Key behavior:

- Accepts local uploaded files, latest recordings, and URL sources.
- Marks local `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov` sources as video items.
- Creates one job JSON under `data\jobs`.
- Processes items sequentially in one worker thread.
- Supports stop-after-current, clear, retry failed items, pending-item removal, running transcription/frame-extraction cancellation, status snapshots, elapsed time, ETA, and persistent job snapshots.
- Treat the queue as a media processing queue, not only a transcription queue.
- Current executable operations are `transcribe_audio` and `extract_frames`.
- URL items are created as media processing items. By default they transcribe audio, keep frame extraction off, and carry default frame extraction settings for later opt-in when no frontend processing plan is supplied.
- Visible but disabled future operations are `ocr` and `cv`.
- Queue item status remains the behavior switch for existing logic. Stage fields are a small UI/status model layered on top: `stage`, `stage_label_key`, and `stage_detail`.
- Current stage IDs are `idle`, `waiting_download`, `preparing_source`, `downloading_media`, `downloading_video`, `cancelling_download`, `download_cancelled`, `download_failed`, `transcribing_audio`, `cancelling_transcription`, `extracting_frames`, `cancelling`, `completed`, `failed`, and `cancelled`.
- Active items expose one `stage_progress` object. `mode` is `determinate`, `indeterminate`, or `none`; determinate downloads may include percent/bytes/speed/ETA, and frame extraction may include completed/total units. Transcription stays indeterminate because the backend has no reliable segment total.
- Future reserved stage IDs are `ocr_pending_future`, `cv_pending_future`, and `media_index_pending_future`; they are labels only and must not imply OCR/CV/media-index implementation.
- Stores each item's actual processing plan in `processing_plan`. The current schema has `audio.enabled/model/device`, `frames.enabled/rate/interval_sec/jpeg_quality`, `ocr.enabled/engine/languages/status`, and `cv.enabled/engine/status`.
- Default processing settings are frontend state for now. The frontend sends a snapshot with each add-files/add-recordings/add-urls request, so defaults apply only to newly added items.
- Pending item edits update the item plan. Precedence is per-item `processing_plan` over defaults; legacy `operations` and `frame_extraction` are synchronized compatibility fields.
- `POST /api/queue/estimate-item` runs one pending-item runtime estimate at a time. Queue start, item edits/removal, retry, and clear are blocked until it finishes.
- Estimates always use the item's normalized `processing_plan`; defaults are relevant only through the legacy-plan normalization fallback.
- The runtime Model/Device/Compute type/Speed cards have one frontend renderer. During audio transcription they use the current item's audio plan plus matching resolved transcriber values; during non-audio queue stages they show not applicable, and while idle they show idle.
- Old queue items without `processing_plan` remain valid. The worker falls back to the queue start model/device and legacy operation/frame fields.
- Stores per-item operation choices in `operations`: `transcribe_audio`, `extract_frames`, `ocr`, and `cv`.
- Keeps OCR and CV as no-op placeholders in the backend. Incoming OCR/CV enabled flags are normalized back to disabled with `status=coming_soon`.
- Stores per-item frame settings in `frame_extraction`: extraction rate, JPEG quality, estimates, warning flag, and latest extraction result.
- Stores terminal output metadata in `outputs`: transcript path/existence, diagnostic JSON path/existence, frame folder path/existence, frame index path/existence, downloaded URL media path/existence/deleted marker, uploaded temp path/existence/deleted marker, and retention cleanup error markers.
- Calls the optional `retention_cleaner` callback only after a fully successful item. Failed, cancelled, and partial-success items keep intermediate files for debugging.
- Uses callbacks supplied by `app/main.py` to download URLs, transcribe files, extract frames, estimate runtimes, and record errors.

Future OCR/CV engines, media indexes, and RemoteBackend worker plans should extend `processing_plan` instead of adding another disconnected global selector. They must keep the compatibility fields stable until older job JSON and UI code no longer depend on them.

The queue intentionally processes one item at a time. This lowers CUDA memory pressure and keeps the UI progress model simple.

Stage labels are frontend-localized through `static/i18n.js`. Backend snapshots should send stable stage IDs and label keys, not hardcoded UI copy. Persistent stage messages belong in normal page content such as `#queueStageStatus` and `.queue-item-stage`; they must not be implemented only as auto-hiding toasts because the user needs to see the current long-running stage at any time.

Add-button safety lives primarily in `static/app.js`. The UI keeps `isAddingFile`, `isAddingUrl`, `isAddingRecording`, and `pendingAddKeys` guards so repeated clicks during a slow backend response do not enqueue duplicates. Browser file keys use file name, size, and `lastModified`; URL keys use normalized URL text; latest-recording keys use source type plus saved audio path. The backend also ignores active duplicate source paths and normalized URL adds as a secondary guard. Controls must be re-enabled in `finally` paths after success or failure.

Output artifacts are a compatibility layer, not a replacement for existing top-level result fields. Keep `transcript_path`, `json_path`, `frames_path`, `frames_index_path`, and downloaded media fields on the item for older code. Use `outputs` for user-facing artifact display and future artifact extensions. Future OCR should add keys such as `ocr_timeline_path`, `ocr_text_path`, and matching existence/deleted markers without changing existing transcript/frame keys.

### `app/runtime_estimate.py`

Runtime test-run service for pending queue items.

- Uses a default sample duration of 60 seconds and caps it to the source duration for shorter media.
- Uses `audio_duration_seconds()` with existing item/video metadata as fallback. Missing duration produces `duration_unavailable` rather than a misleading projection.
- Clips long audio/video sources to a temporary mono 16 kHz WAV through the existing FFmpeg dependency, then calls `AudioTranscriber` directly. It never calls `TranscriptStore`.
- Calls `VideoFrameExtractor.extract_sample()` with the item's frame rate and JPEG quality. Sample JPEGs are written only below the estimate workspace; no `frames_index.json` is created.
- Wraps all sample work in `TemporaryDirectory` under the project `tmp` directory. Temporary WAV/JPEG/scratch files must be removed on success and exception paths.
- URL items use an existing local `source_path`/downloaded media path only. The estimate endpoint does not start a URL download.
- Stores only a compact `estimate` object on the queue item. It does not alter item `status`, terminal outputs, transcript paths, or frame paths.

Current compact schema:

```json
{
  "estimate": {
    "status": "complete",
    "created_at": "2026-06-19T12:00:00+03:00",
    "sample_duration_sec": 60.0,
    "source_duration_sec": 1800.0,
    "approximate": true,
    "audio": {
      "enabled": true,
      "model": "small",
      "device": "auto",
      "effective_device": "cuda",
      "compute_type": "float16",
      "sample_runtime_sec": 8.4,
      "estimated_full_runtime_sec": 252.0,
      "speed_factor": 7.143
    },
    "frames": {
      "enabled": true,
      "rate": {"mode": "interval", "seconds": 30},
      "jpeg_quality": 75,
      "sample_frames": 3,
      "estimated_total_frames": 61,
      "sample_runtime_sec": 1.2,
      "estimated_full_runtime_sec": 24.4
    },
    "total_estimated_full_runtime_sec": 276.4
  }
}
```

Failures use `status=failed` plus a stable `error_code`; a plan with no enabled executable operations returns `status=complete` and `no_enabled_operations=true`. When OCR or CV processing is implemented, its estimator must be added in the same feature stage and included in the combined total without weakening the temporary-file rule.

### `app/frame_extractor.py`

OpenCV-backed video frame extraction for queue video items.

Key behavior:

- Supports `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov` through `config.SUPPORTED_VIDEO_EXTENSIONS`.
- Normalizes extraction rates to fixed interval values (`30`, `20`, `15`, `10`, `5`, `3`, `2`, `1` seconds) or FPS values (`2`, `3`, `5`, `10`, `15`, `20`, `30`).
- Defaults to one frame every `10` seconds and JPEG quality `90`.
- Available UI quality options include `75`, `80`, `85`, `90`, `95`, and `100`.
- JPEG quality `100` can create much larger files and usually should not be required for OCR/CV.
- Reads metadata with OpenCV: duration, FPS, width, height, and source frame count when available.
- Estimates output frame count and a rough min/max disk usage range from duration, dimensions, and quality.
- Writes each extraction to `data\recordings\<base>__frames`.
- Writes JPEGs as `frame_000001__t000000.000.jpg`, where `t` is seconds from video start.
- Writes and updates `frames_index.json` during processing, cancellation, completion, and failure.
- Accepts a cancellation event; cancellation preserves partial JPEGs and marks the index as `cancelled`.

The index payload has schema version `1` and includes:

```json
{
  "schema_version": 1,
  "status": "completed",
  "completed": true,
  "source_video": "clip.avi",
  "source_path": "data/uploads/clip.avi",
  "source_stem": "clip",
  "output_base": "clip_20260611_120000",
  "frames_dir": "clip_20260611_120000__frames",
  "frames_path": "data/recordings/clip_20260611_120000__frames",
  "extraction": {
    "mode": "interval",
    "seconds": 10,
    "requested_fps": null,
    "jpeg_quality": 90
  },
  "video_metadata": {
    "duration_sec": 31.0,
    "fps": 30.0,
    "width": 1920,
    "height": 1080,
    "frame_count": 930
  },
  "estimated_frame_count": 4,
  "extracted_frame_count": 4,
  "requested_fps_exceeds_source_fps": false,
  "frames": [
    {
      "index": 1,
      "t": 0.0,
      "file": "frame_000001__t000000.000.jpg",
      "width": 1920,
      "height": 1080
    }
  ]
}
```

On cancellation, `status` is `cancelled`, `completed` is `false`, `cancelled` is `true`, and `cancelled_at_t` records the next timestamp that would have been processed. On failure, `status` is `failed` and `error_message` is populated.

### `app/transcriber.py`

Whisper transcription service.

Key behavior:

- Wraps `faster_whisper.WhisperModel`.
- Caches one model instance by model/device/compute configuration.
- Supports `auto`, `cpu`, and `cuda` device preferences.
- Falls back from auto/CUDA candidates according to config.
- Stores model caches under `models\faster-whisper`.
- Checks `ffmpeg` before transcribing media formats that need decoding.
- Returns text, segments, timings, realtime factor, model, device, and compute metadata.
- Accepts an optional cancellation callback from the queue. The callback is checked before segment iteration and between yielded segments; cancellation returns a `cancelled` / `partial` result instead of raising or killing the worker thread.

Use the existing normalization and model-loading helpers when adding new transcription paths.

Transcription cancellation lifecycle:

- `QueueManager.cancel_item()` accepts the active item while its status is `extracting_audio`, `transcribing`, or `extracting_frames`.
- For transcription, the queue stores a per-item `threading.Event`, sets `cancel_requested`, and moves the visible stage to `cancelling_transcription`.
- The frontend disables the current item's cancel button immediately, retains that pending state through polling via `cancel_requested`, and does not send duplicate cancellation requests.
- `app/main.py` passes `cancel_event.is_set` into `AudioTranscriber.transcribe()` as `should_cancel`.
- `AudioTranscriber` checks the callback before invoking segment iteration and between segments. It must not use unsafe Python thread termination.
- A cancelled transcription returns partial segment data with `cancelled=True`, `partial=True`, and a cancellation reason.
- `TranscriptStore.save_cancelled()` writes any recognized text to a transcript whose name contains `__partial_cancelled__`, and writes JSON with `status: "cancelled"`, `partial: true`, and `cancelled: true`.
- The queue marks the item `cancelled`, refreshes `outputs.transcript_partial`, skips frame extraction for that item, and continues with the next pending item.
- Frame extraction keeps its existing cancellation lifecycle: the frame processor receives a cancellation event, preserves partial JPEGs, marks `frames_index.json` as cancelled/incomplete, and the queue continues.

### `app/model_manager.py`

Whisper model management service for the UI.

Key behavior:

- Lists the supported models from `config.SUPPORTED_WHISPER_MODELS`.
- Detects local faster-whisper snapshots under `models\faster-whisper` without loading every model.
- Starts one background model download at a time through faster-whisper's Hugging Face download helper.
- Reports download status with an indeterminate progress fallback when exact percent is unavailable.
- Keeps model setup states non-conflicting: not downloaded, downloading, verifying, ready, or failed. Ready and failed terminal states are inactive and do not carry stale download progress.
- Returns static model metadata for the Info button.
- Deletes only exact cache paths for the selected supported model, including the matching `.locks` entry when present.
- Refuses invalid model names and confirmation-less deletes.

Deletion must stay conservative. Do not delete `models`, `models\huggingface`, or the whole Hugging Face cache from this service. If future custom model directories are added, extend the safety checks before exposing delete controls for those paths.

### `app/transcript_store.py`

Transcript and metadata persistence.

Key behavior:

- Saves successful transcripts as TXT plus JSON metadata.
- Saves error metadata JSON for failed work.
- Saves benchmark transcripts and benchmark timing JSON.
- Sanitizes source names for Windows-safe filenames.
- Preserves URL metadata such as source URL, platform, title, and downloaded audio path.

Future media-session outputs should probably add new metadata fields here or in a new session store, rather than overloading unrelated transcript fields.

### `app/benchmark_service.py`

Asynchronous benchmark runner.

Key behavior:

- Registers an uploaded benchmark source.
- Runs CPU or CUDA cold/warm benchmark work in a background thread.
- Uses `AudioTranscriber` and `TranscriptStore`.
- Clears cached model state for cold runs.
- Requires a compatible cold run before warm runs.

Benchmarks are deliberately separate from the queue.

### `app/url_downloader.py`

URL downloader/extractor.

Key behavior:

- Detects direct media URLs by path extension; query strings are ignored.
- Downloads direct `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov` URLs over HTTP(S) without `yt-dlp`.
- Uses `yt-dlp` for webpage/video-platform URLs such as YouTube or VK.
- Accepts public HTTP(S) URLs.
- Downloads direct media or extracts platform audio/video to `data\downloads`.
- Accepts a cancellation event and progress callback for both direct and `yt-dlp` downloads.
- Direct downloads stream into a unique `.part` path, report real byte progress from `Content-Length` when available, and atomically rename only after a non-empty successful download.
- `yt-dlp` uses progress hooks for bytes/total/speed/ETA and postprocessor hooks for cancellation checks. Unknown totals remain indeterminate rather than using a fabricated percentage.
- Cancellation raises `UrlDownloadCancelled`; the queue maps it to `download_cancelled` without creating a normal error artifact and continues to the next item.
- Cancellation/failure cleanup only removes downloader-owned files inside the configured downloads directory. If a locked `yt-dlp` file cannot be deleted, cleanup attempts to quarantine it with a `.partial` suffix. Prefix cleanup never traverses or deletes outside that directory.
- Returns source metadata to the queue and transcript store.
- Keeps raw downloader failures in technical details while exposing readable queue errors for timeout and authorization/cookies cases.

Progress callback schema:

```json
{
  "mode": "determinate",
  "percent": 43.2,
  "downloaded_bytes": 12345678,
  "total_bytes": 28765432,
  "speed_bytes_per_sec": 123456,
  "eta_sec": 132,
  "source": "direct"
}
```

Direct download behavior is tested with mocked HTTP responses. Platform downloads are best-effort and depend on the installed `yt-dlp` version and platform support; cookies/browser-auth support remains future work. This stage does not redesign model download progress; model lifecycle progress remains owned by `model_manager.py` and its existing UI.

## Frontend Files

### `static/index.html`

Static DOM contract for the UI.

Important areas:

- Header and language switch.
- Global transcription settings.
- Whisper model manager table below transcription settings.
- Recording section with microphone, system audio, screen, coordinate-ordered display cards, FPS, mouse action, keyboard action, and per-display preview controls.
- Recording device selectors, display selectors, and level meters.
- Help section.
- Queue/source forms.
- Manual video/audio merge form.
- Runtime metrics and queue progress.
- Collapsible file storage section with a storage overview panel, retention settings, safe downloads/uploads cleanup, and compact scrollable recordings/transcripts lists.
- Collapsible benchmark section.

The contract tests look for specific IDs, order, and structural elements. Keep ID changes deliberate and update tests only when the product contract truly changes.

### `static/app.js`

Main browser controller.

Responsibilities:

- Bind DOM elements.
- Call backend APIs.
- Manage recording, device refresh/switching, level polling, Whisper model manager actions, queue actions, storage size/settings/cleanup display, video/audio merge actions, benchmark actions, toasts, operation overlay, and transcript loading.
- Use `window.LATI18N` for UI strings and backend text translation.
- Start the product tour through `window.LocalMediaTranscriberTour`.

Avoid embedding Russian text in this file. Dynamic UI text should go through `static/i18n.js`.

### `static/i18n.js`

RU/EN localization dictionaries and translation helpers.

Important details:

- Default UI language is `ru`.
- Storage key is currently `latUiLanguage`; keep it unless there is a migration plan.
- RU and EN dictionaries must have matching keys.
- `translateText` maps backend Russian messages to English when the UI language is EN.

When adding UI text, add both RU and EN dictionary keys. When adding backend messages that surface to users, add translation pairs if English UI should display them.

### `static/style.css`

Light UI styling and project color identity.

Current LocalMediaTranscriber palette:

- Primary: `#2563eb`
- Primary dark: `#1d4ed8`
- Accent: `#7c3aed`
- Soft background: `#f8fafc`
- Card border / soft blue: `#dbeafe`

Status colors are intentionally separate:

- Success: `#147843`
- Warning: `#946200`
- Error: `#b42318`

Keep the UI light and readable. Avoid radical layout changes until the Compact Media Recording UI iteration is explicitly requested.

### `static/tour.js`

Guided tour controller.

Responsibilities:

- Defines tour steps against existing DOM IDs.
- Shows first-run prompt.
- Persists tour completion state.
- Exposes `window.LocalMediaTranscriberTour`.

If DOM IDs change, update tour selectors and `tests/test_ui_contract.py`.

### `static/icons`

Browser tab/app icon assets.

- `favicon.svg` is the current scalable favicon and is linked from `static/index.html`.
- If a PNG fallback is added later, prefer `favicon-32x32.png` and add the matching `<link rel="icon">`.
- Future replacement sets can also include 16x16, 48x48, and 180x180 Apple touch icon files.
- To change the browser tab icon, replace the files while keeping the same filenames or update the `<link rel="icon">` tags.

## Current Media Recording Flow

1. The frontend loads storage, devices, model status, and initial state.
2. The user selects recording sources: `mic`, `system`, `screen`, optional mouse actions, optional keyboard actions, or a supported combination.
3. If Screen is enabled, the UI shows coordinate-ordered physical display cards, optional manual preview controls, the screen FPS selector, and mouse/keyboard action logging controls.
4. Before recording starts, the frontend must not poll microphone or system capture endpoints. Idle level meters show localized inactive messages.
5. `POST /api/record/start` validates the selected sources and checks for conflicting benchmark work.
6. If screen is enabled, the backend validates display selection and FPS before opening audio streams.
7. For `mic`, `AudioRecorder.start()` creates `mic_<timestamp>.wav`.
8. For `system`, `SystemAudioRecorder.start()` creates `system_<timestamp>.wav`.
9. For `mic` + `system`, both recorders start with the same timestamp and save separate files. They are not mixed.
10. Display preview, if used, captures only manual thumbnails through `/api/displays/preview` and does not write preview files to disk.
11. For `screen`, `ScreenRecorder.start()` creates flat screen video files and `session_YYYYMMDD_HHMMSS.json` in `data\recordings`.
12. If mouse or keyboard action logging is enabled, `InputEventRecorder` creates JSONL event files with the same timestamp and updates `events` / `event_logging` in session JSON.
13. If audio and screen are recorded together, the screen session JSON references the actual audio filenames.
14. Screen videos use the selected FPS as the `VideoWriter` FPS. When capture falls behind, the latest captured frame is duplicated into missing output frame slots so playback duration remains real time.
15. A simple cursor marker is drawn into the display video that currently contains the cursor.
16. While recording, the UI polls level endpoints only for active audio sources and shows level meters, screen selection state, input logging state when available, and a timer.
17. Device switch endpoints can update microphone or output device during recording.
18. `POST /api/record/stop` stops the active recorder(s), gathers diagnostics, updates the latest recording references, and refreshes storage.

Audio files, screen videos, input event JSONL files, merged videos, and new screen session JSON all live in `data\recordings` as a flat list. `data\media_sessions` is legacy-only for earlier MVP runs.

### Microphone stream lifecycle

- Idle UI, queue polling, storage polling, model polling, and device list refresh must not open microphone streams.
- `static/app.js` gates microphone level polling with `recordingUsesMicInput()` and system loopback level polling with `recordingUsesSystemAudio()`.
- `getUserMedia({ audio: ... })`, browser `AudioContext` mic analysis, `sd.rec`, or loopback probes must not run on page load or queue polling.
- The microphone stream is opened only by `POST /api/record/start` when the selected recording mode includes `mic` or `both`.
- `POST /api/record/stop`, failed start cleanup, and runtime device switching must stop and close replaced streams before discarding references.
- If a future explicit microphone test/preview is added, it must have clear start/stop controls and stop every media track or backend stream when stopped.
- Manual Windows verification: open the app and wait 1-2 minutes without recording, then process local/URL queue items. The Windows microphone tray icon should not appear or blink. Start mic recording to verify the icon appears, then stop and verify it disappears shortly after the recorder stops.

`GET /api/storage` exposes only user-facing recordings in the normal recordings file list: `.wav`, `.mp3`, `.m4a`, `.mp4`, `.avi`, `.mkv`, `.webm`, `.flac`, and `.ogg`. Service metadata such as `session_*.json`, `.log`, `.tmp`, and `.pyc` remains on disk but is hidden from the regular UI list.

## Current Video Mux Flow

1. The frontend loads recent user-facing `data\recordings` media files from `/api/storage`.
2. The "Merge video with audio" form lists recent video files and audio files from that directory.
3. The user selects one video and one or two audio files.
4. `POST /api/video-mux/merge` validates that every selected file is a simple filename inside `data\recordings`.
5. `VideoMuxer` requires `ffmpeg` in `PATH`.
6. One audio file is mapped as the output audio track. Two audio files are mixed into one AAC track.
7. The output MP4 is saved back into `data\recordings`.

## Current Media Processing Queue Flow

1. The user adds sources to the queue:
   - latest microphone/system recordings through `/api/queue/add-recordings`;
   - selected local files through `/api/queue/add-files`;
   - public URLs through `/api/queue/add-urls`.
2. `QueueManager` creates or updates a job under `data\jobs`.
3. Video items receive default operations: `transcribe_audio=true`, `extract_frames=false`, `ocr=false`, and `cv=false`.
4. Before the queue starts, the UI can call `/api/queue/update-item` to change video operations and frame extraction settings.
5. Before the queue starts, or while another item is running, pending items can be removed through `/api/queue/remove-item`.
6. While the queue is idle, `/api/queue/estimate-item` can test a pending local item's enabled audio/frame operations in a temporary workspace and attach compact estimate metadata without changing the item result state.
7. The user starts the queue with `/api/queue/start`, passing the selected model and device preference.
8. Queue settings are frozen for that run.
9. A single worker thread processes items in order.
10. The UI polls `/api/queue/status` and renders persistent stage status. Stage labels come from `static/i18n.js`, and stage text must stay visible for the whole active stage.
11. URL items are downloaded/extracted through `UrlDownloader` before processing.
12. For URL audio-only transcription, `UrlDownloader.download()` downloads direct media URLs directly; non-direct URLs keep the stable `yt-dlp` audio-only extraction path.
13. For URL frame extraction, `UrlDownloader.download_video()` downloads direct media URLs directly or asks `yt-dlp` for a video-readable media file under `data\downloads`; the queue reuses it for frame extraction and, when selected, transcription.
14. For audio transcription, files are validated and passed to `AudioTranscriber`; `TranscriptStore` saves TXT and JSON outputs.
15. For frame extraction, `VideoFrameExtractor` writes JPEGs and `frames_index.json` under `data\recordings\<base>__frames`.
16. A running item can be cancelled while its status is `downloading`, `extracting_audio`, `transcribing`, or `extracting_frames`; cancellation is cooperative and the worker continues to the next pending item.
17. Transcription cancellation may wait for the current model-loading step or Whisper segment to finish. Partial transcripts are saved with a `__partial_cancelled__` marker and cancelled/partial JSON metadata. Frame extraction cancellation keeps partial frames and marks `frames_index.json` cancelled/incomplete.
18. URL download cancellation signals the active downloader event, moves the item through `cancelling_download` to `download_cancelled`, cleans partial files, and continues the queue.
19. On full success only, `StorageManager.apply_retention_cleanup()` may delete downloaded URL media or uploaded temp files when the user disabled the matching keep setting. It never deletes primary outputs.
20. Terminal queue items refresh `outputs` so the UI can show created artifacts, missing/deleted markers, and cleanup errors directly on the item card.
21. Queue status shows counts, current item, current stage, elapsed time, ETA, progress, operation settings, estimates, downloaded media paths, transcript output paths, frame folder paths, frame counts, frame index paths, and output artifacts.
22. `stop-after-current` completes the active item and cancels pending items.
23. `retry-errors` moves failed items back to pending for a later manual start.

Stage transitions are intentionally coarse and persistent:

- pending local item: `idle`;
- pending URL item: `waiting_download`;
- local item setup and post-download metadata/duration checks: `preparing_source`;
- URL audio/media download: `downloading_media`;
- URL video-readable download for frame extraction: `downloading_video`;
- requested URL download cancellation: `cancelling_download`;
- terminal URL download states: `download_cancelled` or `download_failed`;
- audio extraction/transcription: `transcribing_audio`;
- requested transcription cancellation: `cancelling_transcription`;
- frame extraction: `extracting_frames`;
- requested frame extraction cancellation: `cancelling`;
- terminal item states: `completed`, `failed`, or `cancelled`.

The queue is intentionally sequential. Do not parallelize transcription or frame extraction without a separate design for GPU memory, disk pressure, cancellation, UI status, and job persistence.

Current output relationship:

```text
source video
  -> audio transcript in data/transcripts
  -> frames folder in data/recordings/<base>__frames/
  -> frames_index.json inside frames folder
```

Outputs are not physically unified into one folder yet. The queue derives a shared source/output base so transcript names, frame folders, and future derived artifacts remain visibly related. Future OCR/CV outputs and any combined media index should keep using the same source/output base naming.

URL output relationship:

```text
direct media URL
  -> direct HTTP download in data/downloads
  -> transcript and/or frame extraction

webpage/video-platform URL
  -> yt-dlp download/extraction in data/downloads
  -> transcript and/or frame extraction

URL source
  -> downloaded media file in data/downloads
  -> transcript in data/transcripts
  -> frames folder in data/recordings/<base>__frames
  -> frames_index.json
  -> future ocr_timeline.json
  -> future cv_timeline.json
  -> future combined media index
```

URL frame indexes can include `source_type`, `source_url`, source title/platform, and downloaded media paths when that metadata is available. Direct URL extension detection ignores query strings, so `video.mp4?token=abc` is treated as a direct `.mp4` file. If transcription succeeds and frame extraction fails, the transcript path remains on the queue item. If transcription fails but frame extraction was selected, the worker still attempts frame extraction and preserves frame outputs if they succeed. OCR, CV, cookies/authentication, playlists, and video quality selection remain non-goals.

Manual cancellation checklist:

- Normal local audio/video transcription still completes and shows transcript + JSON artifacts.
- Cancelling a long transcription shows `cancelling_transcription`, then a cancelled item with a partial transcript marker when text was recognized.
- After cancelling the first of two queued items, the second pending item runs normally.
- Frame extraction cancellation still preserves partial frames and cancelled index metadata.
- Cancelling a direct or `yt-dlp` download shows `cancelling_download`, removes downloader-owned partial files, marks the item `download_cancelled`, and continues to the next pending item.
- URL transcription can be cancelled after download when the item is in transcription.

Manual cleanup for `data\downloads` and `data\uploads` is separate from queue retention. It is user-triggered, confirmed in the UI, and returns deleted counts plus per-entry errors. Do not add destructive cleanup for `data\recordings` or `data\transcripts` without a separate product requirement.

## Development Cleanup

Use `run.bat` for normal local startup. It prints a shutdown hint after the server command exits; if Ctrl+C or a closed console leaves stale locks, use the scoped cleanup scripts.

Current script chain:

```text
run.bat
stop.bat
cleanup-dev.bat
scripts/cleanup_dev.ps1
```

`stop.bat` is the user-facing stop command. It calls `scripts\cleanup_dev.ps1 -StopOnly` and only stops Python/uvicorn processes whose command line references the resolved `C:\Python\LocalMediaTranscriber` project root. It must not kill unrelated `python.exe` processes.

`cleanup-dev.bat` calls `scripts\cleanup_dev.ps1` without `-StopOnly`. It:

- stops project-scoped Python/uvicorn server processes;
- removes `__pycache__` directories under `app`, `tests`, and `scripts`;
- removes project `.pytest_cache` when present;
- removes `.git\index.lock` only when no active `git.exe`, `ssh.exe`, `gpg.exe`, or `codex.exe` command line references this repository;
- prints `git status --short` at the end.

The PowerShell script uses command-line filtering because process names alone are too broad. If process command lines cannot be read, the script refuses to guess and reports that limitation.

Before commit, if Git lock or cache issues appear, `cleanup-dev.bat` is the correct tool.

## RU/EN Localization Notes

- All static UI labels should live in `static/i18n.js`.
- Any new visible UI text must use the existing i18n mechanism. Do not hardcode user-facing labels directly in HTML or JS unless this is already the established pattern and both RU/EN variants remain supported.
- `static/index.html`, `static/app.js`, and `static/tour.js` should not embed Russian user-facing text.
- Keep RU and EN dictionary keys identical.
- For new dynamic keys used by `t("key")`, make sure tests can find the key in both dictionaries.
- For backend messages that users see through toast/output fields, add English translations to `textPairs`.
- The UI language switch changes interface language only. It does not set Whisper speech language.
- Whisper speech language is controlled by `WHISPER_LANGUAGE`; empty means faster-whisper auto-detects.

## Testing Notes

Light checks for small UI/docs iterations:

```bat
.venv\Scripts\python.exe -m compileall app
.venv\Scripts\python.exe -m unittest tests.test_i18n tests.test_ui_contract
.venv\Scripts\python.exe -m unittest tests.test_frame_extractor
.venv\Scripts\python.exe -m unittest tests.test_model_manager
.venv\Scripts\python.exe -m unittest tests.test_file_listing tests.test_dev_cleanup_scripts
.venv\Scripts\python.exe -m unittest tests.test_screen_recorder
.venv\Scripts\python.exe -m unittest tests.test_video_muxer
.venv\Scripts\python.exe -m unittest tests.test_queue_manager tests.test_media_validation
git diff --check
git diff --stat
git status
```

Do not run full `unittest discover` unless the task asks for it or the change affects broader backend behavior.

Useful targeted tests:

- `tests.test_i18n`: localization key contract and no Russian static markup in selected frontend files.
- `tests.test_ui_contract`: DOM IDs, queue endpoint usage, section order, and tour selectors.
- `tests.test_model_manager`: model cache status, safe delete behavior, download-status shape, and mocked verification endpoint behavior.
- `tests.test_file_listing`: media-only recordings list suffix contract.
- `tests.test_dev_cleanup_scripts`: cleanup entrypoint existence and project-scoped safety markers.
- `tests.test_screen_recorder`: screen FPS/display validation, media session JSON, and lightweight API validation.
- `tests.test_video_muxer`: FFmpeg command construction, path validation, audio-required validation, and missing-FFmpeg handling.
- `tests.test_frame_extractor`: video metadata, estimates, JPEG output, index persistence, and cancellation.
- `tests.test_queue_manager`: queue behavior, video item operation settings, pending removal, and frame extraction cancellation.
- `tests.test_transcript_store`: transcript filename and metadata persistence.
- `tests.test_media_validation`: supported media validation.
- `tests.test_url_downloader`: URL downloader logic.
- `tests.test_benchmark_service`: benchmark state behavior.

Manual checks after UI-facing changes:

- Start through `run.bat`.
- Confirm the header says `Local Media Transcriber`.
- Confirm the blue-violet palette is visible and readable.
- Confirm old UI sections are still present.
- Confirm microphone recording is available.
- Confirm system audio recording is available.
- Confirm transcription queue controls are available.
- Confirm RU/EN switching works.

## Dependency Management

- Always use the project `.venv`.
- Do not install dependencies globally.
- Do not install dependencies into `C:\Python\LocalAudioTranscriber`.
- For CPU/base dependencies, update `requirements-cpu.txt`.
- For GPU/CUDA setup changes, update `requirements-gpu.txt`; screen-runtime dependencies are mirrored there for this fork.
- If a new feature needs dependencies, install them only inside `C:\Python\LocalMediaTranscriber\.venv`.
- Keep runtime caches and temporary files inside the project folder where possible.
- FFmpeg is an external executable expected in `PATH` for media decoding and video/audio muxing. Do not bundle FFmpeg binaries into this repository.

Preferred setup:

```bat
cd /d C:\Python\LocalMediaTranscriber
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-cpu.txt
```

GPU add-ons:

```bat
pip install -r requirements-gpu.txt
```

## Fork Safety Rules

- Work only in `C:\Python\LocalMediaTranscriber`.
- Do not modify `C:\Python\LocalAudioTranscriber`.
- Do not modify other projects in `C:\Python`.
- Keep this fork's docs, UI identity, color palette, and requirements separate from LocalAudioTranscriber.
- Do not perform broad backend module renames just to match the new product name.
- Preserve existing microphone, system audio, queue, and runtime switching behavior unless the task explicitly asks to change it.

## Roadmap

Planned product direction:

1. Compact Media Recording UI.
2. Source checkboxes: microphone, system, screen.
3. Screen recording MVP.
4. Media session structure.
5. Multiple screens saved as separate video files.
6. Mouse events MVP.
7. Keyboard events MVP with a clear privacy warning.
8. Advanced keyframe selection.
9. OCR.
10. VLM.
11. Local/server processing modes.
12. Possible pay-as-you-go server processing.

Suggested implementation shape for future media work:

- Keep existing audio recorders as independent services.
- Add a media-session coordinator instead of merging screen recording into audio recorder modules.
- Store session metadata separately from transcript metadata at first.
- Add tests around session metadata before adding OCR/VLM processing.

## Current No-Go List

Do not add these until explicitly requested:

- OCR, VLM, advanced keyframe selection, or scene detection.
- Cursor trail overlays, click pulse overlays, or typed text logging.
- Automatic audio/video muxing at stop time or a complex timeline editor.
- A complex media-session editor/viewer.
- Backend audio recording logic changes.
- Transcription queue logic changes.
- API endpoint changes without a product need.
- Compact Media UI.
- Server processing.
- Installer or EXE packaging.
