# Codex task: Stage 1.1c — EasyOCR over existing extracted frames

## Project

Work only in:

```text
C:\Python\LocalMediaTranscriber
```

Do **not** modify:

```text
C:\Python\LocalAudioTranscriber
```

Do not work in any other project folder.

Do not commit. The user will test and commit manually.

Do not add new BAT files.

## Start mode

Start in Plan Mode first.

This task touches optional OCR dependencies, OCR backend logic, queue processing, outputs, UI, i18n, and tests.

First inspect the current implementation and produce a short implementation plan. Then proceed only if the plan is straightforward.

If this requires a broad architecture refactor, stop and report.

## Task history requirement

Save the full text of this task in a new markdown file under:

```text
docs/codex_tasks/
```

Use the actual current date at the time of implementation, not an example date from this prompt.

Filename format:

```text
YYYY-MM-DD_stage_1_1c_easyocr_over_frames.md
```

Example:

If today is `2026-06-26`, use:

```text
docs/codex_tasks/2026-06-26_stage_1_1c_easyocr_over_frames.md
```

Also update:

```text
docs/CODEX_TASKS.md
```

The file in `docs/codex_tasks/` must contain the full task text, not only a summary.

## Dependency policy

The project currently has:

```text
requirements-cpu.txt
requirements-gpu.txt
```

For this task, add a new optional OCR requirements file:

```text
requirements-ocr-easyocr.txt
```

Rules:

1. Do not install dependencies automatically.
2. Do not modify `requirements-cpu.txt`.
3. Do not modify `requirements-gpu.txt`.
4. Create `requirements-ocr-easyocr.txt` for EasyOCR optional dependencies.
5. Keep EasyOCR optional: the app must start normally when EasyOCR is not installed.
6. If EasyOCR is not installed, readiness/status should show EasyOCR as unavailable.
7. The user will manually install OCR dependencies with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr-easyocr.txt
```

Suggested content for `requirements-ocr-easyocr.txt`:

```text
easyocr
```

If you think additional dependency pins are necessary, report the recommendation. Do not silently add heavy dependencies beyond EasyOCR unless required.

## Current context

The project already supports:

* local audio/video transcription;
* URL audio/video transcription;
* local/URL frame extraction;
* queue processing;
* per-item `processing_plan`;
* runtime estimate/test-run;
* URL download profiles;
* URL max download height;
* extracted frame max size;
* URL cancellation and downloaded media cleanup;
* OCR backend selector/readiness detection for:

  * Tesseract;
  * EasyOCR;
  * PaddleOCR;
  * Windows OCR.

Important: OCR backend selector/readiness exists, but real OCR processing over frames is not implemented yet.

Before changing code:

1. Read `docs/HANDOFF.md`.
2. Read `docs/PROJECT_STATE.md`.
3. Read `docs/CODEX_TASKS.md`.
4. Inspect `app/ocr_manager.py`.
5. Inspect `app/queue_manager.py`.
6. Inspect `app/frame_extractor.py`.
7. Inspect current frame output structure and metadata.
8. Inspect current UI placeholders for OCR.
9. Inspect i18n/UI tests.

## Concept

OCR means Optical Character Recognition: recognizing text in images.

This task should process already extracted frames:

```text
video / URL / screen recording
→ extracted frames
→ EasyOCR
→ frames_ocr.jsonl + frames_ocr.txt
```

Mouse/keyboard events are not part of this task. In the future they may be used as frame-selection triggers, but not now.

## Goal

Implement first real OCR processing backend:

```text
EasyOCR over existing extracted frames
```

After this task, the user should be able to:

1. Install optional EasyOCR dependencies.
2. Select EasyOCR as OCR backend.
3. Enable OCR for a queue item.
4. Process a video/URL with frame extraction.
5. Get OCR results from extracted frames.
6. Open output files with recognized text and numbers.

## Strict non-goals

Do not implement PaddleOCR.

Do not implement Windows OCR.

Do not implement real Tesseract OCR processing unless trivial and already present.

Do not implement CV processing.

Do not implement Smart Frame Extraction.

Do not implement mouse/keyboard-triggered frames.

Do not implement LLM analysis.

Do not implement VLM OCR.

Do not add OCR over live screen recording in real time.

Do not add automatic dependency installation.

Do not change URL download behavior.

Do not change frame extraction behavior except what is strictly necessary to pass frame paths into OCR.

Do not break existing audio/video/URL queue behavior.

## Required behavior

### 1. Optional EasyOCR adapter

Add an EasyOCR adapter/module.

Possible module names:

```text
app/ocr_processor.py
app/easyocr_processor.py
app/ocr_easyocr.py
```

Use project-consistent naming.

Requirements:

* use optional import;
* if `easyocr` is unavailable, do not crash app startup;
* expose a clean processing function/class for OCR over frame files;
* support cancellation;
* support progress callback;
* return structured OCR results.

Pseudo-behavior:

```python
try:
    import easyocr
except ImportError:
    easyocr = None
```

If EasyOCR is not installed and OCR processing is requested, fail gracefully with a controlled error message.

### 2. EasyOCR languages

Support at least:

```text
ru
en
```

Default languages:

```json
["ru", "en"]
```

If the existing OCR settings already store selected languages, reuse that.

If language selection is not ready yet, use `["ru", "en"]` for this stage and document it.

Do not overbuild language management in this task.

### 3. OCR queue step

Add OCR as a real queue processing step after frame extraction.

Expected flow for video/URL items when OCR is enabled:

```text
download URL if needed
→ transcribe audio if enabled
→ extract frames if enabled or required by OCR
→ OCR over extracted frames
→ terminal status
```

For this stage, OCR requires frames.

Preferred behavior:

* If OCR is enabled, ensure frame extraction is enabled in the processing plan.
* If implementation cannot safely auto-enable frames, show/return a controlled validation error.
* Do not silently run OCR with no frames.

OCR should run on the final available frame set for this stage, which currently means existing extracted frames.

Future architecture may use `final_frames` / `frame_set`, but do not implement Smart Frame Extraction now.

### 4. UI behavior

Enable OCR checkbox only when it is actionable.

Current UI has disabled OCR placeholders. Update them so that:

* OCR can be enabled when selected backend is `easyocr` and EasyOCR is available;
* OCR remains disabled/unavailable when backend is not available;
* UI clearly shows if EasyOCR dependencies are missing;
* OCR checkbox should be available in default queue settings and per-item settings if consistent with current UI;
* if OCR is enabled, frame extraction should be enabled or required.

Do not add broad OCR settings UI beyond what is necessary.

Do not implement PaddleOCR/Windows OCR UI behavior beyond keeping their readiness/disabled state intact.

### 5. Processing plan

Extend `processing_plan.ocr`.

Example:

```json
{
  "ocr": {
    "enabled": true,
    "backend": "easyocr",
    "languages": ["ru", "en"],
    "status": "pending"
  }
}
```

Keep backward compatibility with existing OCR selector/readiness fields if present.

New queue items should snapshot current OCR settings.

Existing queue items should not unexpectedly mutate unless the user changes their per-item settings.

### 6. OCR outputs

For each processed item with OCR enabled, create OCR outputs near the existing frame output location.

Preferred files:

```text
frames_ocr.jsonl
frames_ocr.txt
```

If project conventions require another location, follow existing output structure and document it.

#### JSONL format

One JSON object per frame.

Suggested schema:

```json
{
  "frame_index": 1,
  "frame_path": "frame_000001.jpg",
  "timestamp_sec": 10.0,
  "engine": "easyocr",
  "languages": ["ru", "en"],
  "text": "recognized text joined for this frame",
  "blocks": [
    {
      "text": "recognized block",
      "confidence": 0.91,
      "bbox": [[10, 20], [200, 20], [200, 60], [10, 60]]
    }
  ],
  "duration_sec": 0.234
}
```

Use available frame metadata for `frame_index` and `timestamp_sec`.

If timestamp metadata is unavailable, use `null` and do not fail.

Paths should be relative where practical.

#### TXT format

Human-readable text grouped by frame.

Suggested format:

```text
[frame_000001.jpg | 00:00:10]
recognized text here

[frame_000002.jpg | 00:00:20]
recognized text here
```

Empty OCR frames may be skipped in TXT or included with a marker. Choose the simpler project-consistent behavior and document it.

### 7. OCR result stored in queue item

Store a compact OCR result in item metadata.

Suggested fields:

```json
{
  "ocr_result": {
    "backend": "easyocr",
    "languages": ["ru", "en"],
    "frames_processed": 25,
    "frames_with_text": 12,
    "ocr_time_sec": 8.52,
    "sec_per_frame": 0.341,
    "jsonl_path": ".../frames_ocr.jsonl",
    "txt_path": ".../frames_ocr.txt"
  }
}
```

Show enough information in UI/status/logs for manual verification.

### 8. Progress and cancellation

OCR must support queue cancellation.

Requirements:

* cancellation should be checked between frames;
* cancelled OCR should not corrupt output files;
* partial results may be kept if project convention allows partial outputs;
* item status should become cancelled if user cancels;
* cleanup behavior for URL downloads must remain unchanged.

Progress should show roughly:

```text
OCR: frame 3 / 25
```

All user-facing progress strings through i18n.

### 9. Benchmark logging

Add OCR benchmark logging:

```text
frames_processed
frames_with_text
ocr_time_sec
sec_per_frame
backend
languages
```

Log it and include it in OCR result metadata.

### 10. EasyOCR model download note

EasyOCR may download models on first use.

Do not implement custom model download UI in this task.

Document in README/PROJECT_STATE that:

* first EasyOCR run may require internet access;
* model files may be cached by EasyOCR/PyTorch;
* OCR is optional and installed through `requirements-ocr-easyocr.txt`.

## Error handling

Controlled failures required:

1. OCR enabled but EasyOCR is not installed.
2. OCR enabled but no frames are available.
3. Frame path missing.
4. EasyOCR raises an exception for one frame.
5. OCR is cancelled mid-run.

Decide whether a single bad frame fails the whole OCR step or is recorded as frame-level error. Prefer robust behavior:

* frame-level OCR error is recorded;
* processing continues unless error is fatal;
* fatal errors are logged and item fails gracefully.

## Tests

All tests must pass without EasyOCR installed.

Use mocks/fakes for EasyOCR.

Likely files:

```text
tests/test_ocr_manager.py
tests/test_queue_manager.py
tests/test_ui_contract.py
tests/test_i18n.py
tests/test_http_smoke.py
```

Add a new test file if useful:

```text
tests/test_ocr_processor.py
```

Required test coverage:

### Dependency/readiness

1. App starts when EasyOCR is not installed.
2. EasyOCR readiness unavailable when import is missing.
3. EasyOCR readiness available when mocked.

### Processor

4. EasyOCR processor converts frame results to JSONL records.
5. TXT output is created.
6. Empty frame OCR result handled.
7. Frame-level error handled.
8. Cancellation stops processing.
9. Benchmark fields computed.

### Queue

10. OCR step runs after frame extraction when enabled.
11. OCR disabled preserves old behavior.
12. OCR enabled requires frames or auto-enables frames.
13. OCR cancellation works.
14. OCR result metadata stored in queue item.
15. URL cleanup/cancel behavior remains stable.

### UI/i18n

16. OCR checkbox/action is enabled only when EasyOCR is selected and available.
17. OCR unavailable state is shown when EasyOCR is missing.
18. RU/EN i18n keys exist.
19. No hardcoded Cyrillic in `static/app.js` / `static/index.html`.
20. Existing OCR selector/readiness UI still works.

### Requirements

21. `requirements-ocr-easyocr.txt` exists.
22. `requirements-cpu.txt` unchanged.
23. `requirements-gpu.txt` unchanged.

## Documentation

Update:

```text
README.md
docs/DEVELOPERS.md
docs/PROJECT_STATE.md
docs/CODEX_TASKS.md
```

README should include:

* what EasyOCR OCR does;
* how to install optional OCR dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr-easyocr.txt
```

* first-run model download note;
* output files:

  * `frames_ocr.jsonl`;
  * `frames_ocr.txt`.

DEVELOPERS should include:

* optional dependency import pattern;
* OCR processor/output structure;
* queue OCR step;
* cancellation/progress behavior;
* test strategy with mocks.

PROJECT_STATE should include:

* implemented OCR status;
* known limitations;
* manual checks required;
* next possible OCR stages.

CODEX_TASKS should index this task.

Do not over-expand documentation.

Update `docs/DECISIONS.md` only if a real architecture decision is made.

## Validation commands

Run focused validation:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_manager
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager
.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_processor
git diff --check
git diff --stat
git status --short
```

If `tests.test_ocr_processor` does not exist before this task, create it or report the closest equivalent.

Do not run broad discovery if it risks hanging.

CRLF warnings are acceptable.

## Manual testing checklist for user

After implementation and after installing OCR dependencies manually:

### 1. Install optional OCR dependency

```powershell
cd C:\Python\LocalMediaTranscriber
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr-easyocr.txt
```

### 2. Start app

```powershell
.\run.bat
```

Expected:

* app starts normally;
* OCR settings show EasyOCR available;
* OCR checkbox/action can be enabled.

### 3. Recommended first test video

Use a short 1–3 minute screen recording with large text/numbers:

* trading terminal chart;
* MOEX/ICE/TradingView page;
* Excel/table;
* presentation slide;
* browser page with Russian/English text.

Recommended settings:

```text
URL max resolution: Up to 720p or Up to 1080p
Frame extraction: every 5–10 seconds
Max frame size: width up to 1280 px
OCR backend: EasyOCR
OCR languages: ru + en
```

Avoid first testing on:

* 4K video;
* tiny text;
* fast scrolling;
* low-contrast text;
* heavily compressed video.

### 4. Run OCR

Process video/URL with:

* frame extraction enabled;
* OCR enabled;
* EasyOCR selected.

Expected:

* item completes;
* OCR progress is visible;
* `frames_ocr.jsonl` exists;
* `frames_ocr.txt` exists;
* recognized text/numbers from frames are present.

### 5. Regression

Verify:

* local transcription still works;
* URL transcription still works;
* frame extraction still works;
* URL cleanup after cancel still works;
* OCR disabled path behaves as before.

## Expected result

After this task:

* EasyOCR is available as an optional OCR backend;
* app still works without EasyOCR installed;
* user can install EasyOCR via `requirements-ocr-easyocr.txt`;
* OCR can run over existing extracted frames;
* text and numbers can be recognized from video frames;
* OCR results are saved to JSONL and TXT;
* OCR progress/cancel/benchmark exists;
* no dependencies installed automatically;
* no commit created.
