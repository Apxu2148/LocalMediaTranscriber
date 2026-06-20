# Codex task: Stage 1.1b — OCR backend selector + EasyOCR/PaddleOCR/Windows OCR readiness detection

## Project

Work only in:

`C:\Python\LocalMediaTranscriber`

Do **not** modify:

`C:\Python\LocalAudioTranscriber`

Do not work in any other project folder.

Do not commit. The user will test and commit manually.

Do not add new BAT files.

Do not install dependencies automatically.

Do not add heavy dependencies to the main requirements files in this stage.

All user-facing strings must support both RU and EN and must go through:

* `static/i18n.js`

Do not hardcode Russian user-facing strings in:

* `static/app.js`
* `static/index.html`

Update documentation:

* `README.md`
* `docs/DEVELOPERS.md`

Update tests.

## Current context

The project already supports:

* local audio/video transcription;
* URL audio/video transcription;
* local/URL frame extraction;
* queue processing;
* per-item `processing_plan`;
* runtime estimate/test-run for transcription and frame extraction;
* URL download progress and cancellation;
* cancellation for transcription and frame extraction;
* Tesseract OCR detection/settings from Stage 1.1a;
* OCR/CV processing is still disabled/coming soon.

Stage 1.1a added:

* `app/ocr_manager.py`;
* OCR APIs in `app/main.py`;
* localized OCR status/settings UI;
* Tesseract path detection;
* Tesseract version/language checks;
* OCR still does not process frames.

Now we need to expand from “Tesseract-only OCR settings” to a more general OCR backend selector/catalog.

## Goal

Add an OCR backend selector and readiness detection for multiple OCR engines:

1. Tesseract OCR — external executable backend, already partially implemented.
2. EasyOCR — optional integrated Python backend.
3. PaddleOCR — optional/experimental Python backend placeholder/readiness detection.
4. Windows OCR — optional/experimental Windows-only backend placeholder/readiness detection.

This stage must prepare OCR architecture for future OCR processing, but must not run OCR on frames yet.

## Strict non-goals

Do **not** implement actual OCR processing in this task.

Do **not**:

* run OCR on extracted frames;
* create `frames_ocr.jsonl`;
* create `frames_ocr.txt`;
* add OCR queue processing;
* add OCR cancellation;
* add OCR runtime estimate;
* add Smart Frame Extraction;
* add EasyOCR/PaddleOCR to main requirements files;
* auto-install EasyOCR/PaddleOCR/Tesseract;
* implement RemoteBackend;
* implement VLM OCR.

This is backend selection/readiness UI only.

## Desired OCR backend model

Introduce a clean conceptual model for OCR backends.

Suggested backend IDs:

```text
tesseract
easyocr
paddleocr
windows_ocr
```

Suggested user-facing names:

RU/EN can use the same names:

```text
Tesseract OCR
EasyOCR
PaddleOCR
Windows OCR
```

Suggested status values:

```text
available
not_installed
not_found
external_path_required
experimental
unsupported_platform
check_failed
coming_soon
```

Use project-consistent naming if different.

Example status object:

```json
{
  "selected_backend": "tesseract",
  "backends": {
    "tesseract": {
      "id": "tesseract",
      "name": "Tesseract OCR",
      "type": "external_executable",
      "available": false,
      "status": "not_found",
      "path": null,
      "version": null,
      "languages": [],
      "notes": ["external_path_required"]
    },
    "easyocr": {
      "id": "easyocr",
      "name": "EasyOCR",
      "type": "python_optional",
      "available": false,
      "status": "not_installed",
      "version": null,
      "languages": ["ru", "en"],
      "notes": ["optional_dependency_missing"]
    },
    "paddleocr": {
      "id": "paddleocr",
      "name": "PaddleOCR",
      "type": "python_optional_experimental",
      "available": false,
      "status": "not_installed",
      "version": null,
      "notes": ["experimental"]
    },
    "windows_ocr": {
      "id": "windows_ocr",
      "name": "Windows OCR",
      "type": "windows_system_experimental",
      "available": false,
      "status": "unsupported_platform",
      "version": null,
      "notes": ["windows_only", "experimental"]
    }
  }
}
```

Exact schema may differ, but it must be structured and testable.

## Backend requirements

### 1. Extend OCR manager

Update `app/ocr_manager.py` or equivalent.

Required capabilities:

* keep current Tesseract detection;
* add selected OCR backend setting;
* add backend status list;
* add EasyOCR detection;
* add PaddleOCR detection;
* add Windows OCR detection placeholder;
* return a combined OCR status payload.

### 2. Tesseract backend

Keep existing behavior:

* configured path;
* `shutil.which("tesseract")`;
* common Windows paths;
* version check;
* language check;
* rus/eng readiness.

Do not regress Tesseract status.

### 3. EasyOCR backend detection

Do not install EasyOCR.

Detect whether EasyOCR is importable:

```python
import easyocr
```

If import succeeds:

* mark backend as available;
* retrieve version if possible via `easyocr.__version__`;
* show that it is an integrated optional backend;
* show intended/default languages: `ru`, `en`.

If import fails:

* mark as not installed;
* show clear message that EasyOCR is an optional Python backend and is not installed yet.

Do not initialize `easyocr.Reader` in this stage unless absolutely safe and fast. Import check is enough. Creating a Reader may download models or allocate resources; avoid that in 1.1b.

Suggested note:

RU:

```text
EasyOCR не установлен. Этот встроенный OCR-движок будет доступен после установки дополнительных Python-зависимостей.
```

EN:

```text
EasyOCR is not installed. This integrated OCR backend will be available after installing optional Python dependencies.
```

### 4. PaddleOCR backend detection

Do not install PaddleOCR.

Detect whether PaddleOCR is importable:

```python
import paddleocr
```

or a safe equivalent.

If import succeeds:

* mark backend as available/experimental;
* retrieve version if possible;
* show as experimental.

If import fails:

* mark not installed/experimental.

Do not initialize OCR models.

Do not add PaddleOCR dependencies.

### 5. Windows OCR backend detection

Do not implement actual Windows OCR processing.

This stage should show Windows OCR as an experimental backend.

Detection should be lightweight:

* if platform is not Windows: `unsupported_platform`;
* if Windows: optionally try to detect `winrt` / relevant package availability if already installed;
* otherwise mark as not installed / experimental.

Do not add WinRT dependencies.

Do not require MSIX/package identity.

Suggested note:

RU:

```text
Windows OCR — экспериментальный системный OCR для Windows. Обработка кадров будет добавлена позже.
```

EN:

```text
Windows OCR is an experimental Windows system OCR backend. Frame processing will be added later.
```

### 6. Settings persistence

Persist selected OCR backend using existing settings infrastructure.

Suggested setting:

```json
{
  "ocr": {
    "selected_backend": "tesseract",
    "tesseract_path": "...",
    "default_languages": ["rus", "eng"]
  }
}
```

For EasyOCR, default languages may map to:

```json
["ru", "en"]
```

Do not overcomplicate language normalization in this stage; document that Tesseract and EasyOCR use different language identifiers.

### 7. API endpoints

Extend current OCR APIs.

Existing likely endpoints from 1.1a:

```text
GET  /api/ocr/status
POST /api/ocr/settings
POST /api/ocr/check
```

Required behavior:

* `GET /api/ocr/status` returns selected backend and all backend statuses.
* `POST /api/ocr/settings` can save selected backend and Tesseract path.
* `POST /api/ocr/check` rechecks all OCR backends or selected backend.

If endpoint names differ, keep project conventions.

### 8. Processing plan integration

The default processing settings and per-item `processing_plan` currently show OCR as coming soon.

Update OCR plan to include selected backend, but still do not process OCR.

Example:

```json
{
  "ocr": {
    "enabled": false,
    "backend": "easyocr",
    "languages": ["ru", "en"],
    "status": "coming_soon",
    "engine_available": false
  }
}
```

If OCR toggle remains disabled, that is fine.

Important:

* Changing OCR backend must not make OCR processing run.
* Queue must continue to treat OCR as no-op/coming soon.

## Frontend/UI requirements

### 1. OCR backend selector

In the OCR settings/status block, add a selector:

RU:

```text
OCR-движок
```

EN:

```text
OCR engine
```

Options:

```text
Tesseract OCR
EasyOCR
PaddleOCR
Windows OCR
```

Each option should show a clear status nearby.

### 2. OCR backend status cards

Show compact status for each backend, or at least selected backend plus a details area.

Recommended compact layout:

```text
OCR engine: [EasyOCR ▼]
Status: Not installed
Type: Integrated optional backend
Notes: Optional Python dependencies are not installed.
```

For Tesseract, keep path input/check.

For EasyOCR/PaddleOCR, do not show `tesseract.exe` path input.

### 3. Conditional fields

If selected backend is `tesseract`:

* show Tesseract path input;
* show Tesseract version/languages;
* show `rus`/`eng` readiness.

If selected backend is `easyocr`:

* show import status;
* show version if available;
* show intended language pair `ru+en`;
* show optional dependency note;
* no path to executable.

If selected backend is `paddleocr`:

* show experimental/not installed/available status;
* no path to executable.

If selected backend is `windows_ocr`:

* show Windows-only/experimental status;
* no path to executable.

### 4. Clear user guidance

Add guidance text that OCR processing is still coming in the next stage.

RU:

```text
На этом этапе программа только проверяет OCR-движки. Распознавание текста на кадрах будет добавлено на следующем этапе.
```

EN:

```text
At this stage the app only checks OCR engines. Text recognition on frames will be added in the next stage.
```

### 5. Do not make the page too long

The UI is already becoming long.

Keep this section compact:

* use collapsible details if the project already has such patterns;
* avoid adding a large table if simple cards/selectors are enough;
* avoid duplicating too much text in item cards.

### 6. No hardcoded Cyrillic

All UI strings through `static/i18n.js`.

## i18n labels

Add RU/EN keys for:

* OCR engine;
* Tesseract OCR;
* EasyOCR;
* PaddleOCR;
* Windows OCR;
* integrated backend;
* external executable;
* optional backend;
* experimental backend;
* not installed;
* unsupported platform;
* optional dependencies missing;
* backend available;
* backend not available;
* selected backend;
* OCR engines checked;
* OCR engine settings saved;
* OCR processing will be added in the next stage.

Use existing i18n naming style.

## Tests

Add/update tests.

Likely files:

* `tests/test_ocr_manager.py`
* `tests/test_i18n.py`
* `tests/test_ui_contract.py`
* `tests/test_http_smoke.py`
* `tests/test_queue_manager.py`
* `tests/test_storage_manager.py`

### Required test coverage

#### OCR manager tests

Use mocks. Do not require Tesseract/EasyOCR/PaddleOCR/Windows OCR installed.

Test:

1. Tesseract detection still works as before.
2. EasyOCR available when import succeeds.
3. EasyOCR not installed when import fails.
4. EasyOCR detection does not initialize model reader.
5. PaddleOCR available when import succeeds.
6. PaddleOCR not installed when import fails.
7. Windows OCR unsupported on non-Windows.
8. Windows OCR marked experimental on Windows.
9. Combined status returns all backends.
10. Selected backend is persisted.
11. Invalid selected backend is rejected or falls back safely.
12. OCR processing remains disabled/no-op.

#### API tests

Test:

1. `GET /api/ocr/status` returns all backend statuses.
2. `POST /api/ocr/settings` saves selected backend.
3. `POST /api/ocr/settings` can still save Tesseract path.
4. `POST /api/ocr/check` returns combined status.
5. Invalid backend returns clear error or safe fallback.

#### i18n tests

Verify all new RU/EN keys exist.

#### UI contract tests

Verify:

* no hardcoded Cyrillic in `static/app.js` / `static/index.html`;
* OCR backend selector exists;
* all backend options appear;
* Tesseract path field is still present;
* OCR is still coming soon / no processing output UI introduced.

#### Queue safety tests

Verify:

* OCR selected backend does not trigger processing;
* queue transcription still works;
* frame extraction still works;
* runtime estimate still ignores OCR for now;
* URL download cancellation remains unaffected.

## Documentation

Update `README.md`:

* explain OCR backend selector;
* explain that current stage only checks OCR engines;
* describe each backend briefly:

  * Tesseract: external executable;
  * EasyOCR: optional integrated Python backend;
  * PaddleOCR: optional experimental backend;
  * Windows OCR: experimental Windows-only backend;
* explain actual frame OCR will come later.

Update `docs/DEVELOPERS.md`:

* document OCR backend status schema;
* document detection strategy for each backend;
* document settings schema;
* document that OCR processing is intentionally still disabled;
* document future Stage 1.1c: OCR over extracted frames.

## Validation commands

Run:

```powershell
cd C:\Python\LocalMediaTranscriber

.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest tests.test_i18n tests.test_ui_contract
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_manager
.\.venv\Scripts\python.exe -m unittest tests.test_queue_manager tests.test_frame_extractor
.\.venv\Scripts\python.exe -m unittest tests.test_runtime_estimate tests.test_url_downloader
.\.venv\Scripts\python.exe -m unittest tests.test_http_smoke
.\.venv\Scripts\python.exe -m unittest tests.test_storage_manager tests.test_model_manager
```

Then:

```powershell
Select-String -Path static\app.js,static\index.html -Pattern "[А-Яа-яЁё]"
git diff --check
git diff --stat
git status --short
```

CRLF warnings are acceptable.

Do not run broad discovery if it risks hanging.

## Manual testing checklist

### 1. Start app

```powershell
cd C:\Python\LocalMediaTranscriber
.\run.bat
```

Expected:

* app starts normally;
* OCR settings block appears.

### 2. Tesseract option

Select Tesseract OCR.

Expected:

* Tesseract path field appears;
* if Tesseract is missing, status says not found;
* app does not crash.

### 3. EasyOCR option

Select EasyOCR.

Expected if EasyOCR is not installed:

* status says not installed / optional dependency missing;
* no path-to-exe field;
* OCR processing still coming soon.

If EasyOCR happens to be installed:

* status says available;
* version shown if available.

### 4. PaddleOCR option

Select PaddleOCR.

Expected:

* status says not installed or available/experimental;
* clearly marked experimental;
* no processing runs.

### 5. Windows OCR option

Select Windows OCR.

Expected:

* on Windows, status says experimental/available-not-implemented or similar;
* no processing runs;
* no crash.

### 6. Settings persistence

1. Select EasyOCR.
2. Save settings.
3. Refresh page.
4. Expected: selected backend remains EasyOCR.

Repeat for Tesseract if needed.

### 7. Regression

Verify quickly:

* local short transcription still works;
* local frame extraction still works;
* runtime estimate still works;
* URL download progress/cancel still works;
* OCR still does not attempt to process frames.

## Expected result

After this task:

* OCR settings are backend-based, not Tesseract-only;
* Tesseract remains supported as an external engine;
* EasyOCR is visible as an optional integrated backend;
* PaddleOCR is visible as optional/experimental;
* Windows OCR is visible as Windows-only/experimental;
* selected OCR backend is persisted;
* no actual OCR processing is implemented yet;
* the project is ready for the next stage: choosing and implementing the first real OCR processing backend.