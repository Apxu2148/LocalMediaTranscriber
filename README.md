# LocalMediaTranscriber

LocalMediaTranscriber is a local Windows web app for recording microphone audio, recording system audio through WASAPI loopback, and transcribing local media with `faster-whisper`.

This project is a separate fork of `LocalAudioTranscriber`. The current version still keeps the proven audio recording and transcription workflow, while the future direction is broader media capture: media sessions, screen recording, OCR, keyframes, VLM analysis, and optional local or server-side processing.

## Current Features

- Record microphone audio to WAV.
- Record Windows system audio to WAV through WASAPI loopback.
- Record microphone and system audio as two separate WAV files.
- Record one or more physical displays to per-display video files in `data\recordings`.
- Preserve real-time screen video duration by duplicating the latest frame when capture falls below the selected FPS.
- Draw a visible mouse cursor marker into screen recordings.
- Merge one screen video with microphone and/or system audio into a video with sound through FFmpeg.
- Show microphone and system audio levels.
- Add latest recordings, local files, or public URLs to a global transcription queue.
- Transcribe `.wav`, `.mp3`, `.m4a`, `.mp4`, `.webm`, and `.mkv` sources.
- Extract and transcribe the audio track from supported video files.
- Choose Whisper models: `tiny`, `base`, `small`, `medium`, `large-v3`.
- Use CPU by default, or CUDA/GPU when GPU dependencies are installed.
- Save transcripts and JSON diagnostics in `data\transcripts`.
- Switch the UI between RU and EN.
- Run simple CPU/GPU transcription benchmarks.

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

`run.bat` uses `.venv\Scripts\python.exe`, starts the FastAPI server, and opens the browser with a cache-busting query parameter. If port `8000` is already in use, the script asks before stopping that process.

## Stored Files

Recordings:

```text
C:\Python\LocalMediaTranscriber\data\recordings
```

Transcripts:

```text
C:\Python\LocalMediaTranscriber\data\transcripts
```

Screen videos and screen session JSON:

```text
C:\Python\LocalMediaTranscriber\data\recordings
```

New screen recordings are stored as a flat list beside audio recordings, for example `screen1_20260609_001122__30fps.mp4` and `session_20260609_001122.json`. Older MVP runs may still exist under `data\media_sessions`.

Downloads from public URLs:

```text
C:\Python\LocalMediaTranscriber\data\downloads
```

Logs:

```text
C:\Python\LocalMediaTranscriber\data\logs\app.log
```

## Notes

For `.mp3`, `.m4a`, `.mp4`, `.webm`, and `.mkv`, make sure `ffmpeg` is installed and available in `PATH`. FFmpeg is also required for the "Merge video with audio" workflow. Uploaded video support extracts the audio track only; screen recording creates video files with a cursor marker but does not perform OCR, keyframe extraction, scene detection, mouse event logging, keyboard logging, or VLM analysis yet.

Use the app only with audio, video, and files you are allowed to record, download, process, and transcribe.
