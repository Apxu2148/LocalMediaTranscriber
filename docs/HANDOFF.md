# LocalMediaTranscriber — handoff

## Current state

LocalMediaTranscriber is a fork of LocalAudioTranscriber.

Implemented through Stage 1.1c:
- local audio/video transcription;
- URL audio/video transcription;
- local/URL frame extraction;
- queue processing;
- processing_plan per item;
- runtime estimate/test-run;
- URL download progress and cancellation;
- cancellation for transcription and frame extraction;
- URL download profiles plus media/extraction benchmark diagnostics;
- OCR backend selector/readiness catalog for Tesseract, EasyOCR, PaddleOCR, and Windows OCR;
- EasyOCR over extracted frame folders with `frames_ocr.jsonl` and `frames_ocr.txt` artifacts.

PaddleOCR, Windows OCR, Tesseract OCR processing, and CV processing are still disabled / coming soon.

## Current next task

Future OCR/CV stages: add runtime estimates if needed, consider additional OCR backends, and design smarter frame selection/CV/LLM/VLM work separately.

## Constraints

- Work only in C:\Python\LocalMediaTranscriber.
- Do not modify C:\Python\LocalAudioTranscriber.
- Do not commit automatically.
- Do not install dependencies automatically.
- Do not add heavy dependencies to main requirements.
- Do not add new BAT files.
- All UI strings through static/i18n.js.
