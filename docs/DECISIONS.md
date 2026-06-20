# Architectural decisions

## OCR backend catalog and plan compatibility

Stage 1.1b exposes OCR readiness as a catalog keyed by stable backend IDs: `tesseract`, `easyocr`, `paddleocr`, and `windows_ocr`. Optional Python/system backends are detected by import only; model/reader initialization belongs to the future execution stage.

Processing plans use `ocr.backend` as the selected backend and retain `ocr.engine` with the same value for compatibility with Stage 1.1a jobs and UI code. Selection does not enable processing: queue normalization continues to force `ocr.enabled=false` until Stage 1.1c supplies the complete execution contract.
