# Project state

## Current milestone

Stage 1.1b, URL retention cleanup, URL download profiles, and video resolution controls are implemented and validated. URL jobs now snapshot a configurable download profile plus optional max video height, and frame extraction can optionally downscale saved JPEGs. OCR execution remains intentionally disabled.

## URL download profiles and diagnostics

- Persisted profiles cover Auto, extraction-friendly, quality/size, WebM/MP4/MKV/MOV/AVI preferences, audio-friendly, and an advanced custom yt-dlp format string.
- `processing_plan.url_download` freezes the profile/custom/log settings for each new item and survives pending-item edits.
- Download metadata records container, codecs, resolution, FPS, size, elapsed download time, selected profile, and actual format expression when available.
- URL frame jobs record elapsed extraction time, frame count, and seconds per frame in queue/job metadata and logs.
- The persistent queue-start message now uses the existing dynamic renderer, fixing the observed RU-to-EN switch issue. Stage/progress and per-item content already re-render from keys/status snapshots.

## Video resolution controls

- `url_download.max_video_height` persists as `auto`, `480`, `720`, `1080`, `1440`, or `2160`; invalid values fall back to `auto`.
- Built-in yt-dlp video profiles prepend bounded selectors and keep the original profile string as the final fallback. `custom` format strings stay unchanged and ignore max height.
- Direct media URLs keep their source media unchanged and only record `url_download_max_video_height` in diagnostics.
- `frames.max_frame_size` persists as `original`, `width_1920`, `width_1280`, `width_960`, or `width_640`; invalid values fall back to `original`.
- Frame extraction remains OpenCV-backed and resizes decoded frames before JPEG encoding only when downscaling is requested. Aspect ratio is preserved and smaller videos are never upscaled.
- New items snapshot `processing_plan.url_download.max_video_height` and `processing_plan.frames.max_frame_size`; the frame value is mirrored into legacy `frame_extraction.max_frame_size`.

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
- `app/frame_settings_manager.py`, `app/frame_extractor.py`, `app/runtime_estimate.py`, queue/main integration, compact localized resolution controls, and focused resolution/estimate/UI tests.

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

Video resolution controls:

- `.venv\Scripts\python.exe -m unittest tests.test_frame_extractor tests.test_url_downloader tests.test_queue_manager tests.test_runtime_estimate tests.test_http_smoke tests.test_ui_contract tests.test_i18n` (126 tests)
- `git diff --check` passed with CRLF warnings only.
- The first sandboxed test run failed with Windows `PermissionError` during temp-file unlink/replace cleanup; the same focused suite passed when rerun with normal filesystem permissions.

## Manual checks still required

- Start with `run.bat` and exercise all four selector options.
- Confirm Tesseract path visibility and readiness on the local machine.
- Confirm selection persists after refresh.
- Smoke-test transcription, frame extraction, estimates, and URL cancellation.
- With URL media retention disabled, cancel during frame extraction and confirm the owned download is removed; repeat with retention enabled and confirm it remains.
- Save Prefer WebM, refresh, and confirm persistence; compare Auto, WebM, MP4, and extraction-friendly profiles on the same short URL using job/log diagnostic fields.
- Save a URL max height and frame max size, refresh, add a new URL/video item, and confirm the new item snapshots those values while older pending items keep their previous plans.
- Extract frames from a video wider than the selected max size and verify `frames_index.json` records the downscaled dimensions; repeat with a smaller video and confirm no upscaling.
- Switch RU to EN while a queue is active and confirm the persistent queue-start/stage/per-item messages update.

## Known limitations

- No backend performs OCR or creates OCR artifacts.
- Optional dependencies are detected but never installed or initialized.
- PaddleOCR and Windows OCR are readiness-only experimental entries.
- Profiles are best-effort because sites expose different formats. Direct media URLs keep their source format, MOV/AVI preferences do not force remuxing, and no per-URL format listing is implemented.
- URL max height is best-effort and can fall back to a higher format when the source does not expose a matching bounded format. It is not applied to custom yt-dlp strings or direct media URLs.
- Frame max size changes saved extracted JPEG dimensions only; it does not change the source decoder path or force a new FFmpeg extraction pipeline.
- `ffprobe` metadata is marked unavailable/check-failed when the executable is absent or cannot read the file; downloads continue normally.
- Existing transient toasts are not retroactively translated after a language switch, but persistent queue/stage/item content re-renders.

## Backlog notes

- Polish URL finalizing/progress feedback after a direct or yt-dlp download reaches 100% but before post-download probing, queue handoff, retention decisions, or frame-extraction setup finishes. The current stage/progress behavior is stable, but that finalizing window can be made clearer for users.

## Recommended next stage

Stage 1.1c: choose the first executable backend and implement OCR over extracted frames with artifacts, queue handling, runtime estimation, and cancellation in the same stage.

## Documentation / project memory notes

The current memory file structure is sufficient. Keep `HANDOFF.md` brief and use this file for validation and limitations.
