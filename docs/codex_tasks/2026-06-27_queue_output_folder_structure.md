# Codex task: Queue output folder structure with user-defined queue folder name

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

Do not install dependencies.

Do not modify requirement files:

```text
requirements-cpu.txt
requirements-gpu.txt
requirements-ocr-easyocr.txt
requirements-ocr-paddleocr.txt
requirements-ocr-tesseract.txt
requirements-ocr-windows.txt
```

if some of them do not exist, do not create them in this task.

## Start mode

Start in Plan Mode first.

This is an architectural output-layout task. It affects queue processing, artifact paths, UI output links, tests, and documentation.

Before implementation, inspect current output path logic and explain:

1. where transcripts are currently saved;
2. where recordings are currently saved;
3. where downloaded URL media is saved;
4. where extracted frames are currently saved;
5. where OCR artifacts are currently saved;
6. where mouse/keyboard/session artifacts are currently saved;
7. where “Созданные файлы” / created files are currently assembled in the UI/API;
8. what backward compatibility risks exist.

Then implement the focused structure below.

## Background

The project currently has working:

```text
recording
transcription
URL/local media queue
frame extraction
EasyOCR over frames
runtime estimate with OCR
mouse events
keyboard events
session JSON
```

But outputs are scattered across folders such as:

```text
data/recordings/
data/transcripts/
data/downloads/
```

and extracted frames/OCR artifacts are stored near recording-derived names, not inside a single per-queue folder.

Before adding CV, VLM, and more multimodal artifacts, outputs must be reorganized.

## Goal

Create a new queue-oriented output structure:

```text
data/
  queues/
    <queue_folder_name>/
      queue_manifest.json
      queue_log.txt              # optional if already easy
      item_001_<safe_source_name>/
        source/
        downloads/
        transcript/
        frames/
        ocr/
        cv/
        events/
        logs/
      item_002_<safe_source_name>/
        ...
```

The user should be able to enter a human-readable folder name for the current queue in the UI.

If the user does not enter a name, generate a safe default folder name based on current date/time.

## Required target structure

### Queue root

Create all queue output folders under:

```text
data/queues/
```

Each queue processing session should have one root folder:

```text
data/queues/<queue_folder_name>/
```

Examples:

```text
data/queues/2026-06-27_181500_queue/
data/queues/2026-06-27_181500_ocr_test_moex_brent/
data/queues/2026-06-27_181500_visiology_demo_test/
```

### Queue folder name

The UI should allow the user to enter a queue folder name.

Russian label:

```text
Название папки очереди
```

English label:

```text
Queue folder name
```

Help text, Russian:

```text
Если оставить пустым, имя будет создано автоматически по дате и времени.
```

Help text, English:

```text
If empty, a date/time-based folder name will be generated automatically.
```

Expected behavior:

* User enters text, for example:

```text
ocr_test_moex_brent
```

* Actual folder becomes:

```text
2026-06-27_181500_ocr_test_moex_brent
```

or equivalent timestamp-prefixed safe name.

If empty:

```text
2026-06-27_181500_queue
```

### Name sanitization

Sanitize user-provided names for Windows-safe paths.

Rules:

* trim leading/trailing spaces;
* lower-level exact casing is not critical;
* replace invalid path characters with `_`;
* collapse repeated `_`;
* limit length to a reasonable max, for example 80–120 chars;
* avoid reserved Windows names if helper already exists;
* never allow `..`, absolute paths, drive prefixes, or path separators to escape `data/queues`.

Examples:

```text
"My OCR test / MOEX: Brent?" -> "My_OCR_test_MOEX_Brent"
"  demo   queue  " -> "demo_queue"
```

If sanitization produces an empty string, fall back to:

```text
queue
```

### Queue manifest

Create:

```text
data/queues/<queue_folder_name>/queue_manifest.json
```

It should contain at least:

```json
{
  "queue_id": "...",
  "queue_folder_name": "...",
  "created_at": "...",
  "project": "LocalMediaTranscriber",
  "items": [
    {
      "index": 1,
      "source": "...",
      "source_type": "local_file | url | recording | unknown",
      "item_folder": "item_001_<safe_source_name>",
      "processing_plan": {},
      "outputs": {}
    }
  ]
}
```

The exact schema can follow existing queue metadata conventions, but it must be useful for reading the queue folder later.

The manifest should be updated when item outputs become available.

Do not overbuild a database layer.

### Item folders

Each queue item should get a folder:

```text
item_001_<safe_source_name>/
item_002_<safe_source_name>/
item_003_<safe_source_name>/
```

Examples:

```text
item_001_screen2_20260627_180942_3fps/
item_002_youtube_abc123/
item_003_local_video_demo/
```

If source name is unknown or URL is too long, use a safe short fallback:

```text
item_001_url_source
item_002_media_item
```

Keep numbering stable for the queue item order.

## Required item subfolders

Create these subfolders when needed, or create them upfront if easier:

```text
source/
downloads/
transcript/
frames/
ocr/
cv/
events/
logs/
```

Preferred behavior:

* create only relevant folders, but creating the full skeleton is acceptable if simpler;
* future `cv/` should exist or be reserved so Stage CV can write there later.

## Where artifacts should go

### Source metadata

For local source files:

```text
item_xxx/source/source_manifest.json
```

Should include:

```json
{
  "original_path": "...",
  "source_type": "local_file",
  "copied_to_queue": false
}
```

Do not copy large local source files into `source/` by default unless current architecture already copies them. Prefer metadata reference first to avoid duplicating large videos.

For recorded sessions already in `data/recordings`, keep original files in `data/recordings` for now if necessary, but item manifest should link to them.

### URL downloads

Downloaded URL media should go under:

```text
item_xxx/downloads/
```

If “keep downloaded URL video after processing” is disabled, retention cleanup should delete downloaded media from this item folder.

Important:

* do not delete local user files;
* cleanup errors should be logged and should not mask processing status;
* preserve existing retention behavior but adapt paths.

### Transcripts

Transcript outputs should go under:

```text
item_xxx/transcript/
```

Expected:

```text
transcript.txt
transcript.json
```

or equivalent current names if there is a strong reason to preserve model/date naming.

Preferred:

```text
transcript/
  transcript.txt
  transcript.json
```

If current code relies on unique timestamp/model filenames, keep compatibility by using stable short aliases or include original filename in manifest.

### Frames

Extracted frames should go under:

```text
item_xxx/frames/
```

Expected:

```text
frames/
  frame_000001__t000000.000.jpg
  frame_000002__t000003.000.jpg
  frames_index.json
```

### OCR

OCR outputs should go under:

```text
item_xxx/ocr/
```

Expected:

```text
ocr/
  frames_ocr.jsonl
  frames_ocr.txt
```

Important:

* update OCR writer paths;
* update queue outputs;
* update created files UI;
* do not change OCR JSONL schema except paths if necessary.

### Events

Mouse/keyboard/session artifacts related to this item/session should be linked or copied under:

```text
item_xxx/events/
```

Expected:

```text
events/
  mouse_events.jsonl
  keyboard_events.jsonl
  input_events.jsonl      # if exists
  session.json            # if exists or if appropriate
```

If current recording logic creates events in `data/recordings`, do not break recording. For this stage, acceptable options:

Option A, preferred if not too risky:

* when a recording item is processed through queue, copy or link relevant event files into `item_xxx/events/`;
* keep originals in `data/recordings` for backward compatibility.

Option B, acceptable MVP:

* store event file paths in `source_manifest.json` and `queue_manifest.json`;
* do not copy events yet;
* but “Созданные файлы” should clearly include event paths if they belong to the item.

Do not overbuild event synchronization in this task.

### Logs

If item-specific logs exist or are easy to add, put them under:

```text
item_xxx/logs/
```

Otherwise reserve the folder for later.

### CV

Do not implement CV in this task.

But reserve:

```text
item_xxx/cv/
```

Future CV stage will write:

```text
cv/
  frames_cv.jsonl
  frames_cv.txt
```

## Created files UI/API

Update all places where created output files are shown.

The UI should display paths from the new queue folder structure.

Russian:

```text
Созданные файлы
```

must show item outputs such as:

```text
Очередь:
C:\Python\LocalMediaTranscriber\data\queues\2026-06-27_181500_ocr_test\

Транскрипт TXT:
...\item_001_screen2\transcript\transcript.txt

Кадры:
...\item_001_screen2\frames\

OCR JSONL:
...\item_001_screen2\ocr\frames_ocr.jsonl

OCR TXT:
...\item_001_screen2\ocr\frames_ocr.txt
```

English equivalent should also work through i18n.

Do not leave UI pointing only to old `data/transcripts` or old `data/recordings/...__frames` paths for newly processed queue items.

## Backward compatibility

Existing files in old folders should not be deleted or migrated automatically.

Existing old outputs should remain readable if UI currently lists history.

Do not break:

```text
data/recordings/
data/transcripts/
```

for recording and old artifacts unless the code naturally no longer uses them for queue processing.

Recording itself may still initially write raw recordings into `data/recordings/`. That is acceptable for this stage.

Queue processing outputs for new items should use `data/queues/...`.

If there is existing history logic that reads from old folders, do not remove it unless explicitly necessary. Prefer additive behavior.

## Queue folder lifecycle

The queue folder should be created at a clear point.

Preferred:

* create or reserve queue folder when first queue item is added or when queue processing starts;
* the queue folder name should be visible in the UI before processing if possible.

Acceptable MVP:

* queue folder is created when processing starts or when estimate/processing first needs output paths;
* UI should still show which folder will be used.

Avoid creating a new queue root per item. One queue root must contain all item folders for that queue/session.

If the user changes queue folder name after items are already processed, do not attempt complex migration.

Reasonable behavior:

* allow editing while queue has no completed/processing outputs;
* once processing starts, lock the folder name or show that it applies only to the next queue.

Implement the simpler safe option.

## Queue state and reset behavior

Clarify current queue lifecycle and implement predictable behavior:

* Current queue has one queue folder name.
* Clearing/resetting the queue should allow a new queue folder name for the next run.
* Adding more items to the same queue before processing should put them into the same queue folder.
* Multiple items processed in one queue should share the same queue root.

If there is already a queue id/session id, use it.

## API considerations

If existing API has queue add/update/start endpoints, extend them minimally.

Possible data field:

```json
{
  "queue_folder_name": "ocr_test_moex_brent"
}
```

or settings endpoint for queue defaults.

Do not make breaking API changes if avoidable.

## UI requirements

Add a queue folder name input near the global/default queue settings.

Suggested location:

```text
Настройки по умолчанию для очереди
```

or near the queue controls.

Russian:

```text
Название папки очереди
```

English:

```text
Queue folder name
```

Help text:

Russian:

```text
Если оставить пустым, имя будет создано автоматически по дате и времени.
```

English:

```text
If empty, a date/time-based folder name will be generated automatically.
```

Show resolved/current queue folder path if possible:

Russian:

```text
Папка очереди:
...
```

English:

```text
Queue folder:
...
```

Do not hardcode Cyrillic in `static/app.js` or `static/index.html`.

Use `static/i18n.js`.

## Non-goals

Do not implement CV.

Do not implement VLM.

Do not implement new OCR engines.

Do not change OCR schema except output paths.

Do not change transcript content format.

Do not migrate old historical outputs.

Do not delete old output folders.

Do not change recording raw-file behavior unless required.

Do not introduce a database.

Do not add dependencies.

Do not commit.

## Task history requirement

Save the full text of this task in a new markdown file under:

```text
docs/codex_tasks/
```

Use the actual current date at the time of implementation, not an example date from this prompt.

Filename format:

```text
YYYY-MM-DD_queue_output_folder_structure.md
```

Example:

If today is `2026-06-27`, use:

```text
docs/codex_tasks/2026-06-27_queue_output_folder_structure.md
```

Also update:

```text
docs/CODEX_TASKS.md
```

The file in `docs/codex_tasks/` must contain the full task text, not only a summary.

## Documentation

Update:

```text
docs/PROJECT_STATE.md
docs/HANDOFF.md
docs/CODEX_TASKS.md
```

Update `docs/DECISIONS.md` only if a real architecture decision is made. This task probably qualifies as an output-layout architecture decision, so add a concise decision entry if appropriate.

README update is optional; do it only if there is a user-facing section about outputs.

## Tests

Add or update tests using temporary directories. Do not require real EasyOCR, real Whisper, or real media downloads.

### Required test intent — queue folder naming

1. Empty queue folder name generates timestamp-based safe default.
2. User-provided queue folder name is sanitized.
3. Invalid path characters are replaced.
4. Path traversal attempts cannot escape `data/queues`.
5. Multiple items in one queue share the same queue root.
6. Item folders are numbered as `item_001...`, `item_002...`.

### Required test intent — output paths

7. Transcript output path points to `item_xxx/transcript/`.
8. Frames output path points to `item_xxx/frames/`.
9. OCR output path points to `item_xxx/ocr/`.
10. URL downloads, when retained, are under `item_xxx/downloads/`.
11. URL downloads, when not retained, are cleaned from the item downloads folder without deleting local files.
12. Queue manifest is created.
13. Queue manifest contains item records and output paths.

### Required test intent — UI/API

14. UI contains queue folder name input.
15. UI has i18n keys for queue folder name/help/path.
16. No hardcoded Cyrillic is added to `static/app.js` or `static/index.html`.
17. Created files UI uses new output paths for new queue processing.
18. Existing queue item controls still work.

### Required test intent — regression

19. Existing queue tests pass.
20. Existing runtime estimate tests pass.
21. Existing OCR processor tests pass.
22. Existing frame extractor tests pass.
23. Existing UI/i18n/http smoke tests pass.

## Validation commands

Run:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
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

## Manual test checklist for user

### Test A — one queue with one item

1. Start app:

```powershell
.\run.bat
```

2. Enter queue folder name:

```text
queue_structure_test
```

3. Add one short local video.
4. Enable:

   * audio if available;
   * frame extraction;
   * OCR EasyOCR.
5. Run processing.
6. Confirm output folder exists:

```text
data/queues/<timestamp>_queue_structure_test/
```

7. Confirm item folder exists:

```text
item_001_<safe_source_name>/
```

8. Confirm outputs are inside:

```text
transcript/
frames/
ocr/
```

9. Confirm “Созданные файлы” shows new queue paths.

### Test B — one queue with multiple items

1. Clear/reset queue if needed.
2. Enter queue folder name:

```text
multi_item_test
```

3. Add two media items.
4. Process both.
5. Confirm both items are under the same queue root:

```text
data/queues/<timestamp>_multi_item_test/
  item_001_...
  item_002_...
```

### Test C — no user folder name

1. Clear/reset queue.
2. Leave queue folder name empty.
3. Add and process one item.
4. Confirm default folder name is generated:

```text
data/queues/YYYY-MM-DD_HHMMSS_queue/
```

### Test D — unsafe folder name

1. Enter unsafe name:

```text
..\bad/name:test?*
```

2. Add/process item or inspect resolved folder name.
3. Confirm output remains inside:

```text
data/queues/
```

and sanitized name does not escape the project.

### Test E — URL download retention

If convenient:

1. Add URL item.
2. Disable keep downloaded media.
3. Process.
4. Confirm downloaded media does not remain in `downloads/`.
5. Confirm local source files are never deleted.

## Expected result

After this task:

* New queue processing writes outputs under `data/queues/<queue_folder>/item_xxx/`.
* User can enter a name for the current queue folder.
* Empty name creates a date/time-based queue folder.
* Each queue item has its own subfolder.
* Transcripts, frames, OCR, downloads, events/log metadata paths are organized under the item folder.
* Created files UI shows the new paths.
* Old outputs are not deleted or migrated.
* Existing tests still pass.
* No commit is created.
