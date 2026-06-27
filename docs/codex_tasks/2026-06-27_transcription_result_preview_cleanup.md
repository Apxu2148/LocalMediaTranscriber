# Codex task: Make transcription result preview collapsible and queue-aware

Work only in:

```text
C:\Python\LocalMediaTranscriber
```

Do not commit. The user will test and commit manually.

Do not add dependencies.

Do not modify requirements files.

Do not add BAT files.

## Goal

Fix the UI block currently named roughly:

```text
Рез-т последней транскрибации
```

After the queue output folder structure change, this block may point to an outdated/legacy transcript path. Make it safer and less intrusive.

## Requirements

1. Make the transcription result block collapsible.
2. The block should be collapsed by default.
3. Keep it as a secondary preview block, not the main artifact navigation.
4. The main artifact navigation remains “Созданные файлы”.
5. By default, the block should show the latest available transcription result if current app state can provide it.
6. If a queue item has just produced a transcript under:

```text
data/queues/<queue>/item_xxx/transcript/
```

then the preview should prefer that latest queue transcript over old legacy `data/transcripts` paths.
7. Add a small input allowing the user to specify a transcript file path manually.
8. Add a button to load/show that transcript file path.
9. Validate that the path is a local file path and avoid path traversal/security issues.
10. If the file does not exist or cannot be read, show a clear localized error.
11. Do not implement a full file browser.
12. Do not change transcript generation format.
13. Do not change queue output structure.
14. Do not break old standalone transcription behavior.

## UI text

Use i18n. Do not hardcode Cyrillic in `static/app.js` or `static/index.html`.

Russian labels:

```text
Результат транскрибации
Путь к transcript-файлу
Показать файл
Последняя транскрибация
Не удалось прочитать transcript-файл
```

English labels:

```text
Transcription result
Transcript file path
Show file
Latest transcription
Failed to read transcript file
```

## Preferred behavior

The block can be implemented as an HTML `<details>` element.

Default state:

```html
<details>
```

not open by default.

If there is an existing details-state preservation pattern in `static/app.js`, use it. If not, keep this simple.

## Backend

If the frontend already receives transcript text/path in the latest job/queue response, use that.

If a new endpoint is needed, add a minimal safe endpoint, for example:

```text
GET /api/transcript/read?path=...
```

or equivalent existing API style.

The endpoint must:

* accept only local file paths;
* read UTF-8 text with safe fallback if existing project conventions use another encoding;
* reject directories;
* reject missing files;
* preferably restrict readable files to project output folders:

  * `data/queues/`
  * `data/transcripts/`
  * maybe `data/recordings/` only if transcript files can be there;
* return structured JSON with `ok`, `path`, `text` or `error`.

Do not allow arbitrary system file reads if avoidable.

## Tests

Add/update focused tests:

1. UI contract test: transcription result block is collapsible / has expected element.
2. i18n test: new RU/EN keys exist.
3. API/http smoke test if a new endpoint is added.
4. Backend path-read test if a new helper is added.
5. Regression: queue tests still pass if touched.

## Validation

Run:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager
git diff --check
git diff --stat
git status --short
```

CRLF warnings are acceptable.

## Task history

Save full task text under:

```text
docs/codex_tasks/
```

Use the actual current date:

```text
YYYY-MM-DD_transcription_result_preview_cleanup.md
```

Update:

```text
docs/CODEX_TASKS.md
```

Do not over-update project docs unless necessary.

## Non-goals

Do not implement CV.

Do not implement VLM.

Do not modify queue folder architecture.

Do not migrate old transcripts.

Do not create a file manager.

Do not commit.
