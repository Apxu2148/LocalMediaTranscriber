# LocalMediaTranscriber

LocalMediaTranscriber is a local Windows web app for recording microphone audio, recording system audio through WASAPI loopback, and processing local media with `faster-whisper` plus video frame extraction tools.

This project is a separate fork of `LocalAudioTranscriber`. The current version still keeps the proven audio recording and transcription workflow, while the future direction is broader media capture: media sessions, screen recording, extracted frames, OCR, VLM analysis, and optional local or server-side processing.

## Current Features

- Record microphone audio to WAV.
- Record Windows system audio to WAV through WASAPI loopback.
- Record microphone and system audio as two separate WAV files.
- Record one or more physical displays to per-display video files in `data\recordings`.
- Pick displays from visual cards ordered by virtual desktop layout, with resolution, coordinates, and optional thumbnails.
- Preserve real-time screen video duration by duplicating the latest frame when capture falls below the selected FPS.
- Draw a visible mouse cursor marker into screen recordings.
- Log mouse and keyboard input events for screen recording sessions.
- Merge one screen video with microphone and/or system audio into a video with sound through FFmpeg.
- Keep the recent recordings list compact and hide service JSON metadata files from the normal user file list.
- Show microphone and system audio levels during active recordings without opening audio devices while idle.
- Add latest recordings, local files, or public URLs to a global media processing queue.
- See persistent queue stage status while long operations run.
- Add controls are disabled while a file, recording, or link is being added to prevent accidental duplicate queue items.
- Transcribe `.wav`, `.mp3`, `.m4a`, `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov` sources.
- Extract and transcribe the audio track from supported video files.
- Choose per-video queue operations: transcribe audio, extract frames, or both.
- Choose URL queue operations: transcribe audio, extract frames from a downloaded video-readable file, or both.
- Optionally cap built-in `yt-dlp` URL video downloads at 480p, 720p, 1080p, 1440p, or 2160p; Auto preserves the previous behavior.
- See direct URL download bytes, total size, speed, ETA, and percentage when the server provides a size; unknown-size and platform downloads show an active indeterminate state.
- Cancel an active direct or `yt-dlp` URL download without stopping the app; partial download files are removed and the queue continues.
- Extract video frames to a per-source folder with a `frames_index.json` manifest.
- Choose JPEG quality `75`, `80`, `85`, `90`, `95`, or `100` for frame extraction; `90` is the default.
- Optionally downscale saved extracted frames to a maximum width of 1920, 1280, 960, or 640 pixels; Original preserves the previous behavior.
- Run a 60-second runtime estimate for a pending item's enabled transcription and frame extraction operations before full processing.
- Use checkbox-style OCR/CV options in default and per-item settings. EasyOCR and CV Visual metadata are the currently functional options; the other OCR/CV options are disabled placeholders for future modules.
- Remove pending queue items, or cancel a running frame extraction item and continue with the rest of the queue.
- Choose Whisper models: `tiny`, `base`, `small`, `medium`, `large-v3`.
- Manage Whisper models before transcription: check local availability, download, verify, view info, and delete selected local caches.
- Use CPU by default, or CUDA/GPU when GPU dependencies are installed.
- Save transcripts and JSON diagnostics in `data\transcripts`.
- See a storage overview for `data\downloads`, `data\uploads`, `data\recordings`, `data\transcripts`, logs, jobs, and total app data size.
- Keep intermediate URL downloads and uploaded temp files by default, with explicit opt-out retention settings.
- Clear `data\downloads` or `data\uploads` from the UI with confirmation; primary recordings, frames, and transcripts are not part of this cleanup.
- See created output artifacts and paths directly on terminal queue item cards.
- Switch the UI between RU and EN.
- Run simple CPU/GPU transcription benchmarks.
- Use a temporary LocalMediaTranscriber browser tab icon from `static\icons`.

## Project Folder

Use this folder for this fork:

```bat
cd /d C:\Python\LocalMediaTranscriber
```

Do not install dependencies globally. Keep the project environment in:

```text
C:\Python\LocalMediaTranscriber\.venv
```

## CPU Setup

```bat
cd /d C:\Python\LocalMediaTranscriber
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-cpu.txt
```

`requirements-cpu.txt` contains the base runtime dependencies for local CPU transcription.
It also includes `mss` and `opencv-python` for screen recording.

## GPU Setup

Install the CPU requirements first, then install the GPU add-ons:

```bat
cd /d C:\Python\LocalMediaTranscriber
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-cpu.txt
pip install -r requirements-gpu.txt
```

`requirements-gpu.txt` contains the CUDA/NVIDIA packages needed for GPU acceleration plus the screen-recording runtime packages mirrored from the CPU file. Keep both requirements files updated when dependencies change.

## OCR / CV Setup

The OCR and CV panels near the default queue settings use checkbox-style options so future builds can enable more than one processor per item. In the current build, EasyOCR is the functional OCR option and CV Visual metadata is the functional CV option. Tesseract OCR, PaddleOCR, Windows OCR, object detection, VLM analysis, and YOLO object detection are visible disabled placeholders.

Tesseract is not bundled, downloaded, or installed by this app. It is visible only as a disabled future placeholder in the current processing UI.

EasyOCR is optional and is the first executable frame-OCR backend. Install it manually only if you want OCR over extracted frames:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr-easyocr.txt
```

This may also install PyTorch dependencies selected by EasyOCR. The app does not install or download OCR dependencies automatically.

EasyOCR can process extracted frames when the optional dependencies are installed. The app still does not install or download OCR/CV dependencies automatically.

## Run

```bat
cd /d C:\Python\LocalMediaTranscriber
.\run.bat
```

The app opens at:

```text
http://127.0.0.1:8000
```

Existing BAT files:

```text
run.bat
  Starts Local Media Transcriber.

stop.bat
  Stops the app/server processes only.

cleanup-dev.bat
  Stops the app/server processes, cleans dev caches, safely removes stale .git/index.lock if no related git/ssh/gpg/codex process is active, and shows git status --short.
```

`run.bat` uses `.venv\Scripts\python.exe`, starts the FastAPI server, and opens the browser with a cache-busting query parameter. If port `8000` is already in use, the script asks before stopping that process.

To stop a stale development server without touching unrelated Python processes:

```bat
cd /d C:\Python\LocalMediaTranscriber
.\stop.bat
```

`stop.bat` only targets Python/uvicorn processes whose command line references this project folder.

For development cleanup after an interrupted run:

```bat
cd /d C:\Python\LocalMediaTranscriber
.\cleanup-dev.bat
```

`cleanup-dev.bat` stops project-scoped Python/uvicorn processes, removes source/test `__pycache__` directories and `.pytest_cache`, removes `.git\index.lock` only when no related `git.exe`, `ssh.exe`, `gpg.exe`, or `codex.exe` command line references this repository, and prints `git status --short`.

If Git reports `.git/index.lock` before commit, run `cleanup-dev.bat`.

## Stored Files

The queue is now a media processing queue. Its main action is "Start processing". Video files and supported video URLs can currently be transcribed, split into frames, processed with EasyOCR frame OCR when available, and analyzed with deterministic CV Visual metadata.

Queue usability:

- The app shows persistent queue stage status near the queue controls and inside running item cards.
- Add buttons are disabled while a file, latest recording, or link is being added. If the laptop is slow, wait for the visible "Adding..." or stage message instead of clicking repeatedly.
- Fast repeated clicks and active duplicate file/link adds are ignored before they can create duplicate queue items.
- Queue stages include preparing source, downloading media/video, transcribing audio, cancelling transcription/frame extraction, extracting frames, completed, failed, and cancelled.
- Active item cards show determinate stage progress for URL downloads and frame extraction when counts are known, or an indeterminate progress bar when the backend cannot provide a real percentage.
- Default processing settings live near the queue controls. They define the audio model/device, frame extraction defaults, URL download profile/resolution, and OCR/CV placeholders for newly added items only.
- Each queue item stores its own processing plan. Changing defaults later does not silently mutate existing items; pending item settings override defaults.
- Pending local items have an **Estimate time** action. It tests up to the first 60 seconds with that item's model/device and frame interval/JPEG quality/max frame size, then shows separate and combined approximate runtimes.
- Estimate samples use temporary clipped audio and temporary JPEGs. They do not create normal transcripts, frame folders, `frames_index.json`, or output artifacts, and the temporary workspace is removed after success or failure.
- Pending URL items can be estimated only when a local downloaded media file is already available. Stage 0.96 does not download a URL solely for estimation.
- After an item completes, fails, or is cancelled, its card shows a "Created files" section with known artifacts: transcript TXT, diagnostic JSON, frame folder, `frames_index.json`, EasyOCR frame OCR JSONL/TXT outputs, downloaded URL media, and uploaded temporary file when available. Cancelled transcription outputs are labelled as partial transcripts. If retention removed a file, the item says so instead of showing it as still present.
- EasyOCR can run over extracted video/URL frames when the optional OCR requirements are installed and the EasyOCR checkbox is enabled. CV Visual metadata can run over extracted frames. PaddleOCR, Windows OCR, object detection, VLM analysis, YOLO, and media-index entries remain disabled placeholders. Runtime estimates do not include a separate OCR/CV estimate yet; actual OCR benchmark metrics are recorded after processing.

URL download profiles:

- New URL items snapshot the selected profile: Auto, best for frame extraction, best quality, smallest file, WebM/MP4/MKV/MOV/AVI preference, audio/transcription friendly, or an advanced custom yt-dlp format string.
- New URL items also snapshot the selected maximum video height: Auto, 480p, 720p, 1080p, 1440p, or 2160p. Auto preserves the previous unbounded profile behavior.
- Actual format availability depends on the source site and URL. Every built-in profile has bounded choices followed by its original fallback; direct media URLs keep their source format because yt-dlp selection is not involved.
- Best for frame extraction prefers MP4-compatible streams and resolutions at or below 720p, then 1080p, before falling back. MOV and AVI preferences are best-effort and do not force unsafe remuxing.
- Audio/transcription friendly preserves the existing audio-only path for transcription-only jobs and remains video-capable when frame extraction is selected.
- The custom field is passed only as yt-dlp's format option. The max-height selector is ignored for custom strings, and an empty custom value safely falls back to Auto.
- Optional media probing records container, codecs, resolution, FPS, file size, download time, selected profile, max video height, and format string. Frame jobs can additionally record elapsed extraction time, frames extracted, and seconds per frame in queue/job metadata and logs. Missing `ffprobe` is reported as unavailable without failing the job.

Storage panel:

- The Files section includes a Storage panel with folder sizes for `data\downloads`, `data\uploads`, `data\recordings`, `data\transcripts`, `data\logs`, `data\jobs`, and the total data size.
- The refresh button recalculates sizes. Missing folders show size `0`.
- Storage settings are conservative by default: downloaded URL media and uploaded temp files are kept unless you explicitly disable the matching keep checkbox.
- When downloaded URL media retention is disabled, the app deletes the current item's owned file after completion, cancellation, or failure. Uploaded temporary files are still deleted only after successful processing when their keep setting is disabled.
- Retention cleanup runs only after active download/transcription/frame work has stopped; it never deletes media still in use.
- Retention cleanup never deletes `data\recordings`, `data\transcripts`, extracted frames, screen recordings, or `frames_index.json`.
- The manual cleanup buttons clear only `data\downloads` or `data\uploads` after confirmation. They do not delete transcripts, recordings, frames, or original user files outside the project `data` folder.
- Storage, URL download, frame extraction, and OCR engine settings are persisted in `data\settings.json`.

OCR backend readiness:

- **Tesseract OCR** is an external executable. The app checks a configured path, `PATH`, common Windows install locations, its version, and installed `rus`/`eng` language data.
- **EasyOCR** is an optional integrated Python backend. Readiness checks only verify the module import and do not initialize a reader or download models; actual reader/model initialization happens only when OCR processing is requested.
- **PaddleOCR** is an optional experimental Python backend. This stage only checks whether its module is importable.
- **Windows OCR** is an experimental Windows-only system backend. The app performs a lightweight WinRT import check on Windows.
- EasyOCR, PaddleOCR, and WinRT dependencies are not installed automatically and are not part of the main requirements files. EasyOCR's optional requirement is isolated in `requirements-ocr-easyocr.txt`.
- When EasyOCR is checked and importable, OCR can be enabled for video and URL queue items. Enabling OCR also enables frame extraction because OCR runs over the extracted frame folder.
- EasyOCR outputs are written beside `frames_index.json` as `frames_ocr.jsonl` and `frames_ocr.txt`. The JSONL contains one record per processed frame; the TXT contains recognized text and frame-level OCR errors.

Recordings:

```text
C:\Python\LocalMediaTranscriber\data\recordings
```

Transcripts:

```text
C:\Python\LocalMediaTranscriber\data\transcripts
```

Audio transcripts are saved under `data\transcripts`.

Screen videos and screen session JSON:

```text
C:\Python\LocalMediaTranscriber\data\recordings
```

New screen recordings are stored as a flat list beside audio recordings, for example `screen1_20260609_001122__30fps.mp4` and `session_20260609_001122.json`. When mouse or keyboard logging is enabled, `mouse_events_YYYYMMDD_HHMMSS.jsonl` and `keyboard_events_YYYYMMDD_HHMMSS.jsonl` are saved beside the session JSON. Older MVP runs may still exist under `data\media_sessions`.

Mouse and keyboard event logging is available only when screen recording is enabled. Keyboard logging records special keys and hotkeys by default; ordinary typed text is not recorded. The technical schema is documented in `docs\DEVELOPERS.md`.

When multiple monitors are connected, the screen selection area shows display cards instead of a plain list. Cards show resolution and virtual desktop coordinates (`left`, `top`) so left/right monitor placement is easier to identify. Per-display preview thumbnails can be enabled manually; preview is off by default to reduce resource usage.

The Recent recordings UI shows user-facing media files only: `.wav`, `.mp3`, `.m4a`, `.mp4`, `.avi`, `.mkv`, `.webm`, `.flac`, and `.ogg`. Service files such as `.json`, `.log`, `.tmp`, and `.pyc` remain hidden from that list. Screen session JSON metadata stays on disk for diagnostics and internal references.

Video frame extraction creates a folder for each processed video item:

```text
C:\Python\LocalMediaTranscriber\data\recordings\<base>__frames
```

The frame index is saved at:

```text
C:\Python\LocalMediaTranscriber\data\recordings\<base>__frames\frames_index.json
```

The folder contains JPEG files named like `frame_000001__t000000.000.jpg` and a `frames_index.json` file with source details, frame extraction settings, video metadata, extracted frame records, status, and cancellation/error information. The default extraction setting is one frame every 10 seconds with JPEG quality `90` and original frame dimensions. Available JPEG quality options are `75`, `80`, `85`, `90`, `95`, and `100`; available max frame sizes are Original, width up to 1920, 1280, 960, or 640 pixels. Downscaling preserves aspect ratio and never upscales smaller videos. Quality `100` can significantly increase file size and usually is not necessary for OCR/CV. The queue UI estimates the frame count and approximate disk usage before processing, and warns when a setting is expected to create more than 1000 images.

When EasyOCR processing is enabled, OCR artifacts are saved in the same extracted-frame folder:

```text
C:\Python\LocalMediaTranscriber\data\recordings\<base>__frames\frames_ocr.jsonl
C:\Python\LocalMediaTranscriber\data\recordings\<base>__frames\frames_ocr.txt
```

EasyOCR uses `ru` and `en` for this stage. Missing EasyOCR dependencies, unsupported OCR backends, missing frame indexes, or empty frame lists fail the queue item with a controlled error instead of crashing the app.

Downloads from public URLs:

```text
C:\Python\LocalMediaTranscriber\data\downloads
```

For URL items, direct media file links ending in `.mp4`, `.webm`, `.mkv`, `.avi`, or `.mov` are downloaded directly over HTTP(S) into `data\downloads` without `yt-dlp`; query strings are ignored for extension detection, and the URL max-height selector does not alter direct downloads. YouTube, VK, and other webpage/video-platform URLs still use `yt-dlp`. For audio-only URL transcription, direct media URLs use the downloaded media file, while non-direct URLs keep the existing audio extraction path. If frame extraction is selected, the downloaded video-readable media file uses the same frame extraction settings as local video files: extraction rate, JPEG quality, and max frame size. URL media downloads are kept under `data\downloads`; transcripts are saved under `data\transcripts`; frames are saved under `data\recordings\<base>__frames`; and `frames_index.json` is saved inside that frames folder.

Some sites, streams, or codecs may fail depending on `yt-dlp`, FFmpeg, OpenCV, and the locally available decoders. Direct `.mp4`, `.webm`, `.mkv`, `.avi`, or `.mov` URLs are the simplest test path. Cookies, authenticated/private videos, playlists, and per-URL format listing are not part of this iteration, so some YouTube/VK URLs can still fail with a readable authorization/cookies message. The URL max-height selector is best-effort and can fall back to a higher source format if no bounded format is available.

Uploaded temporary files:

```text
C:\Python\LocalMediaTranscriber\data\uploads
```

Files selected through browser upload flows are copied into `data\uploads` before processing. The cleanup button for uploads deletes only this project temp folder, never the original file you selected elsewhere on disk.

Logs:

```text
C:\Python\LocalMediaTranscriber\data\logs\app.log
```

Runtime output under `data\recordings`, `data\transcripts`, `data\uploads`, `data\downloads`, `data\jobs`, and `data\logs` is ignored by Git.

Current cancellation behavior: pending or waiting queue items can be removed; active URL downloads, audio transcription, frame extraction, and EasyOCR frame OCR can be cancelled cooperatively, and the queue continues with the next pending item. Direct downloads stop at the next streaming chunk; `yt-dlp` downloads stop through progress/postprocessor hooks. Cancelled or failed downloads remove their owned partial files instead of exposing them as completed media. Audio transcription cancellation is safe but not an unsafe thread kill, so it may finish after the current Whisper segment or model-loading step. Cancelled transcription saves any recognized text as a clearly marked partial transcript with `__partial_cancelled__` in the filename and `status: "cancelled"` / `partial: true` in the diagnostic JSON; the queue does not present that file as a successful final transcript. Cancelled OCR may keep complete JSONL/TXT artifacts for frames processed before cancellation.

Microphone privacy behavior: microphone access is requested only when the user starts a recording that includes the microphone source. Queue processing, URL downloads, local file transcription, frame extraction, storage views, and normal UI browsing do not use the microphone. The level meters stay idle until a matching recording source is active, and the recording stop flow releases the microphone stream.

## Whisper Models

The Whisper models section includes a compact model table. Use it to:

- see whether each supported model is available locally;
- download a selected model before first transcription;
- verify that a downloaded model can load with the selected device setting;
- delete local files for one selected model when you want to reclaim space;
- open approximate model size, parameter, quality, use, and hardware notes.

Model downloads use the project-local faster-whisper cache under:

```text
C:\Python\LocalMediaTranscriber\models\faster-whisper
```

Interrupted downloads should show a clear error and can usually be retried. Delete only removes cache paths that match the selected supported model; it does not wipe the whole Hugging Face cache.

The model manager UI treats model setup as a small lifecycle: not downloaded, downloading, verifying, ready, or failed. After a download or verification succeeds, active download progress is cleared and the table/status area shows the model as locally ready; tests mock model download and verification and must not fetch real model files.

## App Icon

The browser tab icon lives in:

```text
C:\Python\LocalMediaTranscriber\static\icons\favicon.svg
```

This is a temporary blue-violet SVG icon. To replace it later, keep the same filename or update the `<link rel="icon">` entry in `static\index.html`. Recommended future formats are SVG for the scalable favicon, PNG 32x32, and optionally 16x16, 48x48, and 180x180 Apple touch icon files.

## Notes

For `.mp3`, `.m4a`, `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov`, make sure `ffmpeg` is installed and available in `PATH`. FFmpeg is also required for the "Merge video with audio" workflow. Video queue items can extract audio for transcription, save JPEG frames, run EasyOCR when available, and run CV Visual metadata. Future OCR/CV processors remain disabled placeholders.

Use the app only with audio, video, and files you are allowed to record, download, process, and transcribe.
