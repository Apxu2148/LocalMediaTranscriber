from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

from . import config
from .frame_extractor import relative_project_path


logger = logging.getLogger(__name__)

DEFAULT_EASYOCR_LANGUAGES = ["ru", "en"]

try:
    import easyocr
    EASYOCR_IMPORT_ERROR: Exception | None = None
except Exception as exc:
    easyocr = None
    EASYOCR_IMPORT_ERROR = exc


class OcrProcessorError(RuntimeError):
    pass


def normalize_easyocr_languages(value: object) -> list[str]:
    if not isinstance(value, list):
        return list(DEFAULT_EASYOCR_LANGUAGES)
    languages: list[str] = []
    for item in value:
        language = str(item).strip()
        if language and language.isascii() and language.replace("_", "").isalnum() and language not in languages:
            languages.append(language)
    return languages or list(DEFAULT_EASYOCR_LANGUAGES)


def resolve_project_path(path_value: str | Path | None, *, base_dir: Path | None = None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    normalized = str(path_value).replace("\\", "/")
    if normalized.startswith("data/"):
        return config.BASE_DIR / path
    if base_dir is not None:
        return base_dir / path
    return path


def timestamp_label(seconds: float | int | None) -> str | None:
    if seconds is None:
        return None
    total_seconds = max(0, int(float(seconds)))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, whole_seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}"


class EasyOcrFrameProcessor:
    def __init__(
        self,
        *,
        reader_factory: Callable[[list[str]], object] | None = None,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.reader_factory = reader_factory
        self.clock = clock

    def process_frames(
        self,
        *,
        frames_index_path: str | Path | None = None,
        frames_path: str | Path | None = None,
        languages: list[str] | None = None,
        cancel_event: threading.Event | None = None,
        progress_callback: Callable[[dict], None] | None = None,
    ) -> dict:
        selected_languages = normalize_easyocr_languages(languages)
        frames_dir, index_payload = self._load_frame_index(frames_index_path, frames_path)
        frames = index_payload.get("frames") if isinstance(index_payload.get("frames"), list) else []
        if not frames:
            raise OcrProcessorError("OCR requires extracted frames, but no frames were found.")

        reader = self._create_reader(selected_languages)
        jsonl_path = frames_dir / "frames_ocr.jsonl"
        txt_path = frames_dir / "frames_ocr.txt"

        started = self.clock()
        records: list[dict] = []
        frames_with_text = 0
        status = "completed"
        total_frames = len(frames)

        for position, frame in enumerate(frames, start=1):
            if cancel_event is not None and cancel_event.is_set():
                status = "cancelled"
                break
            record = self._process_frame(
                reader,
                frames_dir,
                frame,
                position=position,
                languages=selected_languages,
            )
            records.append(record)
            if record.get("text"):
                frames_with_text += 1
            if progress_callback is not None:
                progress_callback(
                    {
                        "status": "running",
                        "backend": "easyocr",
                        "languages": selected_languages,
                        "frames_processed": len(records),
                        "frames_total": total_frames,
                        "frames_with_text": frames_with_text,
                        "current_frame": record.get("frame_path"),
                    }
                )

        jsonl_path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        self._write_txt(txt_path, records)

        elapsed = round(max(0.0, self.clock() - started), 3)
        processed = len(records)
        result = {
            "status": status,
            "backend": "easyocr",
            "languages": selected_languages,
            "frames_processed": processed,
            "frames_total": total_frames,
            "frames_with_text": frames_with_text,
            "ocr_time_sec": elapsed,
            "sec_per_frame": round(elapsed / processed, 4) if processed else None,
            "jsonl_path": relative_project_path(jsonl_path),
            "txt_path": relative_project_path(txt_path),
            "frames_path": relative_project_path(frames_dir),
            "cancelled": status == "cancelled",
            "completed": status == "completed",
        }
        logger.info(
            "EasyOCR benchmark: frames_processed=%s frames_with_text=%s ocr_time_sec=%s sec_per_frame=%s backend=%s languages=%s",
            result["frames_processed"],
            result["frames_with_text"],
            result["ocr_time_sec"],
            result["sec_per_frame"],
            result["backend"],
            ",".join(selected_languages),
        )
        return result

    def _load_frame_index(
        self,
        frames_index_path: str | Path | None,
        frames_path: str | Path | None,
    ) -> tuple[Path, dict]:
        index_path = resolve_project_path(frames_index_path)
        frames_dir = resolve_project_path(frames_path)
        if index_path is None and frames_dir is not None:
            index_path = frames_dir / "frames_index.json"
        if index_path is None:
            raise OcrProcessorError("OCR requires frames_index.json, but no frame index path was provided.")
        if frames_dir is None:
            frames_dir = index_path.parent
        if not index_path.is_file():
            raise OcrProcessorError(f"OCR frame index was not found: {index_path}")
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise OcrProcessorError(f"Could not read OCR frame index: {exc}") from exc
        if not isinstance(payload, dict):
            raise OcrProcessorError("OCR frame index has an invalid format.")
        return frames_dir, payload

    def _create_reader(self, languages: list[str]):
        if self.reader_factory is not None:
            return self.reader_factory(languages)
        if easyocr is None:
            message = "EasyOCR is not installed. Install optional OCR dependencies with requirements-ocr-easyocr.txt."
            if EASYOCR_IMPORT_ERROR is not None:
                message = f"{message} Import error: {EASYOCR_IMPORT_ERROR}"
            raise OcrProcessorError(message)
        return easyocr.Reader(languages)

    def _process_frame(
        self,
        reader,
        frames_dir: Path,
        frame: dict,
        *,
        position: int,
        languages: list[str],
    ) -> dict:
        frame_file = str(frame.get("file") or "").strip()
        frame_index = int(frame.get("index") or position)
        timestamp_sec = self._optional_float(frame.get("t"))
        frame_path = frames_dir / frame_file if frame_file else frames_dir / f"frame_{frame_index:06d}.jpg"
        started = self.clock()
        record = {
            "frame_index": frame_index,
            "frame_path": frame_file or frame_path.name,
            "timestamp_sec": timestamp_sec,
            "engine": "easyocr",
            "languages": list(languages),
            "text": "",
            "blocks": [],
            "duration_sec": 0.0,
        }
        if not frame_path.is_file():
            record["duration_sec"] = round(max(0.0, self.clock() - started), 3)
            record["error"] = f"Frame path is missing: {frame_file or frame_path.name}"
            return record
        try:
            raw_blocks = reader.readtext(str(frame_path), detail=1)
            blocks = self._normalize_blocks(raw_blocks)
            record["blocks"] = blocks
            record["text"] = "\n".join(block["text"] for block in blocks if block.get("text"))
        except Exception as exc:
            record["error"] = str(exc)
        record["duration_sec"] = round(max(0.0, self.clock() - started), 3)
        return record

    @staticmethod
    def _normalize_blocks(raw_blocks: Iterable[object] | None) -> list[dict]:
        blocks: list[dict] = []
        for raw in raw_blocks or []:
            bbox = None
            text = ""
            confidence = None
            if isinstance(raw, (list, tuple)):
                if len(raw) >= 1:
                    bbox = raw[0]
                if len(raw) >= 2:
                    text = str(raw[1] or "").strip()
                if len(raw) >= 3:
                    try:
                        confidence = round(float(raw[2]), 4)
                    except (TypeError, ValueError):
                        confidence = None
            elif isinstance(raw, dict):
                bbox = raw.get("bbox")
                text = str(raw.get("text") or "").strip()
                try:
                    confidence = round(float(raw.get("confidence")), 4)
                except (TypeError, ValueError):
                    confidence = None
            blocks.append(
                {
                    "text": text,
                    "confidence": confidence,
                    "bbox": EasyOcrFrameProcessor._json_safe_bbox(bbox),
                }
            )
        return blocks

    @staticmethod
    def _json_safe_bbox(value: object) -> list | None:
        if value is None:
            return None
        if hasattr(value, "tolist"):
            try:
                value = value.tolist()
            except Exception:
                return None
        try:
            return json.loads(json.dumps(value, default=lambda item: item.item() if hasattr(item, "item") else str(item)))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _write_txt(path: Path, records: list[dict]) -> None:
        lines: list[str] = []
        for record in records:
            text = str(record.get("text") or "").strip()
            error = record.get("error")
            if not text and not error:
                continue
            timestamp = timestamp_label(record.get("timestamp_sec"))
            header_parts = [str(record.get("frame_path") or f"frame_{record.get('frame_index') or 0:06d}.jpg")]
            if timestamp:
                header_parts.append(timestamp)
            lines.append(f"[{' | '.join(header_parts)}]")
            lines.append(text if text else f"OCR error: {error}")
            lines.append("")
        path.write_text("\n".join(lines).rstrip() + ("\n" if lines else ""), encoding="utf-8")

    @staticmethod
    def _optional_float(value: object) -> float | None:
        try:
            return round(float(value), 3) if value is not None else None
        except (TypeError, ValueError):
            return None


def process_easyocr_frames(
    *,
    frames_index_path: str | Path | None = None,
    frames_path: str | Path | None = None,
    languages: list[str] | None = None,
    cancel_event: threading.Event | None = None,
    progress_callback: Callable[[dict], None] | None = None,
) -> dict:
    return EasyOcrFrameProcessor().process_frames(
        frames_index_path=frames_index_path,
        frames_path=frames_path,
        languages=languages,
        cancel_event=cancel_event,
        progress_callback=progress_callback,
    )
