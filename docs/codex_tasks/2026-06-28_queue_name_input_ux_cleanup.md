# Codex task: Queue name input UX cleanup

Work only in:

```text
C:\Python\LocalMediaTranscriber
```

Do not commit.

Do not add dependencies.

## Goal

Small UI/UX cleanup for queue controls.

## Part 1 - Remove redundant queue settings summary

Remove the UI phrase similar to:

```text
Очередь будет обработана с настройками: модель tiny, устройство auto.
```

and its English equivalent if present.

Do not replace it with another summary.

Reason: the UI already has:

```text
Настройки обработки по умолчанию
```

so the extra summary is redundant and incomplete.

## Part 2 - Allow editing queue folder name before processing starts

Current behavior:

* The field `Название папки очереди` becomes non-editable after adding the first item to the queue.

This is too strict.

Expected behavior:

* The user may edit `Название папки очереди` after adding items to the queue.
* The field should remain editable while the queue has not started processing and no queue output folder has been fixed/created.
* Adding items to the queue should not by itself lock the queue folder name.
* Once processing starts, or once the queue root/output folder is created/fixed, the field can become locked.
* Do not implement migration/renaming of already-created queue folders.
* Do not change queue output folder architecture.
* Do not change queue processing logic except the minimum needed to pass the selected queue folder name at processing/start time.

## UI behavior

Allowed:

```text
1. User adds item_001.
2. User edits queue folder name.
3. User adds item_002.
4. User starts processing.
5. The queue root uses the final entered name.
```

Not required:

```text
Changing folder name after processing has started.
Renaming already-created folders.
Migrating outputs.
```

## Tests

Update focused tests if existing tests assert that the queue folder input is disabled after adding items.

Add/update tests for:

1. Queue folder name input remains enabled when items exist but processing has not started.
2. Queue folder name becomes locked/disabled once processing starts or queue folder is fixed, if this behavior is currently represented in UI state.
3. Removing the redundant settings summary does not break UI contract/i18n tests.

## Validation

Run:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager
git diff --check
git diff --stat
git status --short
```

CRLF warnings are acceptable.

## Task history

If this change is more than a trivial one-file UI tweak, save full task text under:

```text
docs/codex_tasks/
```

Filename:

```text
YYYY-MM-DD_queue_name_input_ux_cleanup.md
```

Update:

```text
docs/CODEX_TASKS.md
```

Do not over-update project docs.

Do not commit.
