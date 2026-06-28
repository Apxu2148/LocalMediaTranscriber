# Codex task: OCR/CV settings UI cleanup and default propagation

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

Do not add new dependencies.

Do not install anything automatically.

Do not change OCR/CV processing algorithms in this task.

This is a focused UI/UX cleanup task after Stage 1.2a CV metadata.

## Current state

Stage 1.2a has already been implemented, tested, committed, and pushed.

Implemented before this task:

```text
- deterministic CV metadata over extracted frames;
- app/cv_processor.py;
- item_xxx/cv/frames_cv.jsonl;
- item_xxx/cv/frames_cv.txt;
- compact default settings UI;
- CV section in default processing settings;
- optional requirements-cv-metadata.txt;
- docs/codex_tasks/2026-06-28_cv_metadata_over_frames.md.
```

Manual review found several UI/UX issues:

```text
1. Header contains unnecessary runtime/settings badge:
   Whisper tiny · auto/auto

2. Header contains version line:
   Version: local-dev-YYYYMMDD

3. OCR and CV settings are visually inconsistent:
   OCR uses a selector;
   CV uses checkboxes.

4. OCR-related checkbox/control appears under Audio / Frames.

5. New queue items do not inherit default OCR/CV settings correctly.

6. OCR/CV settings should use checkbox semantics because future OCR/CV architecture may allow several processors to be enabled at the same time.
```

## Goal

Clean up the UI and settings flow:

```text
- remove unnecessary header clutter;
- remove the simple local-dev version line;
- make OCR settings visually consistent with CV settings;
- use checkboxes for OCR and CV;
- do not encode single-selection semantics for OCR/CV;
- move OCR activation into the OCR section;
- ensure default OCR/CV settings are applied to newly added queue items;
- preserve existing EasyOCR and CV metadata behavior.
```

## Critical design decision: OCR/CV checkboxes are future multi-choice controls

Use checkboxes, not radio buttons and not selectors.

Reason:

```text
Future OCR and CV processing should be able to run more than one processor for the same item.
```

Future examples:

```text
OCR:
[x] EasyOCR
[x] Tesseract OCR
[ ] PaddleOCR
[ ] Windows OCR

CV:
[x] Visual metadata
[x] YOLO object detection
[x] VLM analysis
```

In this task:

```text
- only EasyOCR is functional for OCR;
- only Visual metadata is functional for CV;
- all other OCR/CV checkboxes are disabled placeholders;
- do not implement multi-backend execution yet;
- do not implement backend/module-specific output folders yet;
- but do not add UI or state logic that assumes only one OCR/CV option can ever be selected.
```

Do not use `<select>` for OCR in default settings UI.

Do not replace OCR/CV with radio buttons.

Do not enforce “only one checkbox can be checked” logic.

## Future output architecture note

For this task, keep current output paths for backward compatibility.

Current EasyOCR/CV metadata paths may remain as they are.

Do not migrate outputs now.

However, avoid making new assumptions that would block future backend-specific folders.

Future architecture may use structures like:

```text
item_xxx/ocr/
  easyocr/
    frames_ocr.jsonl
    frames_ocr.txt
  tesseract/
    frames_ocr.jsonl
    frames_ocr.txt

item_xxx/cv/
  metadata/
    frames_cv.jsonl
    frames_cv.txt
  yolo/
    frames_yolo.jsonl
    frames_yolo.txt
  vlm/
    frames_vlm.jsonl
    frames_vlm.txt
```

This task should not implement that structure, but should not make it harder later.

## Non-goals

Do **not** implement:

```text
- new OCR backends;
- Tesseract OCR execution;
- PaddleOCR execution;
- Windows OCR execution;
- multi-OCR processing pipeline;
- object detection;
- YOLO;
- VLM;
- CLIP embeddings;
- image classification;
- new CV modules;
- backend-specific OCR/CV output folders;
- Git-aware version endpoint;
- Git commit info in UI;
- new dependency installation;
- model downloads.
```

Do not change the actual EasyOCR processing logic.

Do not change the actual CV metadata processing logic.

Do not change frame extraction behavior.

Do not change queue folder structure.

Do not migrate old outputs.

Do not add a database.

## Header cleanup

In the app header, remove the unnecessary runtime/settings badge:

```text
Whisper tiny · auto/auto
```

Also remove the line:

```text
Version: local-dev-YYYYMMDD
```

For this task, do **not** replace it with git commit info.

Keep useful environment/status text, for example:

```text
Microphone available, system audio available; ffmpeg found
```

Do not break RU/EN localization.

If any tests currently expect the removed version text or badge, update them.

## OCR settings UI: replace selector with checkboxes

Make OCR visually consistent with CV.

### Russian OCR section

Inside:

```text
OCR / распознавание текста
```

show a flat checkbox list:

```text
[ ] EasyOCR
[ ] Tesseract OCR — скоро
[ ] PaddleOCR — скоро
[ ] Windows OCR — скоро
```

### English OCR section

Inside:

```text
OCR / text recognition
```

show:

```text
[ ] EasyOCR
[ ] Tesseract OCR — coming soon
[ ] PaddleOCR — coming soon
[ ] Windows OCR — coming soon
```

Only `EasyOCR` should be functionally enabled in this task.

The other OCR backend checkboxes must be disabled placeholders and must not affect processing.

Do not keep the old OCR engine selector in the main default processing settings UI.

If there is a separate OCR readiness/debug panel elsewhere, preserve it only if it is still useful and not confusing. If preserved, it must not reintroduce conflicting default-processing selector semantics.

## OCR availability behavior

EasyOCR checkbox behavior:

```text
- If EasyOCR is available/installed, the checkbox can be enabled by the user.
- If EasyOCR is unavailable/not installed, the checkbox should be disabled or should show a clear unavailable state.
- Do not allow real OCR processing to start with an unavailable backend.
```

The previous logic where OCR could not be activated unless an available backend was selected is acceptable.

After this UI change, the equivalent rule is:

```text
OCR is active when at least one available OCR backend checkbox is checked.
```

For this task, that means:

```text
OCR is active only when EasyOCR checkbox is checked and EasyOCR is available.
```

If EasyOCR is unavailable, show a clear message such as:

```text
EasyOCR is not available. Install optional dependencies to enable it.
```

Use existing readiness checks if possible.

## Move OCR activation out of Audio / Frames

Currently an OCR-related checkbox/control appears under:

```text
Аудио / Кадры
```

This is confusing.

The `Audio / Frames` section should contain only audio and frame extraction settings.

Move OCR activation into:

```text
OCR / распознавание текста
```

If the checkbox currently under `Audio / Frames` is not OCR activation but a frame-size optimization flag, inspect its actual meaning:

```text
- If it enables OCR processing, move it to OCR.
- If it controls frame resizing/optimization for OCR/CV, keep it under Frames but rename it clearly.
```

Acceptable labels for a real frame-size optimization flag:

```text
RU: Оптимизировать размер кадров для OCR/CV
EN: Optimize frame size for OCR/CV
```

Do not leave a generic checkbox labeled only:

```text
OCR
```

inside the Frames section.

## CV settings UI

Keep the current CV flat checkbox pattern.

### Russian CV section

Inside:

```text
CV / анализ изображения
```

show:

```text
[ ] Визуальные метаданные
[ ] Распознавание объектов — скоро
[ ] VLM-анализ — скоро
[ ] YOLO object detection — скоро
```

### English CV section

Inside:

```text
CV / image analysis
```

show:

```text
[ ] Visual metadata
[ ] Object detection — coming soon
[ ] VLM analysis — coming soon
[ ] YOLO object detection — coming soon
```

Only `Visual metadata / Визуальные метаданные` should be functional.

Other CV options must remain disabled placeholders and must not affect processing.

Do not add nested YOLO hierarchy in this task.

Do not replace CV checkboxes with a selector or radio buttons.

Do not enforce single-choice behavior for CV.

## Default settings must apply to new queue items

Fix default settings propagation.

Expected behavior:

```text
1. User opens Default processing settings.
2. User enables:
   - OCR → EasyOCR;
   - CV → Visual metadata.
3. User adds a new local video / URL item / recording item to queue.
4. The newly added item should initially inherit those default OCR/CV settings.
```

Specifically:

```text
If default OCR EasyOCR is checked:
  new item OCR EasyOCR should be checked/enabled.

If default CV Visual metadata is checked:
  new item CV Visual metadata should be checked/enabled.
```

This should work for queue item types that support frames:

```text
- local video;
- URL media;
- screen recording / recording file;
- merged video, if supported by current flow.
```

If OCR/CV requires frame extraction, backend should remain defensive:

```text
OCR/CV enabled + no frames → skipped/unavailable state, not crash.
```

Do not make existing pending items auto-update when defaults change unless current project behavior already does that.

Required behavior is for newly added items.

## Per-item settings consistency

If the app has per-item controls/settings, they should use the same conceptual model.

OCR per-item model:

```text
[ ] EasyOCR
[ ] Tesseract OCR — coming soon
[ ] PaddleOCR — coming soon
[ ] Windows OCR — coming soon
```

CV per-item model:

```text
[ ] Visual metadata
[ ] Object detection — coming soon
[ ] VLM analysis — coming soon
[ ] YOLO object detection — coming soon
```

Do not leave default settings using checkboxes while per-item settings use a conflicting selector, unless per-item UI does not currently expose OCR/CV settings.

Preserve current item override behavior.

Do not implement real multi-backend execution in this task.

## Processing plan / backward compatibility

Preserve compatibility with existing processing plan shape as much as possible.

If current backend expects something like:

```json
{
  "ocr_enabled": true,
  "ocr_engine": "easyocr"
}
```

or similar, keep producing equivalent values internally when EasyOCR checkbox is checked.

Acceptable mapping for this task:

```text
EasyOCR checkbox checked
→ ocr_enabled = true
→ ocr_engine = "easyocr"
```

EasyOCR checkbox unchecked:

```text
→ ocr_enabled = false
```

Future OCR backend checkboxes are UI placeholders only and should not produce active processing settings.

For CV:

```text
Visual metadata checked
→ cv.metadata_enabled = true
```

Visual metadata unchecked:

```text
→ cv.metadata_enabled = false
```

Keep existing Stage 1.2a CV metadata behavior intact.

Do not perform a large processing-plan migration.

Do not introduce breaking changes to existing queue items.

## Compact settings UI should remain

Keep the compact/collapsible default settings structure introduced in Stage 1.2a.

Expected state:

```text
Default processing settings — expanded by default

  Audio / Frames — expanded by default
  URL download — collapsed by default
  OCR / text recognition — collapsed by default
  CV / image analysis — collapsed by default
```

Russian equivalent:

```text
Настройки обработки по умолчанию — раскрыты по умолчанию

  Аудио / Кадры — раскрыты по умолчанию
  Скачивание по URL — свернуто по умолчанию
  OCR / распознавание текста — свернуто по умолчанию
  CV / анализ изображения — свернуто по умолчанию
```

Preserve current functionality and form values.

Use `<details>` / `<summary>` where practical.

Do not hardcode Cyrillic in:

```text
static/app.js
static/index.html
```

Use `static/i18n.js`.

## i18n

Update RU/EN labels.

Add or update keys for:

```text
EasyOCR
Tesseract OCR — скоро
PaddleOCR — скоро
Windows OCR — скоро
Tesseract OCR — coming soon
PaddleOCR — coming soon
Windows OCR — coming soon
EasyOCR is not available. Install optional dependencies to enable it.
Optimize frame size for OCR/CV
Оптимизировать размер кадров для OCR/CV
```

Also ensure existing CV labels remain localized:

```text
Визуальные метаданные
Распознавание объектов — скоро
VLM-анализ — скоро
YOLO object detection — скоро

Visual metadata
Object detection — coming soon
VLM analysis — coming soon
YOLO object detection — coming soon
```

Do not hardcode Cyrillic in:

```text
static/app.js
static/index.html
```

Use existing `static/i18n.js` conventions.

## Documentation requirements

Continue the existing documentation structure.

Do not remove or rewrite historical docs.

Update the project state/task tracking docs:

```text
docs/CODEX_TASKS.md
docs/PROJECT_STATE.md
docs/HANDOFF.md
```

Update:

```text
docs/DECISIONS.md
```

only if a new architecture decision is made.

This task likely should add or update a concise decision saying:

```text
OCR and CV default settings use checkbox semantics to preserve future multi-processor support. In the current version only EasyOCR and CV Visual metadata are functional; other options are disabled placeholders.
```

Update public/user-facing documentation where relevant:

```text
README.md
```

The README update should be targeted and concise. Do not rewrite the whole README. Mention only what changed if relevant:

```text
- OCR/CV settings now use checkbox-style options.
- EasyOCR is the currently functional OCR option.
- CV Visual metadata is the currently functional CV option.
- Other OCR/CV options are placeholders for future modules.
```

Update the Developer’s Guide:

```text
docs/DEVELOPER.md
```

The Developer’s Guide update should be targeted and concise. Do not rewrite the whole file. Include the architectural note that:

```text
- OCR/CV UI uses checkbox semantics rather than single-select semantics.
- This is intentional to keep future multi-processor OCR/CV support possible.
- Current backend compatibility may still map EasyOCR checkbox to existing ocr_enabled / ocr_engine = easyocr fields.
- Future multi-backend OCR/CV should avoid output overwrites by using backend/module-specific output folders.
```

Save the full text of this task under:

```text
docs/codex_tasks/
```

Use the actual current date at implementation time.

Filename format:

```text
YYYY-MM-DD_ocr_cv_settings_ui_cleanup.md
```

Example:

```text
docs/codex_tasks/2026-06-28_ocr_cv_settings_ui_cleanup.md
```

The task file must contain the full task text, not only a summary.

## Tests

Add/update focused tests.

### UI contract tests

Verify:

```text
1. Header no longer contains Whisper tiny · auto/auto badge.
2. Header no longer contains Version: local-dev.
3. OCR default settings section contains EasyOCR checkbox.
4. OCR default settings section contains disabled future placeholders:
   - Tesseract OCR;
   - PaddleOCR;
   - Windows OCR.
5. OCR engine selector is no longer present in default settings UI.
6. OCR settings use checkboxes, not radio buttons.
7. OCR checkbox UI does not encode single-selection semantics.
8. CV section still contains Visual metadata checkbox.
9. CV future placeholders remain disabled.
10. CV settings use checkboxes, not radio buttons.
11. Generic OCR checkbox is not present under Audio / Frames.
12. If a frame optimization checkbox remains under Frames, its label is explicit:
    - Optimize frame size for OCR/CV;
    - Оптимизировать размер кадров для OCR/CV.
13. Compact settings default open/collapsed behavior remains:
    - Default processing settings expanded;
    - Audio / Frames expanded;
    - URL download collapsed;
    - OCR collapsed;
    - CV collapsed.
```

### i18n tests

Verify:

```text
14. RU/EN keys exist for all new OCR labels.
15. RU/EN keys exist for EasyOCR unavailable message.
16. RU/EN keys exist for frame optimization label if used.
17. Existing CV labels still exist.
18. No new hardcoded Cyrillic is added to static/app.js or static/index.html.
```

### Queue/default propagation tests

Add/update tests to verify:

```text
19. New queue item inherits default EasyOCR enabled setting.
20. New queue item inherits default CV Visual metadata enabled setting.
21. New queue item does not enable OCR when EasyOCR is unavailable.
22. New queue item preserves OCR disabled when default EasyOCR is unchecked.
23. New queue item preserves CV disabled when default Visual metadata is unchecked.
24. Existing queue tests still pass.
```

Use mocks/stubs if needed.

Do not require real EasyOCR execution.

Do not require network access.

Do not require real URL downloads.

### Multi-choice future-proof tests

Add lightweight tests or assertions where practical:

```text
25. OCR options are represented as checkbox controls, not a single select/radio group.
26. CV options are represented as checkbox controls, not a single select/radio group.
27. Disabled future OCR/CV options do not activate processing settings.
28. The implementation does not introduce client-side logic that automatically unchecks one OCR/CV option when another is checked.
```

Do not implement multi-backend execution.

### Documentation tests or checks

If the project has documentation contract tests, update them as needed.

At minimum, verify manually that these files are updated when relevant:

```text
README.md
docs/DEVELOPER.md
docs/CODEX_TASKS.md
docs/PROJECT_STATE.md
docs/HANDOFF.md
docs/DECISIONS.md, if a decision was added
docs/codex_tasks/YYYY-MM-DD_ocr_cv_settings_ui_cleanup.md
```

### Regression tests

Existing tests should still pass:

```text
tests.test_cv_processor
tests.test_queue_manager
tests.test_runtime_estimate
tests.test_ocr_processor
tests.test_frame_extractor
tests.test_ui_contract
tests.test_i18n
tests.test_http_smoke
```

## Validation commands

Run:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest tests.test_cv_processor
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager
.\.venv\Scripts\python.exe -m unittest tests.test_runtime_estimate
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_processor
.\.venv\Scripts\python.exe -m unittest tests.test_frame_extractor
.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
git diff --check
git diff --stat
git status --short
```

CRLF warnings are acceptable.

Negative-path test logs such as expected failures, invalid backends, download failures, device busy, or frame extraction failures are acceptable if the final unittest result is `OK`.

Do not run broad discovery if it risks hanging.

If tests fail due to environment-only issues, report the exact tests and exact errors. Do not hide failures.

## Manual test checklist for user

### Test A — Header cleanup

1. Start the app.
2. Confirm top-right badge is gone:

   * no `Whisper tiny · auto/auto`.
3. Confirm version line is gone:

   * no `Version: local-dev-YYYYMMDD`.
4. Confirm useful device/ffmpeg status remains visible.

### Test B — Default settings UI

1. Open `Default processing settings`.
2. Confirm:

   * `Audio / Frames` contains only audio/frame settings;
   * OCR activation is inside `OCR / text recognition`;
   * CV activation is inside `CV / image analysis`.
3. Confirm OCR uses checkboxes, not a selector.
4. Confirm CV uses checkboxes.
5. Confirm OCR disabled placeholders are visible:

   * Tesseract OCR — coming soon;
   * PaddleOCR — coming soon;
   * Windows OCR — coming soon.
6. Confirm CV disabled placeholders are visible:

   * Object detection — coming soon;
   * VLM analysis — coming soon;
   * YOLO object detection — coming soon.
7. Confirm checkbox UI does not behave like radio buttons.

### Test C — Default OCR/CV propagation

1. In default settings enable:

   * OCR → EasyOCR;
   * CV → Visual metadata.
2. Add a new video item.
3. Confirm the new item has OCR EasyOCR enabled.
4. Confirm the new item has CV Visual metadata enabled.

### Test D — Defaults off

1. In default settings disable:

   * OCR → EasyOCR;
   * CV → Visual metadata.
2. Add a new video item.
3. Confirm the new item has OCR disabled.
4. Confirm the new item has CV metadata disabled.

### Test E — Processing still works

1. Add a short local video.
2. Enable frame extraction.
3. Enable OCR EasyOCR if available.
4. Enable CV Visual metadata.
5. Run queue processing.
6. Confirm expected outputs:

   * transcript if audio/transcription enabled;
   * frames;
   * OCR outputs if OCR enabled and available;
   * CV outputs:

     * `item_xxx/cv/frames_cv.jsonl`;
     * `item_xxx/cv/frames_cv.txt`.

### Test F — EasyOCR unavailable behavior

If EasyOCR is unavailable in the environment:

1. Open default OCR settings.
2. Confirm EasyOCR cannot be enabled or shows a clear unavailable state.
3. Confirm queue processing does not crash because of unavailable OCR.

## Expected result

After this task:

```text
- Header is cleaner.
- Runtime/settings badge is removed.
- Version line is removed.
- OCR and CV settings use consistent checkbox-style UI.
- OCR/CV checkbox UI is future-proof for multiple processors.
- UI does not encode single-selection semantics for OCR/CV.
- OCR activation is no longer placed under Audio / Frames.
- EasyOCR remains the only functional OCR backend.
- Future OCR backends are visible only as disabled placeholders.
- CV Visual metadata remains the only functional CV option.
- Future CV options remain disabled placeholders.
- New queue items correctly inherit default OCR/CV settings.
- README.md is updated with concise user-facing notes.
- docs/DEVELOPER.md is updated with concise developer/architecture notes.
- Existing EasyOCR, CV metadata, queue, frame extraction, transcription, and URL behavior remain intact.
- No commit is created.
```
