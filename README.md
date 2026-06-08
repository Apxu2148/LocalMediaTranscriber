# LocalMediaTranscriber

LocalMediaTranscriber is a local Windows web app for recording microphone audio, recording system audio through WASAPI loopback, and transcribing local media with `faster-whisper`.

This project is a separate fork of `LocalAudioTranscriber`. The current version still keeps the proven audio recording and transcription workflow, while the future direction is broader media capture: media sessions, screen recording, OCR, keyframes, VLM analysis, and optional local or server-side processing.

## Current Features

- Record microphone audio to WAV.
- Record Windows system audio to WAV through WASAPI loopback.
- Record microphone and system audio as two separate WAV files.
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

`requirements-gpu.txt` should contain only the additional CUDA/NVIDIA packages needed for GPU acceleration. Keep both requirements files updated when dependencies change.

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

Downloads from public URLs:

```text
C:\Python\LocalMediaTranscriber\data\downloads
```

Logs:

```text
C:\Python\LocalMediaTranscriber\data\logs\app.log
```

## Notes

For `.mp3`, `.m4a`, `.mp4`, `.webm`, and `.mkv`, make sure `ffmpeg` is installed and available in `PATH`. Current video support extracts the audio track only; video frames are not analyzed yet.

Use the app only with audio, video, and files you are allowed to record, download, process, and transcribe.
