# Codex task: Per-item OCR backend selector + no-audio runtime estimate robustness

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

Do not add BAT files.

Do not install dependencies.

Do not modify requirement files:

```text
requirements-cpu.txt
requirements-gpu.txt
requirements-ocr-easyocr.txt
```

## Current context

The current working tree already contains the uncommitted implementation of:

```text
Runtime estimate details fix + OCR estimate component
```

Current implemented behavior:

* runtime estimate includes OCR when OCR is enabled and EasyOCR is available;
* OCR estimate uses deterministic sampling of at most 3 temporary frames;
* estimate details preserve open/closed state across queue refreshes;
* EasyOCR import is lazy in `app/ocr_processor.py`;
* local validation passed.

Manual UI testing found two remaining defects that should be fixed before commit.

## Defect 1 — Missing per-item OCR backend selector

### Problem

There is an OCR checkbox in per-item processing settings, but there is no per-item OCR backend selector.

Current bad UX:

```text
1. User adds item to queue.
2. At add time, global OCR backend is not EasyOCR.
3. The item processing plan snapshot does not use EasyOCR.
4. The user cannot conveniently enable EasyOCR OCR for this existing item.
5. Workaround: delete item, change global OCR settings, add item again.
```

This should be fixed.

### Goal

Add an OCR backend selector inside per-item processing settings.

The user should be able to:

```text
1. Add an item to the queue.
2. Open item processing settings.
3. Select OCR backend for that item, for example EasyOCR.
4. Enable OCR for that item if the selected backend is available.
5. Run runtime estimate and processing without deleting/re-adding the item.
```

### Expected UI

Inside:

```text
Параметры обработки элемента / Item processing settings
```

near the OCR checkbox, add a selector:

Russian:

```text
OCR-движок
Auto
EasyOCR
Tesseract
PaddleOCR
Windows OCR
```

English:

```text
OCR backend
Auto
EasyOCR
Tesseract
PaddleOCR
Windows OCR
```

Use existing backend labels/status data if available.

Do not hardcode Cyrillic in `static/app.js` or `static/index.html`.

### Required behavior

The selector must update item-level processing plan data, preferably:

```text
processing_plan.ocr.backend
```

or the existing equivalent field if the current structure uses another name.

If the user selects EasyOCR and EasyOCR is available:

* OCR checkbox can be enabled;
* runtime OCR estimate can run;
* OCR processing can run.

If the selected backend is unavailable:

* UI should not crash;
* either OCR checkbox should be disabled or the UI should show a clear unavailable reason;
* runtime estimate should not crash;
* actual OCR processing should not start with an unavailable backend.

If OCR is enabled for an item, frame extraction must still be required/enabled as before.

The item summary should update to reflect the selected OCR backend, for example:

```text
OCR: EasyOCR / ru, en
```

or the equivalent current summary format.

### Non-goals for Defect 1

Do not implement actual OCR processing for PaddleOCR, Tesseract, or Windows OCR.

Do not add new OCR dependencies.

Do not change OCR output schema.

Do not change `frames_ocr.jsonl`.

Do not change `frames_ocr.txt`.

Do not refactor the entire processing plan architecture.

## Defect 2 — Runtime estimate should not fail completely for video-only files with no audio stream

### Problem

Manual test file:

```text
C:\Python\LocalMediaTranscriber\data\recordings\screen2_20260626_235733__3fps.mp4
```

`ffprobe` shows that the file has only a video stream:

```text
Stream #0:0 Video: mpeg4 ... 1920x1080 ... 3 fps
```

There is no audio stream.

When this item has audio enabled in its processing plan, runtime estimate fails with:

```text
Ошибка оценки
Не удалось подготовить пробный фрагмент.
```

But frame extraction and OCR can still be estimated.

The estimate should not fail completely just because the audio component cannot be estimated.

### Goal

Make runtime estimate robust when audio is enabled but the media file has no audio stream.

Expected behavior:

* audio component is marked unavailable / no audio stream;
* frame extraction estimate still runs;
* OCR estimate still runs if OCR is enabled and EasyOCR is available;
* total estimate is shown for available stages;
* UI clearly says that audio is excluded or unavailable.

### Expected UI behavior

For a video-only file with audio enabled:

Russian example:

```text
Аудио: недоступно — в файле нет аудиодорожки
Кадры: примерно ...
OCR: примерно ...
Итого: примерно ... без аудио
```

English example:

```text
Audio: unavailable — no audio stream found
Frames: about ...
OCR: about ...
Total: about ... excluding audio
```

If total excludes audio, this must be explicit.

### Required backend behavior

In runtime estimate logic:

1. Detect or gracefully handle missing audio stream.
2. Do not let audio sample preparation failure abort the whole estimate when frames/OCR can still be estimated.
3. Return structured estimate data that lets the UI render:

   * audio unavailable reason;
   * frames estimate;
   * OCR estimate;
   * total estimate excluding unavailable components.

Prefer detecting missing audio stream using existing metadata or ffprobe helpers if available.

If exact detection is risky, catching the specific audio sample preparation failure and converting it into an audio unavailable component is acceptable.

Do not silently swallow unrelated unexpected exceptions.

### Non-goals for Defect 2

Do not change real transcription processing behavior in this task.

Do not change queue processing order.

Do not automatically disable audio in the item settings.

Do not modify actual media files.

Do not create audio tracks.

Do not change frame extraction output.

Do not change OCR output.

## Scope

Likely files:

```text
app/runtime_estimate.py
app/main.py
app/ocr_manager.py
app/queue_manager.py
static/app.js
static/i18n.js
tests/test_runtime_estimate.py
tests/test_queue_manager.py
tests/test_ui_contract.py
tests/test_i18n.py
tests/test_http_smoke.py
docs/CODEX_TASKS.md
docs/codex_tasks/
```

Only modify files that are actually needed.

## Task history requirement

Save the full text of this task in a new markdown file under:

```text
docs/codex_tasks/
```

Use the actual current date at the time of implementation, not an example date from this prompt.

Filename format:

```text
YYYY-MM-DD_per_item_ocr_backend_and_no_audio_estimate.md
```

Example:

If today is `2026-06-27`, use:

```text
docs/codex_tasks/2026-06-27_per_item_ocr_backend_and_no_audio_estimate.md
```

Also update:

```text
docs/CODEX_TASKS.md
```

The file in `docs/codex_tasks/` must contain the full task text, not only a summary.

## Tests

Add or update tests using mocks/fakes where practical. Do not require real EasyOCR execution in unit tests.

### Required test intent — per-item OCR backend selector

1. UI contains per-item OCR backend selector.
2. Selector uses i18n labels.
3. No hardcoded Cyrillic is added to `static/app.js` or `static/index.html`.
4. Changing per-item OCR backend updates item processing plan.
5. Selecting EasyOCR allows OCR to be enabled when EasyOCR is available.
6. Selecting unavailable backend does not crash and reports unavailable state.
7. Existing OCR checkbox behavior remains compatible.

### Required test intent — no-audio estimate robustness

8. Runtime estimate with audio enabled and no audio stream does not fail completely.
9. Audio component is marked unavailable with a clear reason.
10. Frames estimate still appears.
11. OCR estimate still appears when OCR is enabled and EasyOCR is available.
12. Total estimate excludes unavailable audio and makes exclusion explicit.
13. Existing successful audio estimate path still works.
14. Existing OCR estimate tests still pass.

### Regression tests

15. Queue tests still pass.
16. OCR processor tests still pass.
17. UI/i18n/http smoke tests still pass.

## Validation commands

Run:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest tests.test_runtime_estimate
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_processor
.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
git diff --check
git diff --stat
git status --short
```

If `tests.test_frame_extractor` is changed or relevant helpers are touched, also run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_frame_extractor
```

CRLF warnings are acceptable.

## Manual test checklist for user

### Test A — per-item OCR backend

1. Start app:

```powershell
.\run.bat
```

2. Set global OCR backend to something other than EasyOCR, or leave it not selected.
3. Add a video item.
4. Open item processing settings.
5. Select EasyOCR in the item-level OCR backend selector.
6. Enable OCR.
7. Click “Оценить время”.
8. Confirm OCR estimate works.
9. Confirm item summary shows OCR with EasyOCR.

### Test B — no-audio video estimate

Use video-only file:

```text
C:\Python\LocalMediaTranscriber\data\recordings\screen2_20260626_235733__3fps.mp4
```

This file has no audio stream.

1. Add the file to queue.
2. Keep audio enabled.
3. Enable frame extraction.
4. Enable OCR with EasyOCR.
5. Click “Оценить время”.
6. Confirm estimate does not fail completely.
7. Confirm audio is shown as unavailable / no audio stream.
8. Confirm frames estimate is shown.
9. Confirm OCR estimate is shown.
10. Confirm total estimate excludes audio or is marked partial.

### Test C — normal video with audio

1. Add a video with audio.
2. Enable audio, frames, OCR.
3. Click “Оценить время”.
4. Confirm audio, frames, OCR, and total are shown normally.

## Expected result

After this task:

* User can select OCR backend per queue item.
* User can enable EasyOCR for an existing item without deleting/re-adding it.
* Runtime estimate no longer fails completely for video-only files with no audio stream.
* Estimate details clearly show unavailable audio and continue frames/OCR estimate.
* No requirements are changed.
* No commit is created.
