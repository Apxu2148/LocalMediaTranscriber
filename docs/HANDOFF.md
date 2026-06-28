# LocalMediaTranscriber — handoff

## Current state

LocalMediaTranscriber is a fork of LocalAudioTranscriber.

Implemented through the OCR/CV settings UI cleanup after Stage 1.2a:
- local audio/video transcription;
- URL audio/video transcription;
- local/URL frame extraction;
- queue processing;
- processing_plan per item;
- runtime estimate/test-run;
- URL download progress and cancellation;
- cancellation for transcription and frame extraction;
- URL download profiles plus media/extraction benchmark diagnostics;
- OCR readiness catalog for Tesseract, EasyOCR, PaddleOCR, and Windows OCR;
- checkbox-style OCR/CV default and per-item settings, with new queue items inheriting current EasyOCR and CV Visual metadata defaults;
- EasyOCR over extracted frame folders with `frames_ocr.jsonl` and `frames_ocr.txt` artifacts;
- deterministic CV metadata over extracted queue frames with `frames_cv.jsonl` and `frames_cv.txt` artifacts;
- queue-owned output folders under `data\queues\<queue_folder>\item_xxx\`, with manifests and per-item `downloads`, `transcript`, `frames`, `ocr`, `cv`, `events`, and `logs` folders.

PaddleOCR, Windows OCR, Tesseract OCR processing, neural object detection, YOLO, and VLM analysis are still disabled / coming soon.

## Current next task

Future OCR/CV stages: consider additional OCR backends and design smarter frame selection, object detection, YOLO, and LLM/VLM work separately from the deterministic CV metadata path.

## Constraints

- Work only in C:\Python\LocalMediaTranscriber.
- Do not modify C:\Python\LocalAudioTranscriber.
- Do not commit automatically.
- Do not install dependencies automatically.
- Do not add heavy dependencies to main requirements.
- Pillow is optional for CV metadata via `requirements-cv-metadata.txt`; do not install it automatically.
- Do not add new BAT files.
- All UI strings through static/i18n.js.
