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
- Show microphone and system audio levels.
- Add latest recordings, local files, or public URLs to a global media processing queue.
- Transcribe `.wav`, `.mp3`, `.m4a`, `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov` sources.
- Extract and transcribe the audio track from supported video files.
- Choose per-video queue operations: transcribe audio, extract frames, or both.
- Choose URL queue operations: transcribe audio, extract frames from a downloaded video-readable file, or both.
- Extract video frames to a per-source folder with a `frames_index.json` manifest.
- Choose JPEG quality `75`, `80`, `85`, `90`, `95`, or `100` for frame extraction; `90` is the default.
- Remove pending queue items, or cancel a running frame extraction item and continue with the rest of the queue.
- Choose Whisper models: `tiny`, `base`, `small`, `medium`, `large-v3`.
- Manage Whisper models before transcription: check local availability, download, verify, view info, and delete selected local caches.
- Use CPU by default, or CUDA/GPU when GPU dependencies are installed.
- Save transcripts and JSON diagnostics in `data\transcripts`.
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

The queue is now a media processing queue. Its main action is "Start processing". Video files and supported video URLs can currently be transcribed, split into frames, or both. OCR and CV/VLM options are visible as disabled coming-soon placeholders and are not implemented yet.

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

The folder contains JPEG files named like `frame_000001__t000000.000.jpg` and a `frames_index.json` file with source details, frame extraction settings, video metadata, extracted frame records, status, and cancellation/error information. The default extraction setting is one frame every 10 seconds with JPEG quality `90`. Available JPEG quality options are `75`, `80`, `85`, `90`, `95`, and `100`. Quality `100` can significantly increase file size and usually is not necessary for OCR/CV. The queue UI estimates the frame count and approximate disk usage before processing, and warns when a setting is expected to create more than 1000 images.

Downloads from public URLs:

```text
C:\Python\LocalMediaTranscriber\data\downloads
```

For URL items, direct media file links ending in `.mp4`, `.webm`, `.mkv`, `.avi`, or `.mov` are downloaded directly over HTTP(S) into `data\downloads` without `yt-dlp`; query strings are ignored for extension detection. YouTube, VK, and other webpage/video-platform URLs still use `yt-dlp`. For audio-only URL transcription, direct media URLs use the downloaded media file, while non-direct URLs keep the existing audio extraction path. If frame extraction is selected, the downloaded video-readable media file uses the same frame extraction settings as local video files: extraction rate and JPEG quality. URL media downloads are kept under `data\downloads`; transcripts are saved under `data\transcripts`; frames are saved under `data\recordings\<base>__frames`; and `frames_index.json` is saved inside that frames folder.

Some sites, streams, or codecs may fail depending on `yt-dlp`, FFmpeg, OpenCV, and the locally available decoders. Direct `.mp4`, `.webm`, `.mkv`, `.avi`, or `.mov` URLs are the simplest test path. Cookies, authenticated/private videos, playlists, and video quality selection are not part of this iteration, so some YouTube/VK URLs can still fail with a readable authorization/cookies message.

Logs:

```text
C:\Python\LocalMediaTranscriber\data\logs\app.log
```

Runtime output under `data\recordings`, `data\transcripts`, `data\uploads`, `data\downloads`, `data\jobs`, and `data\logs` is ignored by Git.

Current cancellation behavior: pending or waiting queue items can be removed; running frame extraction can be cancelled cooperatively and the queue continues; running audio transcription is not safely cancellable yet, and the UI marks that action as unavailable.

## Whisper Models

The Transcription settings section includes a compact Whisper models table. Use it to:

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

## App Icon

The browser tab icon lives in:

```text
C:\Python\LocalMediaTranscriber\static\icons\favicon.svg
```

This is a temporary blue-violet SVG icon. To replace it later, keep the same filename or update the `<link rel="icon">` entry in `static\index.html`. Recommended future formats are SVG for the scalable favicon, PNG 32x32, and optionally 16x16, 48x48, and 180x180 Apple touch icon files.

## Notes

For `.mp3`, `.m4a`, `.mp4`, `.webm`, `.mkv`, `.avi`, and `.mov`, make sure `ffmpeg` is installed and available in `PATH`. FFmpeg is also required for the "Merge video with audio" workflow. Video queue items can extract audio for transcription and/or save JPEG frames. OCR and CV/VLM analysis are still unimplemented; the UI shows them as disabled coming-soon options.

Use the app only with audio, video, and files you are allowed to record, download, process, and transcribe.
