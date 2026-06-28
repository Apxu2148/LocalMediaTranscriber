import json
import re
from pathlib import Path
from typing import Callable


try:
    from PIL import Image, ImageStat, UnidentifiedImageError
except ImportError:  # pragma: no cover - exercised by module-state tests when needed
    Image = None
    ImageStat = None

    class UnidentifiedImageError(Exception):
        pass


SUPPORTED_FRAME_EXTENSIONS = {".jpg", ".jpeg"}
NEAR_DUPLICATE_DIFF_THRESHOLD = 0.03
SCENE_CHANGE_DIFF_THRESHOLD = 0.25


def pillow_available() -> bool:
    return Image is not None and ImageStat is not None


def _frame_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"frame_(\d+)", path.stem)
    if match:
        return int(match.group(1)), path.name
    return 10**12, path.name


def _frame_index(path: Path, fallback: int) -> int:
    match = re.search(r"frame_(\d+)", path.stem)
    return int(match.group(1)) if match else fallback


def _timestamp_sec(path: Path) -> float | None:
    match = re.search(r"__t(\d+)\.(\d+)", path.stem)
    if not match:
        return None
    seconds, milliseconds = match.groups()
    return round(int(seconds) + int(milliseconds[:3].ljust(3, "0")) / 1000.0, 3)


def _resampling_filter():
    return getattr(getattr(Image, "Resampling", Image), "LANCZOS")


def _image_values(image) -> list[int]:
    getter = getattr(image, "get_flattened_data", None)
    return list(getter() if getter is not None else image.getdata())


def _average_hash(gray_image) -> str:
    tiny = gray_image.resize((8, 8), _resampling_filter())
    values = _image_values(tiny)
    average = sum(values) / len(values)
    bits = "".join("1" if value >= average else "0" for value in values)
    return f"{int(bits, 2):016x}"


def _diff_vector(gray_image) -> list[int]:
    return _image_values(gray_image.resize((16, 16), _resampling_filter()))


def _diff_score(current: list[int], previous: list[int] | None) -> float | None:
    if previous is None:
        return None
    total = sum(abs(left - right) for left, right in zip(current, previous))
    return round(total / (len(current) * 255.0), 4)


def _blur_score(gray_image) -> float:
    width, height = gray_image.size
    if width < 2 or height < 2:
        return 0.0
    pixels = gray_image.load()
    total = 0
    comparisons = 0
    for y in range(height):
        for x in range(width):
            value = pixels[x, y]
            if x + 1 < width:
                total += abs(value - pixels[x + 1, y])
                comparisons += 1
            if y + 1 < height:
                total += abs(value - pixels[x, y + 1])
                comparisons += 1
    return round(min(1.0, (total / max(1, comparisons)) / 255.0), 4)


def _frame_metrics(path: Path, fallback_index: int, previous_vector: list[int] | None) -> tuple[dict, list[int]]:
    with Image.open(path) as image:
        image.load()
        gray = image.convert("L")
        stat = ImageStat.Stat(gray)
        brightness = round((stat.mean[0] if stat.mean else 0.0) / 255.0, 4)
        contrast = round(min(1.0, (stat.stddev[0] if stat.stddev else 0.0) / 128.0), 4)
        diff_vector = _diff_vector(gray)
        diff_score = _diff_score(diff_vector, previous_vector)
        if diff_score is None:
            near_duplicate = False
            scene_change = True
        else:
            near_duplicate = diff_score < NEAR_DUPLICATE_DIFF_THRESHOLD
            scene_change = diff_score > SCENE_CHANGE_DIFF_THRESHOLD
        record = {
            "frame_index": _frame_index(path, fallback_index),
            "frame_file": path.name,
            "timestamp_sec": _timestamp_sec(path),
            "width": int(image.width),
            "height": int(image.height),
            "brightness": brightness,
            "contrast": contrast,
            "blur_score": _blur_score(gray),
            "visual_hash": _average_hash(gray),
            "diff_score_vs_previous": diff_score,
            "near_duplicate": near_duplicate,
            "scene_change": scene_change,
        }
        return record, diff_vector


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def _summary_text(records: list[dict], frame_errors: list[dict], message: str | None = None) -> str:
    if not records:
        lines = [
            "CV metadata summary",
            "Frames analyzed: 0",
            message or "No supported frame images were found.",
        ]
        if frame_errors:
            lines.append(f"Unreadable frames skipped: {len(frame_errors)}")
        return "\n".join(lines) + "\n"

    mean_brightness = sum(record["brightness"] for record in records) / len(records)
    mean_contrast = sum(record["contrast"] for record in records) / len(records)
    mean_blur = sum(record["blur_score"] for record in records) / len(records)
    scene_changes = [record for record in records if record["scene_change"]]
    near_duplicates = [record for record in records if record["near_duplicate"]]
    top_scene_changes = sorted(
        [record for record in records if record["diff_score_vs_previous"] is not None],
        key=lambda record: record["diff_score_vs_previous"],
        reverse=True,
    )[:5]

    lines = [
        "CV metadata summary",
        f"Frames analyzed: {len(records)}",
        f"Near-duplicates: {len(near_duplicates)}",
        f"Scene changes: {len(scene_changes)}",
        f"Mean brightness: {mean_brightness:.4f}",
        f"Mean contrast: {mean_contrast:.4f}",
        f"Mean blur score: {mean_blur:.4f}",
        "",
        "Top scene changes:",
    ]
    if top_scene_changes:
        for record in top_scene_changes:
            timestamp = record["timestamp_sec"]
            timestamp_label = f"{timestamp:.3f}s" if isinstance(timestamp, (int, float)) else "unknown"
            lines.append(f"{timestamp_label} - {record['frame_file']} - diff_score {record['diff_score_vs_previous']:.4f}")
    else:
        lines.append("None")
    if frame_errors:
        lines.extend(["", f"Unreadable frames skipped: {len(frame_errors)}"])
    return "\n".join(lines) + "\n"


def analyze_frames(
    *,
    frames_dir: str | Path | None,
    output_dir: str | Path,
    cancel_event=None,
    progress_callback: Callable[[dict], None] | None = None,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "frames_cv.jsonl"
    txt_path = output_path / "frames_cv.txt"

    if not pillow_available():
        message = "Pillow is not available. Install requirements-cv-metadata.txt to enable CV metadata."
        _write_jsonl(jsonl_path, [])
        txt_path.write_text(_summary_text([], [], message), encoding="utf-8", newline="\n")
        return {
            "status": "unavailable",
            "frames_analyzed": 0,
            "jsonl_path": str(jsonl_path),
            "txt_path": str(txt_path),
            "error_message": message,
        }

    if not frames_dir:
        message = "CV metadata requires extracted frames."
        _write_jsonl(jsonl_path, [])
        txt_path.write_text(_summary_text([], [], message), encoding="utf-8", newline="\n")
        return {
            "status": "skipped",
            "frames_analyzed": 0,
            "jsonl_path": str(jsonl_path),
            "txt_path": str(txt_path),
            "error_message": message,
        }

    frames_path = Path(frames_dir)
    frame_paths = [
        path
        for path in sorted(frames_path.iterdir(), key=_frame_sort_key)
        if path.is_file() and path.suffix.lower() in SUPPORTED_FRAME_EXTENSIONS
    ] if frames_path.is_dir() else []

    records: list[dict] = []
    frame_errors: list[dict] = []
    previous_vector: list[int] | None = None
    for fallback_index, frame_path in enumerate(frame_paths, start=1):
        if cancel_event is not None and cancel_event.is_set():
            break
        try:
            record, previous_vector = _frame_metrics(frame_path, fallback_index, previous_vector)
        except (OSError, UnidentifiedImageError) as exc:
            frame_errors.append({"frame_file": frame_path.name, "error_message": str(exc)})
            continue
        records.append(record)
        if progress_callback is not None:
            progress_callback({"status": "running", "frames_analyzed": len(records), "current_frame": frame_path.name})

    cancelled = cancel_event is not None and cancel_event.is_set()
    _write_jsonl(jsonl_path, records)
    message = "CV metadata requires extracted frames." if not frame_paths else None
    txt_path.write_text(_summary_text(records, frame_errors, message), encoding="utf-8", newline="\n")

    status = "cancelled" if cancelled else "completed" if records else "empty"
    return {
        "status": status,
        "frames_analyzed": len(records),
        "frames_skipped": len(frame_errors),
        "near_duplicates": sum(1 for record in records if record["near_duplicate"]),
        "scene_changes": sum(1 for record in records if record["scene_change"]),
        "jsonl_path": str(jsonl_path),
        "txt_path": str(txt_path),
        "frame_errors": frame_errors,
        "error_message": None if records else message or "No supported frame images were found.",
    }
