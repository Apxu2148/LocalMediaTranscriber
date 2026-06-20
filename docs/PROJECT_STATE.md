# Project state

## Current milestone

Stage 1.1b is implemented and validated. A follow-up retention bugfix now removes app-owned URL downloads after completion, cancellation, or failure when `keep_downloaded_url_media=false`. OCR execution remains intentionally disabled.

## URL download cleanup bugfix

- Queue retention now runs from one terminal-item path after active processing has returned.
- URL ownership requires `source_type=url`, the current item's recorded download path, and the existing `data/downloads` safety boundary.
- Cleanup failures are recorded in `outputs` without replacing completed/cancelled/error status or the original processing error.
- Uploaded-temp cleanup remains success-only, and local user files remain protected.

## Changed areas

- `app/ocr_manager.py`: combined backend catalog, optional import checks, Windows platform check, and selected-backend persistence.
- `app/main.py`: selected backend/check API fields and invalid-backend handling.
- `app/queue_manager.py`: selected backend snapshot with OCR still normalized to a no-op.
- `static/index.html`, `static/app.js`, `static/style.css`, `static/i18n.js`: compact selector, conditional Tesseract fields, readiness details, and RU/EN copy.
- Focused OCR/API/i18n/UI/queue tests and OCR documentation.
- `app/queue_manager.py`, `app/storage_manager.py`, focused retention tests, and retention documentation for the URL cleanup bugfix.

## Validation

Passed on 2026-06-20:

URL download cleanup bugfix:

- `python -m compileall app`
- `python -m unittest tests.test_queue_manager` (44 tests)
- `python -m unittest tests.test_url_downloader` (13 tests)
- `python -m unittest tests.test_storage_manager` (10 tests)
- `python -m unittest tests.test_http_smoke` (12 tests)

Stage 1.1b validation:

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
- With URL media retention disabled, cancel during frame extraction and confirm the owned download is removed; repeat with retention enabled and confirm it remains.

## Known limitations

- No backend performs OCR or creates OCR artifacts.
- Optional dependencies are detected but never installed or initialized.
- PaddleOCR and Windows OCR are readiness-only experimental entries.

## Recommended next stage

Stage 1.1c: choose the first executable backend and implement OCR over extracted frames with artifacts, queue handling, runtime estimation, and cancellation in the same stage.

## Documentation / project memory notes

The current memory file structure is sufficient. Keep `HANDOFF.md` brief and use this file for validation and limitations.
