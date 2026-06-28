# Codex task: Stage 1.2a — CV metadata over extracted frames + compact settings UI

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

Do not install dependencies automatically.

Do not modify existing base requirements unless clearly necessary and explained:

```text
requirements-cpu.txt
requirements-gpu.txt
requirements-ocr-easyocr.txt
```

## Start mode

Start in Plan Mode first.

This is a medium-size feature task, but keep the implementation deliberately limited. The current Codex 5-hour token window is limited, so avoid broad refactors and do not implement future CV/VLM features.

## Goal

Implement the first lightweight CV stage:

```text
Stage 1.2a — CV metadata over extracted frames + compact settings UI
```

The implemented CV layer should analyze already extracted frame images and write deterministic visual metadata into each queue item folder:

```text
data/queues/<queue_folder>/item_xxx_<source>/cv/
  frames_cv.jsonl
  frames_cv.txt
```

This stage is **not** neural object detection, not YOLO, not VLM, and not a model-based image understanding stage.

CV metadata must work for **any queue item type that produces extracted frames**:

```text
- local video files
- downloaded URL media
- screen recordings
- merged audio+video files
- any future queue item type that has item_xxx/frames/
```

The CV processor must not depend on the original source type. It should consume the item frames directory only.

## Current architecture context

The project already has:

```text
data/queues/<queue_folder>/
  queue_manifest.json
  item_001_<safe_source_name>/
    source/
    downloads/
    transcript/
    frames/
    ocr/
    cv/
    events/
    logs/
```

Existing implemented features include:

```text
- local media queue
- queue output folders
- per-item folders
- transcript outputs
- frame extraction
- EasyOCR over extracted frames
- OCR output under item/ocr/
- mouse/keyboard/session events
- Created files UI
- queue_manifest.json
```

The CV stage must fit into this existing structure.

## Non-goals

Do **not** implement:

```text
- object detection
- YOLO
- VLM analysis
- CLIP embeddings
- image classification
- face/person detection
- model download
- transformers
- torch-based CV
- ultralytics
- OpenCV as a hard dependency
- CV runtime estimate
- smart frame selection
- CV-assisted OCR
- charts/graphs
- overlay images with boxes
```

Do not change OCR behavior.

Do not change transcript behavior.

Do not change frame extraction behavior except for minimal integration needed for CV outputs.

Do not change queue folder architecture.

Do not migrate old outputs.

Do not add a database.

## Dependency / requirements policy

For this stage, prefer lightweight deterministic image processing.

Preferred implementation:

```text
Pillow / PIL + Python standard library
```

Before changing requirements:

1. Inspect existing requirements files.
2. Check whether Pillow is already explicitly listed.
3. If Pillow is already explicitly listed in base requirements, use it.
4. If Pillow is not explicitly listed, create a separate optional requirements file:

```text
requirements-cv-metadata.txt
```

with:

```text
Pillow
```

Do not add Pillow silently only as a transitive dependency.

Do not add OpenCV, YOLO, ultralytics, torch, transformers, timm, CLIP, or VLM dependencies.

Do not create placeholder requirements files for future YOLO/VLM/object detection stages.

If Pillow is unavailable at runtime, the app should fail gracefully for CV metadata and show a clear unavailable/error state. Do not crash the whole queue.

## CV metadata processor

Add a focused processor module, for example:

```text
app/cv_processor.py
```

The processor should accept a frames directory and an output CV directory.

Input:

```text
item_xxx/frames/*.jpg
```

Output:

```text
item_xxx/cv/frames_cv.jsonl
item_xxx/cv/frames_cv.txt
```

The processor should work the same regardless of source type:

```text
local video / URL video / screen recording / merged video
→ frames
→ CV metadata
```

Do not read the original video file inside the CV processor in this stage.

### Per-frame metrics

For each extracted frame, compute deterministic metadata such as:

```text
- frame_index
- frame_file
- timestamp_sec, if it can be parsed from filename or frame index metadata
- width
- height
- brightness
- contrast
- blur_score or sharpness_score
- visual_hash
- diff_score_vs_previous
- near_duplicate
- scene_change
```

Keep metrics simple and deterministic.

### brightness

Normalize to `0.0–1.0`.

### contrast

Normalize to `0.0–1.0` if practical.

### blur_score / sharpness_score

Use a simple deterministic metric.

Acceptable options:

```text
- PIL-only grayscale edge/difference proxy
- variance-like score based on neighboring pixel differences
```

Do not make OpenCV required.

### visual_hash

Use a simple deterministic average-hash or difference-hash implementation based on resized grayscale image.

Do not add `imagehash` dependency unless already present and explicitly justified. Prefer implementing a small hash helper.

Example:

```text
visual_hash: "8f3a91c0d2e4b7a1"
```

### diff_score_vs_previous

Compare current frame against previous frame using a downscaled grayscale representation.

Normalize to `0.0–1.0`.

### near_duplicate

Boolean based on a conservative threshold.

Example:

```text
near_duplicate = diff_score_vs_previous < 0.03
```

Exact threshold may be adjusted, but keep it documented.

### scene_change

Boolean based on a higher threshold.

Example:

```text
scene_change = diff_score_vs_previous > 0.25
```

Exact threshold may be adjusted, but keep it documented.

### First frame behavior

For the first frame:

```json
{
  "diff_score_vs_previous": null,
  "near_duplicate": false,
  "scene_change": true
}
```

or another consistent convention. Document it in tests.

## JSONL output

Write:

```text
item_xxx/cv/frames_cv.jsonl
```

One JSON object per frame.

Example:

```json
{
  "frame_index": 12,
  "frame_file": "frame_000012__t000033.000.jpg",
  "timestamp_sec": 33.0,
  "width": 1920,
  "height": 1080,
  "brightness": 0.42,
  "contrast": 0.18,
  "blur_score": 0.73,
  "visual_hash": "8f3a91c0d2e4b7a1",
  "diff_score_vs_previous": 0.08,
  "near_duplicate": true,
  "scene_change": false
}
```

Use stable key names.

Do not include absolute paths in every JSONL row unless needed. Prefer relative frame filenames. Absolute output paths can be stored in queue/item outputs.

## TXT output

Write:

```text
item_xxx/cv/frames_cv.txt
```

Human-readable summary.

Include at least:

```text
CV metadata summary
Frames analyzed: <n>
Near-duplicates: <n>
Scene changes: <n>
Mean brightness: <value>
Mean contrast: <value>
Mean blur score: <value>

Top scene changes:
<timestamp> — <frame_file> — diff_score <value>
...
```

If no frames are found, write a clear message and return a structured unavailable/empty result rather than crashing.

## Queue integration

Add CV metadata as an optional queue processing step.

It should run after frame extraction.

Expected behavior:

```text
video / URL / recording / merged video
→ frames
→ CV metadata
→ item/cv/frames_cv.jsonl
→ item/cv/frames_cv.txt
```

CV metadata must work for any queue item type that produces extracted frames:

```text
- local video files
- downloaded URL media
- screen recordings
- merged audio+video files
```

The queue integration should not special-case CV by source type. If `item_xxx/frames/` exists and contains supported image frames, CV metadata can run.

If CV metadata is enabled but frame extraction is disabled or no frames exist:

* do not crash the whole queue;
* mark CV as skipped/unavailable for that item;
* show a clear message such as:

```text
CV metadata requires extracted frames.
```

Backend should be defensive even if UI disables invalid combinations.

Update queue item outputs so `Created files` can show:

```text
CV JSONL:
...\item_xxx\cv\frames_cv.jsonl

CV TXT:
...\item_xxx\cv\frames_cv.txt
```

Update `queue_manifest.json` item outputs to include CV paths when created.

## Processing plan / state

Extend the queue item processing plan with a CV section.

Example shape:

```json
{
  "cv": {
    "metadata_enabled": true,
    "object_detection_enabled": false,
    "vlm_enabled": false,
    "yolo_enabled": false
  }
}
```

Exact names may follow existing project conventions.

Only `metadata_enabled` should do real work in this task.

The other fields are placeholders/UI state only.

## UI requirements

Add a new settings subsection:

```text
CV / анализ изображения
```

English:

```text
CV / image analysis
```

Inside it:

```text
[ ] Визуальные метаданные
[ ] Распознавание объектов — скоро
[ ] VLM-анализ — скоро
[ ] YOLO object detection — скоро
```

English:

```text
[ ] Visual metadata
[ ] Object detection — coming soon
[ ] VLM analysis — coming soon
[ ] YOLO object detection — coming soon
```

Only `Visual metadata / Визуальные метаданные` should be enabled.

The other checkboxes/placeholders should be disabled and must not affect processing.

Do not add another nested hierarchy for YOLO yet. Keep the UI flat for this stage.

## Compact settings UI

The block:

```text
Настройки обработки по умолчанию
```

should become more compact with collapsible subsections.

Required behavior:

```text
Настройки обработки по умолчанию — expanded by default

  Аудио / Кадры — expanded by default
  Скачивание по URL — collapsed by default
  OCR / распознавание текста — collapsed by default
  CV / анализ изображения — collapsed by default
```

English equivalents:

```text
Default processing settings — expanded by default

  Audio / Frames — expanded by default
  URL download — collapsed by default
  OCR / text recognition — collapsed by default
  CV / image analysis — collapsed by default
```

Use `<details>` / `<summary>` where practical.

Preserve current functionality and form values.

Do not hardcode Cyrillic in `static/app.js` or `static/index.html`.

Use `static/i18n.js`.

If there is already a pattern for preserving `<details>` state across UI refresh, reuse it. If not, keep the behavior simple and stable.

## Created files UI

Update Created files so CV outputs appear when created:

```text
CV JSONL:
...\item_xxx\cv\frames_cv.jsonl

CV TXT:
...\item_xxx\cv\frames_cv.txt
```

Do not break transcript, frames, OCR, downloads, events, or queue manifest display.

## i18n

Add RU/EN labels for:

```text
CV / анализ изображения
Визуальные метаданные
Распознавание объектов — скоро
VLM-анализ — скоро
YOLO object detection — скоро
CV JSONL
CV TXT
CV metadata requires extracted frames
CV metadata summary
```

English equivalents:

```text
CV / image analysis
Visual metadata
Object detection — coming soon
VLM analysis — coming soon
YOLO object detection — coming soon
CV JSONL
CV TXT
CV metadata requires extracted frames
CV metadata summary
```

Use existing i18n conventions.

## Documentation requirements

Continue the existing docs structure.

Do not remove or rewrite historical docs.

Update:

```text
docs/CODEX_TASKS.md
docs/PROJECT_STATE.md
docs/HANDOFF.md
docs/DECISIONS.md
```

`docs/DECISIONS.md` should include a concise architecture decision:

```text
Stage 1.2a starts with deterministic CV metadata over extracted frames, not neural object detection, YOLO, or VLM. Heavy CV/VLM backends remain future optional modules.
```

Save the full text of this task under:

```text
docs/codex_tasks/
```

Use the actual current date at implementation time.

Filename format:

```text
YYYY-MM-DD_cv_metadata_over_frames.md
```

Example:

```text
docs/codex_tasks/2026-06-28_cv_metadata_over_frames.md
```

The task file must contain the full task text, not only a summary.

## Requirements documentation

If `requirements-cv-metadata.txt` is created, mention it in:

```text
docs/PROJECT_STATE.md
docs/HANDOFF.md
```

Do not create requirements files for future YOLO/VLM stages.

## Tests

Add/update focused tests. Use temporary directories and generated tiny images. Do not require real videos, EasyOCR, Whisper, external downloads, or heavy dependencies.

### CV processor tests

Create tests for:

1. CV processor writes `frames_cv.jsonl`.
2. CV processor writes `frames_cv.txt`.
3. Per-frame records include expected keys.
4. First frame has stable diff/scene behavior.
5. Identical or near-identical frames produce `near_duplicate = true`.
6. Very different frames produce higher `diff_score_vs_previous`.
7. Scene-change threshold works.
8. Empty frames directory returns clear skipped/empty result.
9. Invalid/unreadable frame does not crash the whole processor if reasonable; it is skipped or reported.

Suggested test file:

```text
tests/test_cv_processor.py
```

### Queue integration tests

Add/update tests for:

10. When CV metadata is enabled and frames exist, queue item outputs include CV JSONL/TXT.
11. CV outputs are written under:

```text
item_xxx/cv/
```

12. `queue_manifest.json` includes CV output paths.
13. If CV is enabled but frame extraction/frames are unavailable, item gets a clear CV skipped/unavailable state without crashing the queue.
14. CV metadata is source-type agnostic: tests should cover or assert that CV consumes frames from the item frames directory and does not depend on whether the original item was a local file, URL download, recording, or merged video.
15. For URL items, if downloaded media produces extracted frames, CV outputs should be written under the URL item folder:

```text
data/queues/<queue>/item_xxx_<url_source>/cv/
```

Mock downloads/frame extraction if needed; do not require network access.

### UI/i18n tests

Add/update tests for:

16. `static/index.html` contains CV settings section.
17. CV placeholders exist and are disabled.
18. Default processing settings block is present.
19. Audio/Frames subsection is expanded by default.
20. URL download subsection is collapsed by default.
21. OCR subsection is collapsed by default.
22. CV subsection is collapsed by default.
23. RU/EN i18n keys exist.
24. No hardcoded Cyrillic is added to `static/app.js` or `static/index.html`.

### Regression tests

Existing tests should still pass:

```text
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

Do not run broad discovery if it risks hanging.

If tests fail due to environment permission issues only, report exactly which tests and errors. Do not hide failures.

## Manual test checklist for user

### Test A — CV metadata on local video

1. Start the app.
2. Enter a queue folder name:

```text
cv_metadata_test
```

3. Add a short local video.
4. Enable frame extraction.
5. Enable:

```text
CV / анализ изображения → Визуальные метаданные
```

6. Run queue processing.
7. Confirm outputs exist:

```text
data/queues/<queue>/item_001_<source>/cv/frames_cv.jsonl
data/queues/<queue>/item_001_<source>/cv/frames_cv.txt
```

8. Confirm `Created files` shows CV JSONL/TXT.
9. Confirm `queue_manifest.json` includes CV outputs.

### Test B — CV disabled

1. Add/process a video with frame extraction but CV metadata disabled.
2. Confirm no `frames_cv.jsonl` / `frames_cv.txt` is created.
3. Confirm queue processing still succeeds.

### Test C — CV enabled without frames

1. Disable frame extraction.
2. Enable CV metadata if UI allows it, or test backend behavior through queue settings.
3. Run processing.
4. Confirm queue does not crash and shows a clear skipped/unavailable CV message.

### Test D — compact settings UI

Confirm:

```text
Настройки обработки по умолчанию — expanded
Аудио / Кадры — expanded
Скачивание по URL — collapsed
OCR / распознавание текста — collapsed
CV / анализ изображения — collapsed
```

Confirm future CV placeholders are visible but disabled:

```text
Распознавание объектов — скоро
VLM-анализ — скоро
YOLO object detection — скоро
```

### Test E — URL video with CV metadata

1. Add a short URL video.
2. Enable frame extraction.
3. Enable:

```text
CV / анализ изображения → Визуальные метаданные
```

4. Run queue processing.
5. Confirm URL media is downloaded/processed according to current URL settings.
6. Confirm extracted frames are written under the URL queue item folder.
7. Confirm CV outputs are written under:

```text
data/queues/<queue>/item_xxx_<url_source>/cv/
```

8. Confirm `Created files` shows CV JSONL/TXT.
9. Confirm `queue_manifest.json` includes CV outputs for the URL item.

### Test F — screen recording / merged video with CV metadata

If convenient:

1. Record a short screen recording or use an existing `data/recordings/*.mp4`.
2. Add it to queue or process it through the current supported flow.
3. Enable frame extraction.
4. Enable CV metadata.
5. Confirm outputs are written under:

```text
data/queues/<queue>/item_xxx_<recording_or_merged_source>/cv/
```

## Expected result

After this task:

* The app has a first lightweight CV metadata stage.
* CV metadata runs over extracted frames only.
* CV metadata works for local videos, URL videos, screen recordings, merged videos, and future item types that provide extracted frames.
* No heavy CV/VLM dependencies are introduced.
* Outputs are written under `item_xxx/cv/`.
* `frames_cv.jsonl` contains one record per frame.
* `frames_cv.txt` contains a human-readable summary for the item/video.
* Created files and queue manifest include CV outputs.
* The default processing settings UI is more compact and has a CV section.
* Object detection, VLM, and YOLO are visible only as disabled future placeholders.
* Existing OCR, frame extraction, transcript, queue, and event functionality remain intact.
* No commit is created.
