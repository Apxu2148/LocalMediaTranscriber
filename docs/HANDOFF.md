# LocalMediaTranscriber — handoff

## Current state

LocalMediaTranscriber is a fork of LocalAudioTranscriber.

Implemented through Stage 1.1b:
- local audio/video transcription;
- URL audio/video transcription;
- local/URL frame extraction;
- queue processing;
- processing_plan per item;
- runtime estimate/test-run;
- URL download progress and cancellation;
- cancellation for transcription and frame extraction;
- OCR backend selector/readiness catalog for Tesseract, EasyOCR, PaddleOCR, and Windows OCR.

OCR/CV processing is still disabled / coming soon.

## Current next task

Stage 1.1c: implement the first OCR processor over extracted frames, with queue execution, artifacts, estimates, and cancellation designed together.

## Constraints

- Work only in C:\Python\LocalMediaTranscriber.
- Do not modify C:\Python\LocalAudioTranscriber.
- Do not commit automatically.
- Do not install dependencies automatically.
- Do not add heavy dependencies to main requirements.
- Do not add new BAT files.
- All UI strings through static/i18n.js.
