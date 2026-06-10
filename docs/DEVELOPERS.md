# Developer's Guide

This guide is the technical handoff for future LocalMediaTranscriber iterations. It describes the current fork, the existing audio/transcription architecture, and the rules for safe development.

## Project Purpose

LocalMediaTranscriber is a local Windows app for recording and transcribing media. Today it is still close to its source fork, LocalAudioTranscriber: it records microphone audio, records system audio through WASAPI loopback, and transcribes audio or audio tracks from supported media files with `faster-whisper`.

The product direction is broader than audio-only transcription. Future iterations should evolve toward media sessions that can combine microphone audio, system audio, screen video, keyframes, OCR, and VLM analysis while preserving the stable audio recording and queue behavior already present.

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
transcriber = AudioTranscriber()
model_manager = WhisperModelManager()
transcript_store = TranscriptStore()
```

Queue and benchmark services use these shared objects. This keeps model caching and recording state centralized, but it also means future changes should be careful with threading, locks, and shared mutable state.

## Important Folders and Files

- `app`: Python backend modules.
- `static`: Browser UI assets.
- `tests`: Focused unit and contract tests.
- `data\recordings`: WAV files created by microphone and system audio recording, screen video files, flat screen `session_*.json` files, and merged video outputs.
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
- `POST /api/queue/start`
- `POST /api/queue/stop-after-current`
- `POST /api/queue/clear`
- `POST /api/queue/retry-errors`
- `GET /api/queue/status`
- `POST /api/benchmark/upload`
- `POST /api/benchmark/run`
- `GET /api/benchmark/status`

The older direct transcription endpoints still exist in the backend, but the current UI uses the queue endpoints for normal transcription work.

### `app/audio_recorder.py`

Microphone recorder service.

Key behavior:

- Lists input devices.
- Starts microphone capture into `data\recordings`.
- Writes WAV chunks through a writer queue.
- Tracks RMS/peak level, silence warnings, duration, dropped chunks, and stream status.
- Supports microphone switching during recording.
- Provides level probes before and during recording.

Do not change this module casually. Recording correctness depends on stream lifecycle, writer thread shutdown, queue limits, and locking.

### `app/system_audio_recorder.py`

Windows system audio recorder service using WASAPI loopback through `soundcard`.

Key behavior:

- Lists output devices.
- Starts system audio recording into `data\recordings`.
- Records in a worker thread.
- Supports output device switching while recording.
- Measures output level and reports silence warnings.
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

Sequential global transcription queue.

Key behavior:

- Accepts local uploaded files, latest recordings, and URL sources.
- Creates one job JSON under `data\jobs`.
- Processes items sequentially in one worker thread.
- Supports stop-after-current, clear, retry failed items, status snapshots, elapsed time, ETA, and persistent job snapshots.
- Uses callbacks supplied by `app/main.py` to download URLs, transcribe files, and record errors.

The queue intentionally processes one item at a time. This lowers CUDA memory pressure and keeps the UI progress model simple.

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

Use the existing normalization and model-loading helpers when adding new transcription paths.

### `app/model_manager.py`

Whisper model management service for the UI.

Key behavior:

- Lists the supported models from `config.SUPPORTED_WHISPER_MODELS`.
- Detects local faster-whisper snapshots under `models\faster-whisper` without loading every model.
- Starts one background model download at a time through faster-whisper's Hugging Face download helper.
- Reports download status with an indeterminate progress fallback when exact percent is unavailable.
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

URL audio downloader/extractor.

Key behavior:

- Uses `yt-dlp`.
- Accepts public HTTP(S) URLs.
- Downloads or extracts audio to `data\downloads`.
- Returns source metadata to the queue and transcript store.

This is best-effort and depends on the installed `yt-dlp` version and platform support.

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
- Collapsible file storage section with compact scrollable recordings/transcripts lists.
- Collapsible benchmark section.

The contract tests look for specific IDs, order, and structural elements. Keep ID changes deliberate and update tests only when the product contract truly changes.

### `static/app.js`

Main browser controller.

Responsibilities:

- Bind DOM elements.
- Call backend APIs.
- Manage recording, device refresh/switching, level polling, Whisper model manager actions, queue actions, storage display, video/audio merge actions, benchmark actions, toasts, operation overlay, and transcript loading.
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
4. The frontend polls microphone and/or system levels according to the selected audio sources.
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
16. While recording, the UI shows level meters, screen selection state, input logging state when available, and a timer.
17. Device switch endpoints can update microphone or output device during recording.
18. `POST /api/record/stop` stops the active recorder(s), gathers diagnostics, updates the latest recording references, and refreshes storage.

Audio files, screen videos, input event JSONL files, merged videos, and new screen session JSON all live in `data\recordings` as a flat list. `data\media_sessions` is legacy-only for earlier MVP runs.

`GET /api/storage` exposes only user-facing recordings in the normal recordings file list: `.wav`, `.mp3`, `.m4a`, `.mp4`, `.avi`, `.mkv`, `.webm`, `.flac`, and `.ogg`. Service metadata such as `session_*.json`, `.log`, `.tmp`, and `.pyc` remains on disk but is hidden from the regular UI list.

## Current Video Mux Flow

1. The frontend loads recent user-facing `data\recordings` media files from `/api/storage`.
2. The "Merge video with audio" form lists recent video files and audio files from that directory.
3. The user selects one video and one or two audio files.
4. `POST /api/video-mux/merge` validates that every selected file is a simple filename inside `data\recordings`.
5. `VideoMuxer` requires `ffmpeg` in `PATH`.
6. One audio file is mapped as the output audio track. Two audio files are mixed into one AAC track.
7. The output MP4 is saved back into `data\recordings`.

## Current Transcription Queue Flow

1. The user adds sources to the queue:
   - latest microphone/system recordings through `/api/queue/add-recordings`;
   - selected local files through `/api/queue/add-files`;
   - public URLs through `/api/queue/add-urls`.
2. `QueueManager` creates or updates a job under `data\jobs`.
3. The user starts the queue with `/api/queue/start`, passing the selected model and device preference.
4. Queue settings are frozen for that run.
5. A single worker thread processes items in order.
6. URL items are downloaded/extracted through `UrlDownloader` before transcription.
7. Files are validated and passed to `AudioTranscriber`.
8. `TranscriptStore` saves TXT and JSON outputs.
9. Queue status is polled by the UI and shows counts, current item, elapsed time, ETA, and progress.
10. `stop-after-current` completes the active item and cancels pending items.
11. `retry-errors` moves failed items back to pending for a later manual start.

The queue is intentionally sequential. Do not parallelize transcription without a separate design for GPU memory, cancellation, UI status, and job persistence.

## Development Cleanup

Use `run.bat` for normal local startup. It prints a shutdown hint after the server command exits; if Ctrl+C or a closed console leaves stale locks, use the scoped cleanup scripts.

`stop.bat` is the user-facing stop command. It calls `scripts\cleanup_dev.ps1 -StopOnly` and only stops Python/uvicorn processes whose command line references the resolved `C:\Python\LocalMediaTranscriber` project root. It must not kill unrelated `python.exe` processes.

`cleanup-dev.bat` calls the same PowerShell script without `-StopOnly`. It:

- stops project-scoped Python/uvicorn server processes;
- removes `__pycache__` directories under `app`, `tests`, and `scripts`;
- removes project `.pytest_cache` when present;
- removes `.git\index.lock` only when no active `git.exe`, `ssh.exe`, `gpg.exe`, or `codex.exe` command line references this repository;
- prints `git status --short` at the end.

The PowerShell script uses command-line filtering because process names alone are too broad. If process command lines cannot be read, the script refuses to guess and reports that limitation.

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
.venv\Scripts\python.exe -m unittest tests.test_model_manager
.venv\Scripts\python.exe -m unittest tests.test_file_listing tests.test_dev_cleanup_scripts
.venv\Scripts\python.exe -m unittest tests.test_screen_recorder
.venv\Scripts\python.exe -m unittest tests.test_video_muxer
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
- `tests.test_queue_manager`: queue behavior.
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
8. Keyframes.
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

- OCR, VLM, keyframe extraction, or scene detection.
- Cursor trail overlays, click pulse overlays, or typed text logging.
- Automatic audio/video muxing at stop time or a complex timeline editor.
- A complex media-session editor/viewer.
- Backend audio recording logic changes.
- Transcription queue logic changes.
- API endpoint changes without a product need.
- Compact Media UI.
- Server processing.
- Installer or EXE packaging.
