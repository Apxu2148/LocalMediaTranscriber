from __future__ import annotations

import ctypes
import json
import logging
import math
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from . import config
from .input_event_recorder import InputEventRecorder
from .utils import timestamp_for_filename, write_json_file


logger = logging.getLogger(__name__)

ALLOWED_SCREEN_FPS = (1, 2, 3, 5, 10, 15, 20, 30)
TIMING_MODE_DUPLICATE_FRAMES = "preserve_realtime_by_duplicate_frames"
TIMING_WARNING_DUPLICATE_RATIO = 0.10


class ScreenRecorderError(RuntimeError):
    pass


class ScreenRecorderValidationError(ScreenRecorderError):
    pass


class ScreenRecorderStateError(ScreenRecorderError):
    pass


class ScreenRecorderDependencyError(ScreenRecorderError):
    pass


def create_session_id(now: datetime | None = None) -> str:
    return f"session_{(now or datetime.now()).strftime('%Y%m%d_%H%M%S')}"


def normalize_screen_fps(fps: int | str | None) -> int:
    try:
        normalized = int(fps if fps is not None else 3)
    except (TypeError, ValueError) as exc:
        raise ScreenRecorderValidationError(
            f"Некорректный FPS. Доступны: {', '.join(str(item) for item in ALLOWED_SCREEN_FPS)}."
        ) from exc

    if normalized not in ALLOWED_SCREEN_FPS:
        raise ScreenRecorderValidationError(
            f"Некорректный FPS. Доступны: {', '.join(str(item) for item in ALLOWED_SCREEN_FPS)}."
        )
    return normalized


def normalize_display_indices(display_indices: list[int] | tuple[int, ...] | None) -> list[int]:
    if not display_indices:
        raise ScreenRecorderValidationError("Выберите хотя бы один дисплей для записи")

    normalized: list[int] = []
    for raw_index in display_indices:
        try:
            display_index = int(raw_index)
        except (TypeError, ValueError) as exc:
            raise ScreenRecorderValidationError("Некорректный идентификатор дисплея.") from exc
        if display_index < 1:
            raise ScreenRecorderValidationError("Некорректный идентификатор дисплея.")
        if display_index not in normalized:
            normalized.append(display_index)

    if not normalized:
        raise ScreenRecorderValidationError("Выберите хотя бы один дисплей для записи")
    return normalized


def select_displays(available_displays: list[dict[str, Any]], display_indices: list[int]) -> list[dict[str, Any]]:
    by_index = {int(display["index"]): display for display in available_displays}
    selected: list[dict[str, Any]] = []
    missing: list[int] = []

    for display_index in display_indices:
        display = by_index.get(display_index)
        if display is None:
            missing.append(display_index)
            continue
        selected.append(dict(display))

    if missing:
        missing_text = ", ".join(str(item) for item in missing)
        raise ScreenRecorderValidationError(f"Дисплей не найден: {missing_text}.")
    return selected


def screen_video_filename(display_index: int, timestamp: str, fps: int, suffix: str = ".mp4") -> str:
    return f"screen{int(display_index)}_{timestamp}__{int(fps)}fps{suffix}"


def build_timing_diagnostics(
    *,
    requested_fps: int,
    duration_seconds: float,
    captured_frame_count: int,
    written_frame_count: int,
    duplicated_frame_count: int,
) -> dict[str, Any]:
    duration = max(0.0, float(duration_seconds))
    written = max(0, int(written_frame_count))
    duplicated = max(0, int(duplicated_frame_count))
    captured = max(0, int(captured_frame_count))
    duplicate_ratio = float(duplicated / written) if written else 0.0
    actual_capture_fps = float(captured / duration) if duration > 0 else 0.0

    return {
        "requested_fps": int(requested_fps),
        "written_fps": int(requested_fps),
        "duration_seconds": round(duration, 3),
        "captured_frame_count": captured,
        "written_frame_count": written,
        "duplicated_frame_count": duplicated,
        "duplicate_ratio": round(duplicate_ratio, 6),
        "actual_capture_fps": round(actual_capture_fps, 3),
        "timing_mode": TIMING_MODE_DUPLICATE_FRAMES,
        "timing_warning": duplicate_ratio > TIMING_WARNING_DUPLICATE_RATIO,
    }


def relative_recordings_dir(recordings_dir: Path) -> str:
    try:
        return str(recordings_dir.resolve().relative_to(config.BASE_DIR.resolve())).replace("\\", "/")
    except ValueError:
        return str(recordings_dir)


def recent_media_sessions(
    media_sessions_dir: Path | None = None,
    limit: int = 5,
    legacy_media_sessions_dir: Path | None = None,
) -> list[dict[str, Any]]:
    root = media_sessions_dir or config.RECORDINGS_DIR
    root.mkdir(parents=True, exist_ok=True)

    session_files = [path for path in root.glob("session_*.json") if path.is_file()]
    legacy_root = legacy_media_sessions_dir
    if legacy_root is None and root.resolve() == config.RECORDINGS_DIR.resolve():
        legacy_root = config.MEDIA_SESSIONS_DIR
    if legacy_root is not None and legacy_root.exists():
        session_files.extend(path for path in legacy_root.glob("session_*/session.json") if path.is_file())

    session_files.sort(key=lambda path: path.stat().st_mtime, reverse=True)

    result: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for session_file in session_files:
        if session_file in seen:
            continue
        seen.add(session_file)
        try:
            payload = json.loads(session_file.read_text(encoding="utf-8"))
        except Exception:
            logger.debug("Failed to read media session JSON: %s", session_file, exc_info=True)
            continue

        result.append(
            {
                "session_id": payload.get("session_id") or session_file.stem,
                "created_at": payload.get("created_at"),
                "finished_at": payload.get("finished_at"),
                "status": payload.get("status"),
                "screens": payload.get("screens") or [],
                "session_dir": str(session_file.parent),
                "recordings_dir": payload.get("recordings_dir") or str(session_file.parent),
                "session_json": str(session_file),
            }
        )
        if len(result) >= limit:
            break
    return result


class _WinPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def current_cursor_position() -> tuple[int, int] | None:
    if os.name != "nt":
        return None

    point = _WinPoint()
    try:
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(point)):
            return int(point.x), int(point.y)
    except Exception:
        logger.debug("Failed to read cursor position", exc_info=True)
    return None


class ScreenRecorder:
    def __init__(
        self,
        recordings_dir: Path | None = None,
        *,
        media_sessions_dir: Path | None = None,
    ) -> None:
        self._recordings_dir = recordings_dir or media_sessions_dir or config.RECORDINGS_DIR
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._started_event = threading.Event()
        self._error: str | None = None
        self._session: dict[str, Any] | None = None
        self._session_dir: Path | None = None
        self._session_json_path: Path | None = None
        self._display_indices: list[int] = []
        self._fps = 3
        self._started_at_perf: float | None = None
        self._last_result: dict[str, Any] | None = None

    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def list_displays(self) -> list[dict[str, Any]]:
        try:
            import mss
        except ImportError as exc:
            raise ScreenRecorderDependencyError(
                "Зависимости записи экрана не установлены. Установите mss и opencv-python из requirements."
            ) from exc

        try:
            with mss.mss() as screen_capture:
                displays = []
                for display_index, monitor in enumerate(screen_capture.monitors[1:], start=1):
                    displays.append(
                        {
                            "index": display_index,
                            "name": f"Display {display_index}",
                            "width": int(monitor.get("width", 0)),
                            "height": int(monitor.get("height", 0)),
                            "left": int(monitor.get("left", 0)),
                            "top": int(monitor.get("top", 0)),
                            "is_primary": display_index == 1,
                        }
                    )
                return displays
        except ScreenRecorderDependencyError:
            raise
        except Exception as exc:
            logger.exception("Failed to list displays")
            raise ScreenRecorderError(f"Не удалось получить список дисплеев: {exc}") from exc

    def validate_request(
        self,
        display_indices: list[int] | tuple[int, ...] | None,
        fps: int | str | None,
        available_displays: list[dict[str, Any]] | None = None,
    ) -> tuple[list[int], int, list[dict[str, Any]]]:
        normalized_indices = normalize_display_indices(display_indices)
        normalized_fps = normalize_screen_fps(fps)
        displays = available_displays if available_displays is not None else self.list_displays()
        selected = select_displays(displays, normalized_indices)
        return normalized_indices, normalized_fps, selected

    def create_session(
        self,
        selected_displays: list[dict[str, Any]],
        fps: int,
        source_flags: dict[str, bool] | None = None,
        *,
        timestamp: str | None = None,
        audio_files: dict[str, str | None] | None = None,
    ) -> tuple[str, Path, dict[str, Any]]:
        self._recordings_dir.mkdir(parents=True, exist_ok=True)
        base_timestamp = timestamp or timestamp_for_filename()
        session_timestamp = base_timestamp
        session_id = f"session_{session_timestamp}"
        counter = 2
        while (self._recordings_dir / f"{session_id}.json").exists():
            session_timestamp = f"{base_timestamp}_{counter}"
            session_id = f"session_{session_timestamp}"
            counter += 1

        created_at = datetime.now().isoformat(timespec="seconds")
        sources = {
            "mic": False,
            "system": False,
            "screens": True,
            "mouse": False,
            "keyboard": False,
        }
        if source_flags:
            sources.update({key: bool(value) for key, value in source_flags.items() if key in sources})
            sources["screens"] = True

        normalized_audio = {
            "mic": audio_files.get("mic") if audio_files else None,
            "system": audio_files.get("system") if audio_files else None,
        }

        session = {
            "session_id": session_id,
            "created_at": created_at,
            "finished_at": None,
            "type": "screen_recording_mvp",
            "sources": sources,
            "recordings_dir": relative_recordings_dir(self._recordings_dir),
            "screens": [
                {
                    "screen_index": int(display["index"]),
                    "name": display.get("name") or f"Display {display['index']}",
                    "width": int(display["width"]),
                    "height": int(display["height"]),
                    "left": int(display["left"]),
                    "top": int(display["top"]),
                    "video_file": screen_video_filename(int(display["index"]), session_timestamp, fps),
                    "video_path": screen_video_filename(int(display["index"]), session_timestamp, fps),
                    "fps": fps,
                    "requested_fps": fps,
                    "written_fps": fps,
                    "duration_seconds": 0,
                    "duration_sec": 0,
                    "captured_frame_count": 0,
                    "written_frame_count": 0,
                    "duplicated_frame_count": 0,
                    "duplicate_ratio": 0.0,
                    "actual_capture_fps": 0.0,
                    "timing_mode": TIMING_MODE_DUPLICATE_FRAMES,
                    "timing_warning": False,
                    "cursor_drawn": False,
                    "cursor_warning": False,
                    "codec": "mp4v",
                }
                for display in selected_displays
            ],
            "audio": normalized_audio,
            "events": {
                "mouse": None,
                "keyboard": None,
            },
            "event_logging": {
                "mouse_enabled": bool(sources["mouse"]),
                "keyboard_enabled": bool(sources["keyboard"]),
                "mouse_status": "pending" if sources["mouse"] else "disabled",
                "keyboard_status": "pending" if sources["keyboard"] else "disabled",
                "mouse_error": None,
                "keyboard_error": None,
            },
            "status": "recording",
        }
        write_json_file(self._recordings_dir / f"{session_id}.json", session)
        return session_id, self._recordings_dir, session

    def start(
        self,
        selected_display_indices: list[int] | tuple[int, ...] | None,
        fps: int | str | None,
        source_flags: dict[str, bool] | None = None,
        *,
        timestamp: str | None = None,
        audio_files: dict[str, str | None] | None = None,
        record_mouse: bool = False,
        record_keyboard: bool = False,
    ) -> dict[str, Any]:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise ScreenRecorderStateError("Запись экрана уже идет.")

        display_indices, normalized_fps, selected_displays = self.validate_request(selected_display_indices, fps)
        session_id, session_dir, session = self.create_session(
            selected_displays,
            normalized_fps,
            {
                **(source_flags or {}),
                "mouse": bool(record_mouse),
                "keyboard": bool(record_keyboard),
            },
            timestamp=timestamp,
            audio_files=audio_files,
        )
        session_json_path = session_dir / f"{session_id}.json"

        stop_event = threading.Event()
        started_event = threading.Event()
        thread = threading.Thread(
            target=self._record_loop,
            args=(selected_displays, normalized_fps, session_dir, session_json_path, session, stop_event, started_event),
            name="screen-recorder",
            daemon=True,
        )

        with self._lock:
            self._thread = thread
            self._stop_event = stop_event
            self._started_event = started_event
            self._error = None
            self._session = session
            self._session_dir = session_dir
            self._session_json_path = session_json_path
            self._display_indices = display_indices
            self._fps = normalized_fps
            self._started_at_perf = time.perf_counter()
            self._last_result = None

        logger.info(
            "Starting screen recording: session_id=%s displays=%s fps=%s recordings_dir=%s",
            session_id,
            display_indices,
            normalized_fps,
            session_dir,
        )
        thread.start()

        if not started_event.wait(timeout=8):
            stop_event.set()
            thread.join(timeout=5)
            error = "Не удалось начать запись экрана: поток записи не запустился вовремя."
            self._mark_failed(error)
            self._clear_state_after_start_failure()
            raise ScreenRecorderError(error)

        with self._lock:
            error = self._error
            alive = self._thread is not None and self._thread.is_alive()

        if error and not alive:
            self._clear_state_after_start_failure()
            raise ScreenRecorderError(error)

        return self._current_summary("Запись экрана началась.")

    def stop(self) -> dict[str, Any]:
        with self._lock:
            thread = self._thread
            if thread is None or not thread.is_alive():
                raise ScreenRecorderStateError("Запись экрана не запущена.")
            stop_event = self._stop_event

        stop_event.set()
        thread.join(timeout=15)

        with self._lock:
            if thread.is_alive():
                self._error = "Не удалось остановить запись экрана: поток записи не завершился вовремя."
                error = self._error
            else:
                error = self._error
            result = self._last_result or self._summary_from_session_locked()
            self._thread = None
            self._started_at_perf = None

        if error and result.get("status") != "completed":
            raise ScreenRecorderError(error)

        logger.info("Screen recording stopped: session_id=%s status=%s", result.get("session_id"), result.get("status"))
        return result

    def status(self) -> dict[str, Any]:
        with self._lock:
            is_recording = self._thread is not None and self._thread.is_alive()
            started_at = self._session.get("created_at") if self._session else None
            elapsed = (
                round(time.perf_counter() - self._started_at_perf, 1)
                if is_recording and self._started_at_perf is not None
                else 0
            )
            event_logging = self._session.get("event_logging") if self._session else {}
            return {
                "is_recording": is_recording,
                "session_id": self._session.get("session_id") if self._session else None,
                "session_dir": str(self._session_dir) if self._session_dir else None,
                "recordings_dir": str(self._session_dir) if self._session_dir else None,
                "session_json": str(self._session_json_path) if self._session_json_path else None,
                "display_indices": list(self._display_indices),
                "fps": self._fps,
                "started_at": started_at,
                "elapsed_sec": elapsed,
                "status": self._session.get("status") if self._session else None,
                "error": self._error,
                "event_logging": event_logging,
                "mouse_events": self._event_api_state(event_logging, "mouse", is_recording),
                "keyboard_events": self._event_api_state(event_logging, "keyboard", is_recording),
            }

    def _record_loop(
        self,
        selected_displays: list[dict[str, Any]],
        fps: int,
        recordings_dir: Path,
        session_json_path: Path,
        session: dict[str, Any],
        stop_event: threading.Event,
        started_event: threading.Event,
    ) -> None:
        writers: list[dict[str, Any]] = []
        frame_interval = 1.0 / float(fps)
        started_at = time.perf_counter()
        finished_at = started_at
        error: str | None = None
        input_events: InputEventRecorder | None = None

        try:
            import cv2
            import mss
            import numpy as np
        except ImportError:
            error = "Зависимости записи экрана не установлены. Установите mss и opencv-python из requirements."
            self._fail_worker(recordings_dir, session_json_path, session, error, started_event)
            return

        try:
            for display in selected_displays:
                writer_info = self._open_video_writer(cv2, recordings_dir, display, fps, session)
                writers.append(
                    {
                        **writer_info,
                        "display": display,
                        "latest_frame": None,
                        "has_fresh_frame": False,
                        "captured_frame_count": 0,
                        "written_frame_count": 0,
                        "duplicated_frame_count": 0,
                        "capture_warning_count": 0,
                        "last_capture_error": None,
                        "cursor_warning": False,
                        "cursor_drawn": False,
                        "next_frame_at": 0.0,
                    }
                )
                self._update_session_screen(
                    session,
                    int(display["index"]),
                    writer_info["relative_path"],
                    writer_info["path"].name,
                    writer_info["codec"],
                    {},
                )

            with mss.mss() as screen_capture:
                for item in writers:
                    first_frame = self._wait_for_first_frame(
                        screen_capture,
                        np,
                        cv2,
                        item["display"],
                        stop_event,
                        timeout_seconds=5.0,
                    )
                    if first_frame is None:
                        raise ScreenRecorderError(
                            f"Не удалось получить первый кадр для дисплея {int(item['display']['index'])}."
                        )
                    item["latest_frame"] = first_frame
                    item["has_fresh_frame"] = True
                    item["captured_frame_count"] = 1

                started_at = time.perf_counter()
                for item in writers:
                    item["next_frame_at"] = started_at

                input_events = InputEventRecorder(
                    recordings_dir=recordings_dir,
                    timestamp=str(session.get("session_id") or "").removeprefix("session_"),
                    screens=session.get("screens") or [],
                    fps=fps,
                    record_mouse=bool(session.get("sources", {}).get("mouse")),
                    record_keyboard=bool(session.get("sources", {}).get("keyboard")),
                )
                self._apply_input_event_metadata(session, input_events.start(started_at=started_at))
                write_json_file(session_json_path, session)
                with self._lock:
                    self._session = session
                started_event.set()

                while not stop_event.is_set():
                    wrote_any = False
                    for item in writers:
                        wrote_any = self._write_due_frames(
                            item,
                            screen_capture,
                            np,
                            cv2,
                            frame_interval,
                            allow_capture=True,
                            until=time.perf_counter(),
                        ) or wrote_any

                    if wrote_any:
                        continue

                    next_due = min(float(item["next_frame_at"]) for item in writers)
                    wait_seconds = max(0.001, min(0.05, next_due - time.perf_counter()))
                    stop_event.wait(wait_seconds)

                stop_time = time.perf_counter()
                finished_at = stop_time
                for item in writers:
                    self._write_due_frames(
                        item,
                        screen_capture,
                        np,
                        cv2,
                        frame_interval,
                        allow_capture=False,
                        until=stop_time,
                    )
        except Exception as exc:
            error = f"Не удалось записать экран: {exc}"
            logger.exception("Screen recorder failed")
            if not started_event.is_set():
                started_event.set()
        finally:
            if input_events is not None:
                self._apply_input_event_metadata(session, input_events.stop())

            for item in writers:
                try:
                    item["writer"].release()
                except Exception:
                    logger.debug("Failed to release screen video writer", exc_info=True)

            if error:
                self._remove_video_outputs(writers)

            if finished_at <= started_at:
                finished_at = time.perf_counter()
            duration = max(0.0, finished_at - started_at)
            self._finish_session(recordings_dir, session_json_path, session, writers, duration, error)

    def _wait_for_first_frame(
        self,
        screen_capture: Any,
        np: Any,
        cv2: Any,
        display: dict[str, Any],
        stop_event: threading.Event,
        *,
        timeout_seconds: float,
    ) -> Any | None:
        deadline = time.perf_counter() + timeout_seconds
        while not stop_event.is_set() and time.perf_counter() < deadline:
            try:
                return self._capture_frame(screen_capture, np, cv2, display)
            except Exception:
                logger.debug("Initial screen frame capture failed", exc_info=True)
                stop_event.wait(0.05)
        return None

    def _write_due_frames(
        self,
        item: dict[str, Any],
        screen_capture: Any,
        np: Any,
        cv2: Any,
        frame_interval: float,
        *,
        allow_capture: bool,
        until: float,
    ) -> bool:
        next_frame_at = float(item["next_frame_at"])
        if until < next_frame_at:
            return False

        slots_due = max(1, int(math.floor((until - next_frame_at) / frame_interval)) + 1)
        if allow_capture:
            try:
                item["latest_frame"] = self._capture_frame(screen_capture, np, cv2, item["display"])
                item["has_fresh_frame"] = True
                item["captured_frame_count"] += 1
            except Exception as exc:
                item["capture_warning_count"] += 1
                item["last_capture_error"] = str(exc)
                logger.debug("Screen frame capture failed; duplicating latest frame", exc_info=True)

        for slot_index in range(slots_due):
            latest_frame = item.get("latest_frame")
            if latest_frame is None:
                break

            is_duplicate = not item.get("has_fresh_frame")
            self._write_frame_with_cursor(cv2, item, latest_frame)
            item["written_frame_count"] += 1
            if is_duplicate:
                item["duplicated_frame_count"] += 1
            item["has_fresh_frame"] = False
            item["next_frame_at"] = next_frame_at + frame_interval * float(slot_index + 1)

        return True

    def _capture_frame(self, screen_capture: Any, np: Any, cv2: Any, display: dict[str, Any]) -> Any:
        monitor = {
            "left": int(display["left"]),
            "top": int(display["top"]),
            "width": int(display["width"]),
            "height": int(display["height"]),
        }
        frame = np.array(screen_capture.grab(monitor))
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def _write_frame_with_cursor(self, cv2: Any, item: dict[str, Any], raw_frame: Any) -> None:
        frame = raw_frame.copy()
        cursor = current_cursor_position()
        if cursor is None:
            item["cursor_warning"] = True
        elif self._draw_cursor_marker(cv2, frame, item["display"], cursor):
            item["cursor_drawn"] = True
        item["writer"].write(frame)

    def _draw_cursor_marker(
        self,
        cv2: Any,
        frame: Any,
        display: dict[str, Any],
        cursor: tuple[int, int],
    ) -> bool:
        cursor_x, cursor_y = cursor
        left = int(display["left"])
        top = int(display["top"])
        width = int(display["width"])
        height = int(display["height"])
        if not (left <= cursor_x < left + width and top <= cursor_y < top + height):
            return False

        x = int(cursor_x - left)
        y = int(cursor_y - top)
        cv2.circle(frame, (x, y), 8, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(frame, (x, y), (min(width - 1, x + 14), min(height - 1, y + 20)), (0, 0, 0), 3, cv2.LINE_AA)
        cv2.line(frame, (x, y), (min(width - 1, x + 14), min(height - 1, y + 20)), (255, 255, 255), 1, cv2.LINE_AA)
        return True

    def _open_video_writer(
        self,
        cv2: Any,
        recordings_dir: Path,
        display: dict[str, Any],
        fps: int,
        session: dict[str, Any],
    ) -> dict[str, Any]:
        display_index = int(display["index"])
        width = int(display["width"])
        height = int(display["height"])
        attempts = [
            ("mp4v", ".mp4"),
            ("XVID", ".avi"),
            ("MJPG", ".avi"),
        ]
        screen = self._session_screen(session, display_index)
        base_name = Path(screen["video_file"]).stem

        for codec, suffix in attempts:
            output_path = recordings_dir / f"{base_name}{suffix}"
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(str(output_path), fourcc, float(fps), (width, height))
            if writer.isOpened():
                return {
                    "writer": writer,
                    "path": output_path,
                    "relative_path": output_path.name,
                    "codec": codec,
                }
            writer.release()

        raise ScreenRecorderError(f"Не удалось открыть video writer для дисплея {display_index}.")

    def _session_screen(self, session: dict[str, Any], display_index: int) -> dict[str, Any]:
        for screen in session["screens"]:
            if int(screen["screen_index"]) == display_index:
                return screen
        raise ScreenRecorderError(f"Дисплей не найден: {display_index}.")

    def _update_session_screen(
        self,
        session: dict[str, Any],
        display_index: int,
        relative_path: str,
        video_file: str,
        codec: str,
        diagnostics: dict[str, Any],
    ) -> None:
        screen = self._session_screen(session, display_index)
        screen["video_file"] = video_file
        screen["video_path"] = relative_path
        screen["codec"] = codec
        screen.update(diagnostics)
        if "duration_seconds" in diagnostics:
            screen["duration_sec"] = diagnostics["duration_seconds"]

    def _finish_session(
        self,
        recordings_dir: Path,
        session_json_path: Path,
        session: dict[str, Any],
        writers: list[dict[str, Any]],
        duration: float,
        error: str | None,
    ) -> None:
        for item in writers:
            screen = self._session_screen(session, int(item["display"]["index"]))
            requested_fps = int(screen.get("requested_fps") or self._fps)
            diagnostics = build_timing_diagnostics(
                requested_fps=requested_fps,
                duration_seconds=duration,
                captured_frame_count=int(item.get("captured_frame_count") or 0),
                written_frame_count=int(item.get("written_frame_count") or 0),
                duplicated_frame_count=int(item.get("duplicated_frame_count") or 0),
            )
            diagnostics.update(
                {
                    "capture_warning_count": int(item.get("capture_warning_count") or 0),
                    "last_capture_error": item.get("last_capture_error"),
                    "cursor_drawn": bool(item.get("cursor_drawn")),
                    "cursor_warning": bool(item.get("cursor_warning")),
                }
            )
            self._update_session_screen(
                session,
                int(item["display"]["index"]),
                item["relative_path"],
                item["path"].name,
                item["codec"],
                diagnostics,
            )

        session["finished_at"] = datetime.now().isoformat(timespec="seconds")
        session["status"] = "failed" if error else "completed"
        if error:
            session["error"] = error

        write_json_file(session_json_path, session)
        result = self._summary_from_session(recordings_dir, session_json_path, session)

        with self._lock:
            self._session = session
            self._error = error
            self._last_result = result

    def _fail_worker(
        self,
        recordings_dir: Path,
        session_json_path: Path,
        session: dict[str, Any],
        error: str,
        started_event: threading.Event,
    ) -> None:
        logger.exception("Screen recorder dependency failure")
        session["finished_at"] = datetime.now().isoformat(timespec="seconds")
        session["status"] = "failed"
        session["error"] = error
        write_json_file(session_json_path, session)
        with self._lock:
            self._session = session
            self._error = error
            self._last_result = self._summary_from_session(recordings_dir, session_json_path, session)
        started_event.set()

    def _mark_failed(self, error: str) -> None:
        with self._lock:
            session = self._session
            session_dir = self._session_dir
            session_json_path = self._session_json_path
            self._error = error
        if session and session_dir and session_json_path:
            self._finish_session(session_dir, session_json_path, session, [], 0, error)

    def _remove_video_outputs(self, writers: list[dict[str, Any]]) -> None:
        for item in writers:
            path = item.get("path")
            if isinstance(path, Path):
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    logger.debug("Failed to remove failed screen video: %s", path, exc_info=True)

    def _current_summary(self, message: str) -> dict[str, Any]:
        with self._lock:
            result = self._summary_from_session_locked()
            result.update({"message": message, "recording": True})
            return result

    def _summary_from_session_locked(self) -> dict[str, Any]:
        if self._session_dir is None or self._session is None or self._session_json_path is None:
            return {}
        return self._summary_from_session(self._session_dir, self._session_json_path, self._session)

    def _summary_from_session(self, recordings_dir: Path, session_json_path: Path, session: dict[str, Any]) -> dict[str, Any]:
        screens = session.get("screens") or []
        video_paths = [str(recordings_dir / screen["video_path"]) for screen in screens if screen.get("video_path")]
        duration = max((float(screen.get("duration_seconds") or 0) for screen in screens), default=0.0)
        warnings: list[str] = []
        if any(screen.get("timing_warning") for screen in screens):
            warnings.append("screen_timing_warning")
        if any(screen.get("cursor_warning") for screen in screens):
            warnings.append("screen_cursor_warning")
        event_logging = session.get("event_logging") or {}
        if event_logging.get("mouse_status") == "failed":
            warnings.append("mouse_event_logging_failed")
        if event_logging.get("keyboard_status") == "failed":
            warnings.append("keyboard_event_logging_failed")
        return {
            "source_type": "screen",
            "session_id": session.get("session_id"),
            "session_dir": str(recordings_dir),
            "recordings_dir": str(recordings_dir),
            "session_json": str(session_json_path),
            "display_indices": [int(screen["screen_index"]) for screen in screens],
            "fps": self._fps,
            "screens": screens,
            "audio": session.get("audio") or {},
            "events": session.get("events") or {},
            "event_logging": event_logging,
            "video_paths": video_paths,
            "duration_sec": round(duration, 3),
            "status": session.get("status"),
            "warnings": warnings,
            "error": session.get("error"),
        }

    def _clear_state_after_start_failure(self) -> None:
        with self._lock:
            self._thread = None
            self._started_at_perf = None

    def _apply_input_event_metadata(self, session: dict[str, Any], metadata: dict[str, Any]) -> None:
        session.setdefault("events", {"mouse": None, "keyboard": None})
        session.setdefault("event_logging", {})
        session["events"].update(metadata.get("events") or {})
        session["event_logging"].update(metadata.get("event_logging") or {})

    def _event_api_state(self, event_logging: dict[str, Any], source: str, is_recording: bool) -> str:
        enabled = bool(event_logging.get(f"{source}_enabled"))
        status = str(event_logging.get(f"{source}_status") or ("pending" if enabled else "disabled"))
        if not enabled:
            return "disabled"
        if status == "failed":
            return "failed"
        if is_recording and status == "ok":
            return "recording"
        return status
