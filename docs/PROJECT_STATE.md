# Project state

## Current milestone

Stage 1.1b and URL retention cleanup are implemented and validated. URL jobs now also snapshot a configurable download profile and record media/frame-extraction diagnostics for profile comparisons. OCR execution remains intentionally disabled.

## URL download profiles and diagnostics

- Persisted profiles cover Auto, extraction-friendly, quality/size, WebM/MP4/MKV/MOV/AVI preferences, audio-friendly, and an advanced custom yt-dlp format string.
- `processing_plan.url_download` freezes the profile/custom/log settings for each new item and survives pending-item edits.
- Download metadata records container, codecs, resolution, FPS, size, elapsed download time, selected profile, and actual format expression when available.
- URL frame jobs record elapsed extraction time, frame count, and seconds per frame in queue/job metadata and logs.
- The persistent queue-start message now uses the existing dynamic renderer, fixing the observed RU-to-EN switch issue. Stage/progress and per-item content already re-render from keys/status snapshots.

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
- `app/url_download_manager.py`, `app/url_downloader.py`, queue/main integration, compact localized settings UI, and focused URL profile/diagnostic tests.

## Validation

Passed on 2026-06-20:

URL format selector and diagnostics:

- `python -m compileall app`
- `python -m unittest tests.test_i18n tests.test_ui_contract` (27 tests)
- `python -m unittest tests.test_url_downloader` (18 tests)
- `python -m unittest tests.test_queue_manager` (44 tests)
- `python -m unittest tests.test_storage_manager` (10 tests)
- `python -m unittest tests.test_http_smoke` (13 tests)
- Cyrillic scan of `static/app.js` and `static/index.html` returned no matches.
- Requirements diff was empty; no dependencies or requirements files changed.
- `git diff --check` passed with CRLF warnings only.

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
- Save Prefer WebM, refresh, and confirm persistence; compare Auto, WebM, MP4, and extraction-friendly profiles on the same short URL using job/log diagnostic fields.
- Switch RU to EN while a queue is active and confirm the persistent queue-start/stage/per-item messages update.

## Known limitations

- No backend performs OCR or creates OCR artifacts.
- Optional dependencies are detected but never installed or initialized.
- PaddleOCR and Windows OCR are readiness-only experimental entries.
- Profiles are best-effort because sites expose different formats. Direct media URLs keep their source format, MOV/AVI preferences do not force remuxing, and no per-URL format listing is implemented.
- `ffprobe` metadata is marked unavailable/check-failed when the executable is absent or cannot read the file; downloads continue normally.
- Existing transient toasts are not retroactively translated after a language switch, but persistent queue/stage/item content re-renders.

## Recommended next stage

Stage 1.1c: choose the first executable backend and implement OCR over extracted frames with artifacts, queue handling, runtime estimation, and cancellation in the same stage.

## Documentation / project memory notes

The current memory file structure is sufficient. Keep `HANDOFF.md` brief and use this file for validation and limitations.
