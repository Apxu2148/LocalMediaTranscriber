# Project state

## Current milestone

Stage 1.1b is implemented and validated in the working tree. The app now persists an OCR backend selection and reports readiness for Tesseract, EasyOCR, PaddleOCR, and Windows OCR. OCR execution remains intentionally disabled.

## Changed areas

- `app/ocr_manager.py`: combined backend catalog, optional import checks, Windows platform check, and selected-backend persistence.
- `app/main.py`: selected backend/check API fields and invalid-backend handling.
- `app/queue_manager.py`: selected backend snapshot with OCR still normalized to a no-op.
- `static/index.html`, `static/app.js`, `static/style.css`, `static/i18n.js`: compact selector, conditional Tesseract fields, readiness details, and RU/EN copy.
- Focused OCR/API/i18n/UI/queue tests and OCR documentation.

## Validation

Passed on 2026-06-20:

- `python -m compileall app`
- `python -m unittest tests.test_i18n tests.test_ui_contract` (25 tests)
- `python -m unittest tests.test_ocr_manager` (18 tests)
- `python -m unittest tests.test_queue_manager tests.test_frame_extractor` (48 tests)
- `python -m unittest tests.test_runtime_estimate tests.test_url_downloader` (22 tests)
- `python -m unittest tests.test_http_smoke` (12 tests)
- `python -m unittest tests.test_storage_manager tests.test_model_manager` (19 tests)
- Cyrillic scan of `static/app.js` and `static/index.html` returned no matches; `git diff --check` passed with CRLF warnings only.

## Manual checks still required

- Start with `run.bat` and exercise all four selector options.
- Confirm Tesseract path visibility and readiness on the local machine.
- Confirm selection persists after refresh.
- Smoke-test transcription, frame extraction, estimates, and URL cancellation.

## Known limitations

- No backend performs OCR or creates OCR artifacts.
- Optional dependencies are detected but never installed or initialized.
- PaddleOCR and Windows OCR are readiness-only experimental entries.

## Recommended next stage

Stage 1.1c: choose the first executable backend and implement OCR over extracted frames with artifacts, queue handling, runtime estimation, and cancellation in the same stage.

## Documentation / project memory notes

The current memory file structure is sufficient. Keep `HANDOFF.md` brief and use this file for validation and limitations.
