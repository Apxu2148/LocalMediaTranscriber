# Codex UI polish task: Collapsible settings sections

Work only in C:\Python\LocalMediaTranscriber.
Do not modify C:\Python\LocalAudioTranscriber.
Do not commit.
Do not install dependencies.
Do not modify requirements files.

Important scope limit:
This is a small UI polish task. Do not redesign the UI. Do not move settings between sections. Do not change backend logic. Do not change processing_plan structure. Do not add persistence. Do not change queue behavior. If this requires a broad refactor, stop and report.

Goal:
Reduce UI clutter before adding OCR processing by making existing settings sections collapsible.

Required changes:
1. Make “Default queue settings” / “Настройки по умолчанию для очереди” collapsible by clicking the section header.
2. Keep it expanded by default.
3. Add a clear expand/collapse indicator: ▾ / ▸ or equivalent.
4. Make per-item processing controls collapsible inside each queue item.
5. Suggested label:
   RU: “Параметры обработки элемента”
   EN: “Item processing settings”
6. Keep per-item summary visible even when controls are collapsed.
7. Keep per-item controls expanded by default.
8. Do not change any actual settings behavior.
9. Do not change OCR behavior.
10. All strings via static/i18n.js.
11. No hardcoded Russian in static/app.js or static/index.html.

Files likely involved:
- static/index.html
- static/app.js
- static/i18n.js
- static/style.css
- tests/test_ui_contract.py
- tests/test_i18n.py

Validation:
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m unittest tests.test_ui_contract tests.test_i18n tests.test_http_smoke
git diff --check
git diff --stat
git status --short

Expected result:
- default queue settings section can be collapsed/expanded;
- each queue item’s processing controls can be collapsed/expanded;
- processing summary remains visible;
- no backend changes;
- no dependencies;
- no requirements changes;
- no commit.

Documentation / task history:

1. Save the full text of this task in:

docs/codex_tasks/2026-06-20_collapsible_settings_sections.md

2. Update docs/CODEX_TASKS.md with a short index entry for this task.

3. The file in docs/codex_tasks/ must contain the full task text, not only a summary.

4. Do not over-expand README/PROJECT_STATE for this small UI polish. Update PROJECT_STATE only if useful.
