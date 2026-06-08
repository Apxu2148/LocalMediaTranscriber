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
transcriber = AudioTranscriber()
transcript_store = TranscriptStore()
```

Queue and benchmark services use these shared objects. This keeps model caching and recording state centralized, but it also means future changes should be careful with threading, locks, and shared mutable state.

## Important Folders and Files

- `app`: Python backend modules.
- `static`: Browser UI assets.
- `tests`: Focused unit and contract tests.
- `data\recordings`: WAV files created by microphone and system audio recording.
- `data\uploads`: Files uploaded through the UI for transcription or benchmarks.
- `data\downloads`: Audio extracted or downloaded from public URLs.
- `data\transcripts`: TXT transcripts and JSON metadata.
- `data\jobs`: Queue job JSON snapshots.
- `data\logs`: Runtime logs.
- `models`: Local model/cache directory, including Hugging Face and faster-whisper caches.
- `tmp`: Project-local temporary directory.
- `requirements-cpu.txt`: Base dependencies for CPU/local runtime.
- `requirements-gpu.txt`: GPU-only add-on dependencies.
- `run.bat`: Windows launcher that uses `.venv\Scripts\python.exe`.
- `README.md`: Short user-facing documentation.
- `docs\DEVELOPERS.md`: This technical guide.

## Backend Modules

### `app/main.py`

Primary responsibilities:

- Create the FastAPI app with title `Local Media Transcriber`.
- Serve `static/index.html` at `/`.
- Mount static assets with no-cache headers.
- Expose status, storage, model, recording, transcription, queue, folder, and benchmark endpoints.
- Validate uploaded files, local paths, recording paths, transcript paths, model names, devices, and recording modes.
- Coordinate mutually exclusive operations, such as preventing benchmark work during recording or queue execution.
- Save direct transcription errors through `TranscriptStore`.

Important endpoints include:

- `GET /api/status`
- `GET /api/models`
- `GET /api/storage`
- `GET /api/audio/devices`
- `GET /api/audio/output-devices`
- `GET /api/audio/level`
- `GET /api/audio/output-level`
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
- Recording section with microphone/system/both modes.
- Recording device selectors and level meters.
- Help section.
- Queue/source forms.
- Runtime metrics and queue progress.
- File storage section.
- Benchmark section.

The contract tests look for specific IDs, order, and structural elements. Keep ID changes deliberate and update tests only when the product contract truly changes.

### `static/app.js`

Main browser controller.

Responsibilities:

- Bind DOM elements.
- Call backend APIs.
- Manage recording, device refresh/switching, level polling, queue actions, storage display, benchmark actions, toasts, operation overlay, and transcript loading.
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

## Current Audio Recording Flow

1. The frontend loads storage, devices, model status, and initial state.
2. The user selects recording mode: `mic`, `system`, or `both`.
3. The frontend polls microphone and/or system levels according to the selected mode.
4. `POST /api/record/start` validates the mode and checks for conflicting benchmark work.
5. For `mic`, `AudioRecorder.start()` creates `mic_<timestamp>.wav`.
6. For `system`, `SystemAudioRecorder.start()` creates `system_<timestamp>.wav`.
7. For `both`, both recorders start with the same timestamp and save separate files. They are not mixed.
8. While recording, the UI shows level meters and a timer.
9. Device switch endpoints can update microphone or output device during recording.
10. `POST /api/record/stop` stops the active recorder(s), gathers diagnostics, updates the latest recording references, and refreshes storage.

Do not add screen capture or media-session behavior by modifying this flow directly. Future work should add a coordinating layer that can call the existing audio recorders.

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

## RU/EN Localization Notes

- All static UI labels should live in `static/i18n.js`.
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
git diff --check
git diff --stat
git status
```

Do not run full `unittest discover` unless the task asks for it or the change affects broader backend behavior.

Useful targeted tests:

- `tests.test_i18n`: localization key contract and no Russian static markup in selected frontend files.
- `tests.test_ui_contract`: DOM IDs, queue endpoint usage, section order, and tour selectors.
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
- For GPU-only CUDA/NVIDIA add-ons, update `requirements-gpu.txt`.
- If a new feature needs dependencies, install them only inside `C:\Python\LocalMediaTranscriber\.venv`.
- Keep runtime caches and temporary files inside the project folder where possible.

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
6. Mouse events.
7. Keyboard events with a clear privacy warning.
8. Keyframes.
9. OCR.
10. VLM.
11. Local/server processing modes.
12. Possible pay-as-you-go server processing.

Suggested implementation shape for future media work:

- Keep existing audio recorders as independent services.
- Add a media-session coordinator instead of merging screen recording into audio recorder modules.
- Store session metadata separately from transcript metadata at first.
- Keep screen recording dependencies out of this iteration unless the task explicitly requests them.
- Add tests around session metadata before adding OCR/VLM processing.

## Current No-Go List

Do not add these until explicitly requested:

- Screen recording implementation.
- `mss`, `opencv`, or similar screen/video dependencies.
- `media_sessions` runtime model.
- Backend audio recording logic changes.
- Transcription queue logic changes.
- API endpoint changes without a product need.
- Compact Media UI.
- Mouse or keyboard logging.
- OCR, VLM, or keyframe extraction.
- Server processing.
- Installer or EXE packaging.
