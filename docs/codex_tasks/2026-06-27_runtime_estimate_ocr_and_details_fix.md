# Codex task: Runtime estimate details fix + OCR estimate component

## Project

Work only in:

```text
C:\Python\LocalMediaTranscriber
```

Do **not** modify:

```text
C:\Python\LocalAudioTranscriber
```

Do not commit. The user will test and commit manually.

Do not add new BAT files.

## Start mode

Start in Plan Mode first.

This task touches runtime estimate logic and frontend queue/status rendering. It should remain focused and should not become a broad refactor.

First inspect the current estimate implementation and explain:

1. what is currently included in runtime estimate;
2. whether transcription is included;
3. whether frame extraction is included;
4. whether OCR is included;
5. why “Подробности оценки” auto-collapses after refresh.

Then implement only the focused fix described below.

## Background

Stage 1.1c EasyOCR is already implemented and pushed.

Current OCR behavior:

```text
video / URL / screen recording
→ extracted frames
→ EasyOCR
→ frames_ocr.jsonl
→ frames_ocr.txt
```

A real manual test showed:

```text
Video length: about 2.5 minutes
Extracted frames: 52
Frame max size: width 1920
OCR time: about 8–9 minutes
Total processing time: about 10 minutes
Estimate shown before processing: about 1 minute
```

This suggests that the current “Оценить время” logic may include transcription and/or frame extraction, but may not include EasyOCR.

Also, when the user opens “Подробности оценки”, the details block closes automatically after about one second, probably because queue/status refresh re-renders the UI.

## Goal

Implement a focused fix for runtime estimate UX and OCR estimate.

Required result:

1. “Подробности оценки” should stay open/closed across periodic UI refreshes.
2. Runtime estimate should clearly include OCR when OCR is enabled and EasyOCR is available.
3. OCR estimate must be cheap: do **not** OCR the whole first minute.
4. OCR estimate should use at most 3 sampled frames.
5. Estimate details should show a breakdown:

   * transcription;
   * frame extraction;
   * OCR;
   * total.
6. If OCR cannot be estimated, the UI should say so clearly instead of silently excluding it.

## Scope

This is a focused runtime estimate and UI-state task.

Likely files:

```text
app/main.py
app/queue_manager.py
app/ocr_processor.py
app/ocr_manager.py
static/app.js
static/i18n.js
static/index.html
tests/test_queue_manager.py
tests/test_ui_contract.py
tests/test_i18n.py
tests/test_http_smoke.py
docs/CODEX_TASKS.md
docs/PROJECT_STATE.md
docs/codex_tasks/
```

Only modify files that are actually needed.

## Strict non-goals

Do not implement `data/queues/...` output reorganization.

Do not implement CV.

Do not change OCR output format.

Do not change `frames_ocr.jsonl` schema.

Do not change actual queue processing order.

Do not change EasyOCR processing behavior for real processing.

Do not add PaddleOCR, Tesseract, or Windows OCR processing.

Do not install dependencies.

Do not modify:

```text
requirements-cpu.txt
requirements-gpu.txt
requirements-ocr-easyocr.txt
```

Do not make per-item “Параметры обработки элемента” collapsed by default in this task unless it is a truly trivial one-line adjacent fix. Prefer keeping this task focused.

## Part 1 — Fix estimate details auto-collapse

### Problem

When the user opens “Подробности оценки”, it automatically collapses after the next UI refresh.

### Expected behavior

* If user opens estimate details, it stays open across queue/status refreshes.
* If user closes estimate details, it stays closed across queue/status refreshes.
* This should work while the queue item is processing.
* This state does not need to survive full browser page reload.

### Implementation guidance

Use the same pattern already used for preserving collapsible per-item processing settings, if applicable.

Use a stable frontend key based on queue item identity, for example:

```text
job_id + item index + estimate/details identifier
```

or another stable identifier already used in `static/app.js`.

Do not add backend state for this unless absolutely necessary.

## Part 2 — Verify and fix OCR estimate

### Problem

Manual observation suggests OCR may not be included in runtime estimate.

### Required behavior

If OCR is enabled for an item and selected OCR backend is EasyOCR:

1. Runtime estimate should include an OCR component.
2. Estimate details should show OCR separately.
3. Total estimate should include OCR.
4. If OCR is unavailable or cannot be estimated, estimate details should explicitly say that OCR is not included or cannot be estimated.

## OCR estimate strategy

OCR estimate must be cheap.

Do **not** run OCR on:

```text
- all frames;
- all frames from the first minute;
- 20 frames from a 3-second frame interval sample.
```

Use at most:

```text
max 3 OCR sample frames
```

### Sampling strategy

Preferred strategy:

```text
Use up to 3 deterministic pseudo-random sampled frames from the expected frame timeline.
```

Rules:

1. If expected frame count is 0, OCR estimate should be 0 or unavailable with explanation.
2. If expected frame count is 1–3, use all expected frames.
3. If expected frame count is more than 3, select 3 pseudo-random frames.
4. Sampling must be deterministic for the same item/source/settings.
5. Use a stable seed based on source path / URL / job id / item index or another stable item key.
6. If practical, avoid selecting frames that are too close together.
7. If practical, avoid fully blank/near-empty frames, but do not overbuild image analysis in this task.

### Important

Do not make repeated clicks on “Оценить время” produce totally different estimates for the same item. That is why deterministic pseudo-random sampling is preferred over fully random sampling.

## How to obtain sample frames

Inspect the current estimate implementation.

Possible acceptable approaches:

### Preferred

Reuse existing sample frame extraction logic if it already exists for runtime estimate.

### Acceptable

Create temporary sample frames only for OCR estimate, but only up to 3 frames.

Requirements:

* do not pollute final output folders with estimate-only frames;
* clean up temporary estimate frames when practical;
* do not break existing frame extraction outputs;
* do not change actual processing behavior.

### Fallback

If it is too risky to extract temporary OCR sample frames in this task, implement a clear fallback estimate using previous OCR benchmark or a conservative default sec/frame, and document the limitation.

But first try to implement real 1–3 frame OCR sampling if it is straightforward.

## OCR estimate formula

Use a simple MVP formula:

```text
ocr_total_sec = ocr_sec_per_frame * expected_frame_count
```

Where:

```text
ocr_sec_per_frame = average or median OCR duration across sampled frames
expected_frame_count = expected extracted frame count from video duration and frame interval
```

Prefer median if easy; average is acceptable.

If the first OCR frame is significantly slower due to model warmup, it is acceptable for MVP to include that in the estimate. Add a UI note:

```text
First EasyOCR run may be slower because models may initialize or download.
```

If previous OCR benchmark data is already stored somewhere, it may be used as a fallback or comparison, but do not build a complex benchmark cache in this task.

## Estimate details UI

The estimate details should show a clear breakdown.

Example in Russian:

```text
Оценка времени:
Транскрибация: ~45 сек
Извлечение кадров: ~20 сек
OCR: ~8 мин 40 сек
Итого: ~9 мин 45 сек

OCR:
Ожидаемые кадры: 52
Тестовые кадры: 3
Среднее OCR/кадр: ~10.0 сек
Движок: EasyOCR
Примечание: первый запуск EasyOCR может быть медленнее.
```

Example in English:

```text
Runtime estimate:
Transcription: ~45 sec
Frame extraction: ~20 sec
OCR: ~8 min 40 sec
Total: ~9 min 45 sec

OCR:
Expected frames: 52
Sampled frames: 3
Average OCR/frame: ~10.0 sec
Engine: EasyOCR
Note: first EasyOCR run may be slower.
```

Use i18n. Do not hardcode Cyrillic in `static/app.js` or `static/index.html`.

## Behavior when EasyOCR is not installed or unavailable

If OCR is enabled but EasyOCR is unavailable:

* do not crash;
* do not attempt OCR estimate;
* show in details that OCR estimate is unavailable because EasyOCR is unavailable;
* total estimate should either:

  * exclude OCR with a clear warning; or
  * mark total as incomplete.

Preferred:

```text
OCR: unavailable, EasyOCR is not installed or not available.
Total estimate excludes OCR.
```

## Behavior when OCR is disabled

If OCR is disabled:

* estimate should behave as before;
* no OCR sampling should run;
* estimate details may show OCR as disabled or omit OCR row.

## Performance constraints

The estimate button should remain reasonably responsive.

Hard requirements:

```text
- OCR estimate must process at most 3 frames.
- OCR estimate must not process all frames from the first minute.
- OCR estimate must not run full queue processing.
```

If OCR model initialization makes the first OCR estimate slow, that is acceptable for this stage, but the UI/docs should mention it.

## Task history requirement

Save the full text of this task in a new markdown file under:

```text
docs/codex_tasks/
```

Use the actual current date at the time of implementation, not an example date from this prompt.

Filename format:

```text
YYYY-MM-DD_runtime_estimate_ocr_and_details_fix.md
```

Example:

If today is `2026-06-27`, use:

```text
docs/codex_tasks/2026-06-27_runtime_estimate_ocr_and_details_fix.md
```

Also update:

```text
docs/CODEX_TASKS.md
```

The file in `docs/codex_tasks/` must contain the full task text, not only a summary.

## Documentation

Update only if needed:

```text
docs/PROJECT_STATE.md
docs/CODEX_TASKS.md
```

README update is optional. Do it only if the runtime estimate behavior needs user-facing documentation.

Update `docs/DECISIONS.md` only if a real architecture decision is made.

## Tests

Add or update tests without requiring real EasyOCR execution where possible.

Use mocks/fakes for OCR estimate tests.

Required test intent:

### Estimate composition

1. OCR disabled: estimate behavior remains compatible with previous behavior.
2. OCR enabled + EasyOCR available: estimate includes OCR component.
3. OCR enabled + EasyOCR unavailable: estimate does not crash and clearly marks OCR estimate unavailable.
4. OCR estimate uses at most 3 sampled frames.
5. Expected frame count is used to scale OCR estimate.
6. Total estimate includes OCR when OCR estimate is available.

### Sampling

7. Sampling is deterministic for the same item/source/settings.
8. Sampling does not select more than 3 frames.
9. If expected frames <= 3, all expected frames may be used.

### UI

10. “Подробности оценки” open/closed state is preserved across refresh/re-render.
11. Estimate details show OCR breakdown fields when OCR is enabled.
12. No hardcoded Cyrillic is added to `static/app.js` or `static/index.html`.
13. Existing i18n tests pass.

### Regression

14. Existing queue tests pass.
15. Existing OCR processor tests pass.
16. Existing HTTP smoke tests pass.

## Validation commands

Run focused validation:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_processor
.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
git diff --check
git diff --stat
git status --short
```

CRLF warnings are acceptable.

Do not run broad discovery if it risks hanging.

## Manual test checklist for user

After implementation:

1. Start app:

```powershell
.\run.bat
```

2. Add a short video item.
3. Enable:

   * transcription;
   * frame extraction;
   * OCR with EasyOCR.
4. Use frame interval that creates a meaningful number of frames, for example 3–10 seconds.
5. Click “Оценить время”.
6. Open “Подробности оценки”.
7. Confirm the details block stays open after refresh.
8. Confirm estimate details show:

   * transcription estimate;
   * frame extraction estimate;
   * OCR estimate;
   * total estimate;
   * expected frame count;
   * sampled OCR frame count;
   * OCR sec/frame.
9. Confirm OCR estimate uses no more than 3 frames.
10. Run actual processing and compare estimate with real duration.
11. Confirm old flows still work when OCR is disabled.

## Expected result

After this task:

* “Подробности оценки” no longer auto-collapses during UI refresh.
* Runtime estimate explicitly accounts for EasyOCR when OCR is enabled and available.
* OCR estimate uses at most 3 deterministic pseudo-random sampled frames.
* The user can see a clear estimate breakdown including OCR.
* No dependency files are changed.
* No commit is created.
