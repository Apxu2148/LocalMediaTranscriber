# Architectural decisions

## OCR backend catalog and plan compatibility

Stage 1.1b exposes OCR readiness as a catalog keyed by stable backend IDs: `tesseract`, `easyocr`, `paddleocr`, and `windows_ocr`. Optional Python/system backends are detected by import only; model/reader initialization belongs to the future execution stage.

Processing plans use `ocr.backend` as the selected backend and retain `ocr.engine` with the same value for compatibility with Stage 1.1a jobs and UI code. Selection does not enable processing: queue normalization continues to force `ocr.enabled=false` until Stage 1.1c supplies the complete execution contract.

## URL format profiles are per-item snapshots

URL downloads use stable profile IDs plus an optional advanced yt-dlp format string instead of enumerating site-specific format IDs. The frontend snapshots the selected settings into `processing_plan.url_download` when an item is added, and pending-item edits preserve that snapshot. Direct media URLs bypass yt-dlp format selection. This keeps jobs reproducible without a slow pre-download format-list request.
