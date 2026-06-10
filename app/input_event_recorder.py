from __future__ import annotations

import json
import logging
import re
import threading
import time
from pathlib import Path
from typing import Any, Callable


logger = logging.getLogger(__name__)

ERROR_MESSAGE_LIMIT = 240
MODIFIER_ORDER = ("Ctrl", "Alt", "Shift", "Win")
HOTKEY_TEXT_MODIFIERS = {"Ctrl", "Alt", "Win"}

MODIFIER_KEYS = {
    "ctrl": "Ctrl",
    "ctrl_l": "Ctrl",
    "ctrl_r": "Ctrl",
    "control": "Ctrl",
    "alt": "Alt",
    "alt_l": "Alt",
    "alt_r": "Alt",
    "alt_gr": "Alt",
    "shift": "Shift",
    "shift_l": "Shift",
    "shift_r": "Shift",
    "cmd": "Win",
    "cmd_l": "Win",
    "cmd_r": "Win",
    "win": "Win",
    "win_l": "Win",
    "win_r": "Win",
    "super": "Win",
}

SPECIAL_KEYS = {
    "enter": "Enter",
    "return": "Enter",
    "esc": "Esc",
    "escape": "Esc",
    "tab": "Tab",
    "backspace": "Backspace",
    "delete": "Delete",
    "del": "Delete",
    "up": "ArrowUp",
    "down": "ArrowDown",
    "left": "ArrowLeft",
    "right": "ArrowRight",
    "home": "Home",
    "end": "End",
    "page_up": "PageUp",
    "page_down": "PageDown",
    "insert": "Insert",
    "space": "Space",
}


class JsonlEventWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._file: Any | None = None
        self._lock = threading.Lock()

    def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8", buffering=1)

    def write(self, event: dict[str, Any]) -> None:
        with self._lock:
            if self._file is None:
                raise RuntimeError("JSONL writer is not open.")
            self._file.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
            self._file.write("\n")
            self._file.flush()

    def close(self) -> None:
        with self._lock:
            if self._file is None:
                return
            self._file.flush()
            self._file.close()
            self._file = None


class InputEventRecorder:
    def __init__(
        self,
        *,
        recordings_dir: Path,
        timestamp: str,
        screens: list[dict[str, Any]],
        fps: int,
        record_mouse: bool = False,
        record_keyboard: bool = False,
        mouse_listener_factory: Callable[..., Any] | None = None,
        keyboard_listener_factory: Callable[..., Any] | None = None,
        mouse_position_provider: Callable[[], tuple[int, int] | None] | None = None,
        time_fn: Callable[[], float] = time.perf_counter,
        start_mouse_sampler: bool = True,
    ) -> None:
        self.recordings_dir = recordings_dir
        self.timestamp = timestamp
        self.screens = [dict(screen) for screen in screens]
        self.fps = max(1, int(fps))
        self.record_mouse = bool(record_mouse)
        self.record_keyboard = bool(record_keyboard)
        self._mouse_listener_factory = mouse_listener_factory
        self._keyboard_listener_factory = keyboard_listener_factory
        self._mouse_position_provider = mouse_position_provider
        self._time_fn = time_fn
        self._start_mouse_sampler = start_mouse_sampler
        self._started_at: float | None = None
        self._mouse_writer: JsonlEventWriter | None = None
        self._keyboard_writer: JsonlEventWriter | None = None
        self._mouse_file_created = False
        self._keyboard_file_created = False
        self._mouse_listener: Any | None = None
        self._keyboard_listener: Any | None = None
        self._mouse_sample_stop = threading.Event()
        self._mouse_sample_thread: threading.Thread | None = None
        self._mouse_status = "pending" if self.record_mouse else "disabled"
        self._keyboard_status = "pending" if self.record_keyboard else "disabled"
        self._mouse_error: str | None = None
        self._keyboard_error: str | None = None
        self._keyboard_lock = threading.Lock()
        self._active_modifiers: set[str] = set()
        self._pressed_keys: set[str] = set()
        self._hotkey_key_ids: set[str] = set()

    @property
    def mouse_filename(self) -> str:
        return f"mouse_events_{self.timestamp}.jsonl"

    @property
    def keyboard_filename(self) -> str:
        return f"keyboard_events_{self.timestamp}.jsonl"

    @property
    def mouse_path(self) -> Path:
        return self.recordings_dir / self.mouse_filename

    @property
    def keyboard_path(self) -> Path:
        return self.recordings_dir / self.keyboard_filename

    def start(self, started_at: float | None = None) -> dict[str, Any]:
        self._started_at = started_at if started_at is not None else self._time_fn()
        if self.record_mouse:
            self._start_mouse()
        if self.record_keyboard:
            self._start_keyboard()
        return self.session_metadata()

    def stop(self) -> dict[str, Any]:
        self._mouse_sample_stop.set()
        if self._mouse_sample_thread is not None:
            self._mouse_sample_thread.join(timeout=2)
            self._mouse_sample_thread = None
        self._stop_listener(self._mouse_listener)
        self._stop_listener(self._keyboard_listener)
        self._mouse_listener = None
        self._keyboard_listener = None
        self._close_writer(self._mouse_writer)
        self._close_writer(self._keyboard_writer)
        return self.session_metadata()

    def session_metadata(self) -> dict[str, Any]:
        return {
            "events": {
                "mouse": self.mouse_filename if self.record_mouse and self._mouse_file_created else None,
                "keyboard": self.keyboard_filename if self.record_keyboard and self._keyboard_file_created else None,
            },
            "event_logging": {
                "mouse_enabled": self.record_mouse,
                "keyboard_enabled": self.record_keyboard,
                "mouse_status": self._mouse_status,
                "keyboard_status": self._keyboard_status,
                "mouse_error": self._mouse_error,
                "keyboard_error": self._keyboard_error,
            },
        }

    def api_state(self, active: bool) -> dict[str, str]:
        return {
            "mouse_events": self._channel_api_state(self.record_mouse, self._mouse_status, active),
            "keyboard_events": self._channel_api_state(self.record_keyboard, self._keyboard_status, active),
        }

    def record_mouse_position(
        self,
        x: int | float,
        y: int | float,
        *,
        t: float | None = None,
        frame_index: int | None = None,
    ) -> None:
        event = self._mouse_event_base("position", x, y, t=t)
        if frame_index is not None:
            event["frame_index"] = int(frame_index)
        self._write_mouse_event(event)

    def handle_mouse_click(self, x: int | float, y: int | float, button: Any, pressed: bool) -> None:
        event = self._mouse_event_base("down" if pressed else "up", x, y)
        event["button"] = normalize_mouse_button(button)
        self._write_mouse_event(event)

    def handle_mouse_scroll(self, x: int | float, y: int | float, dx: int | float, dy: int | float) -> None:
        event = self._mouse_event_base("scroll", x, y)
        event["dx"] = int(dx)
        event["dy"] = int(dy)
        self._write_mouse_event(event)

    def handle_key_press(self, key: Any) -> None:
        key_id = keyboard_key_id(key)
        normalized = normalize_keyboard_key(key)
        if normalized is None:
            return
        key_name, key_type = normalized

        with self._keyboard_lock:
            if key_id in self._pressed_keys:
                return
            self._pressed_keys.add(key_id)

            if key_type == "modifier":
                self._active_modifiers.add(key_name)
                self._write_keyboard_event({"t": self._relative_time(), "type": "key_down", "key": key_name})
                return

            modifiers = [name for name in MODIFIER_ORDER if name in self._active_modifiers]
            if key_type == "char":
                if HOTKEY_TEXT_MODIFIERS.intersection(modifiers):
                    self._hotkey_key_ids.add(key_id)
                    self._write_keyboard_event(
                        {"t": self._relative_time(), "type": "hotkey", "keys": [*modifiers, key_name]}
                    )
                return

            if key_type == "special" and modifiers:
                self._hotkey_key_ids.add(key_id)
                self._write_keyboard_event({"t": self._relative_time(), "type": "hotkey", "keys": [*modifiers, key_name]})
                return

            if key_type == "special":
                self._write_keyboard_event({"t": self._relative_time(), "type": "key_down", "key": key_name})

    def handle_key_release(self, key: Any) -> None:
        key_id = keyboard_key_id(key)
        normalized = normalize_keyboard_key(key)
        if normalized is None:
            return
        key_name, key_type = normalized

        with self._keyboard_lock:
            self._pressed_keys.discard(key_id)
            if key_id in self._hotkey_key_ids:
                self._hotkey_key_ids.discard(key_id)
                if key_type == "modifier":
                    self._active_modifiers.discard(key_name)
                return

            if key_type == "modifier":
                self._active_modifiers.discard(key_name)
                self._write_keyboard_event({"t": self._relative_time(), "type": "key_up", "key": key_name})
                return

            if key_type == "special":
                self._write_keyboard_event({"t": self._relative_time(), "type": "key_up", "key": key_name})

    def _start_mouse(self) -> None:
        try:
            self._mouse_writer = JsonlEventWriter(self.mouse_path)
            self._mouse_writer.open()
            self._mouse_file_created = True
            self._ensure_mouse_dependencies()
            self._mouse_listener = self._mouse_listener_factory(
                on_click=self._safe_mouse_click,
                on_scroll=self._safe_mouse_scroll,
            )
            self._mouse_listener.start()
            self._mouse_status = "ok"
            if self._start_mouse_sampler:
                self._mouse_sample_stop.clear()
                self._mouse_sample_thread = threading.Thread(
                    target=self._mouse_sample_loop,
                    name="input-event-mouse-sampler",
                    daemon=True,
                )
                self._mouse_sample_thread.start()
            logger.info("Mouse event logging started: path=%s fps=%s", self.mouse_path, self.fps)
        except Exception as exc:
            logger.warning("Mouse event logging failed to start: %s", exc, exc_info=True)
            self._stop_listener(self._mouse_listener)
            self._mouse_listener = None
            self._mark_mouse_failed(exc)

    def _start_keyboard(self) -> None:
        try:
            self._keyboard_writer = JsonlEventWriter(self.keyboard_path)
            self._keyboard_writer.open()
            self._keyboard_file_created = True
            self._ensure_keyboard_dependencies()
            self._keyboard_listener = self._keyboard_listener_factory(
                on_press=self._safe_key_press,
                on_release=self._safe_key_release,
            )
            self._keyboard_listener.start()
            self._keyboard_status = "ok"
            logger.info("Keyboard event logging started: path=%s", self.keyboard_path)
        except Exception as exc:
            logger.warning("Keyboard event logging failed to start: %s", exc, exc_info=True)
            self._stop_listener(self._keyboard_listener)
            self._keyboard_listener = None
            self._mark_keyboard_failed(exc)

    def _ensure_mouse_dependencies(self) -> None:
        if self._mouse_listener_factory is not None and self._mouse_position_provider is not None:
            return
        try:
            from pynput import mouse
        except Exception as exc:
            raise RuntimeError(f"pynput mouse listener unavailable: {sanitize_error(exc)}") from exc
        if self._mouse_listener_factory is None:
            self._mouse_listener_factory = mouse.Listener
        if self._mouse_position_provider is None:
            controller = mouse.Controller()
            self._mouse_position_provider = lambda: tuple(int(value) for value in controller.position)

    def _ensure_keyboard_dependencies(self) -> None:
        if self._keyboard_listener_factory is not None:
            return
        try:
            from pynput import keyboard
        except Exception as exc:
            raise RuntimeError(f"pynput keyboard listener unavailable: {sanitize_error(exc)}") from exc
        self._keyboard_listener_factory = keyboard.Listener

    def _mouse_sample_loop(self) -> None:
        interval = 1.0 / float(self.fps)
        next_sample_at = self._started_at if self._started_at is not None else self._time_fn()
        while not self._mouse_sample_stop.is_set():
            now = self._time_fn()
            if now < next_sample_at:
                self._mouse_sample_stop.wait(min(0.05, max(0.001, next_sample_at - now)))
                continue
            try:
                position = self._mouse_position_provider() if self._mouse_position_provider else None
                if position is not None:
                    self.record_mouse_position(position[0], position[1], t=self._relative_time(now))
            except Exception as exc:
                logger.warning("Mouse position sampler failed: %s", exc, exc_info=True)
                self._mark_mouse_failed(exc)
                break
            next_sample_at += interval

    def _safe_mouse_click(self, x: int | float, y: int | float, button: Any, pressed: bool) -> None:
        try:
            self.handle_mouse_click(x, y, button, pressed)
        except Exception as exc:
            logger.debug("Mouse click event write failed", exc_info=True)
            self._mark_mouse_failed(exc)

    def _safe_mouse_scroll(self, x: int | float, y: int | float, dx: int | float, dy: int | float) -> None:
        try:
            self.handle_mouse_scroll(x, y, dx, dy)
        except Exception as exc:
            logger.debug("Mouse scroll event write failed", exc_info=True)
            self._mark_mouse_failed(exc)

    def _safe_key_press(self, key: Any) -> None:
        try:
            self.handle_key_press(key)
        except Exception as exc:
            logger.debug("Keyboard press event write failed", exc_info=True)
            self._mark_keyboard_failed(exc)

    def _safe_key_release(self, key: Any) -> None:
        try:
            self.handle_key_release(key)
        except Exception as exc:
            logger.debug("Keyboard release event write failed", exc_info=True)
            self._mark_keyboard_failed(exc)

    def _mouse_event_base(self, event_type: str, x: int | float, y: int | float, *, t: float | None = None) -> dict[str, Any]:
        x_int = int(x)
        y_int = int(y)
        screen = locate_screen(self.screens, x_int, y_int)
        return {
            "t": self._relative_time() if t is None else round(max(0.0, float(t)), 6),
            "type": event_type,
            "x": x_int,
            "y": y_int,
            "screen_index": screen["screen_index"],
            "screen_status": screen["screen_status"],
        }

    def _write_mouse_event(self, event: dict[str, Any]) -> None:
        if self._mouse_writer is None or self._mouse_status == "failed":
            return
        self._mouse_writer.write(event)

    def _write_keyboard_event(self, event: dict[str, Any]) -> None:
        if self._keyboard_writer is None or self._keyboard_status == "failed":
            return
        self._keyboard_writer.write(event)

    def _relative_time(self, now: float | None = None) -> float:
        current = self._time_fn() if now is None else now
        if self._started_at is None:
            return 0.0
        return round(max(0.0, current - self._started_at), 6)

    def _mark_mouse_failed(self, exc: Exception) -> None:
        self._mouse_status = "failed"
        self._mouse_error = sanitize_error(exc)
        self._write_diagnostic(self._mouse_writer, self._mouse_error)

    def _mark_keyboard_failed(self, exc: Exception) -> None:
        self._keyboard_status = "failed"
        self._keyboard_error = sanitize_error(exc)
        self._write_diagnostic(self._keyboard_writer, self._keyboard_error)

    def _write_diagnostic(self, writer: JsonlEventWriter | None, error: str | None) -> None:
        if writer is None or error is None:
            return
        try:
            writer.write({"t": self._relative_time(), "type": "diagnostic", "status": "failed", "error": error})
        except Exception:
            logger.debug("Failed to write input event diagnostic", exc_info=True)

    def _stop_listener(self, listener: Any | None) -> None:
        if listener is None:
            return
        try:
            listener.stop()
        except Exception:
            logger.debug("Failed to stop input listener", exc_info=True)
        join = getattr(listener, "join", None)
        if callable(join):
            try:
                join(timeout=2)
            except RuntimeError:
                pass
            except Exception:
                logger.debug("Failed to join input listener", exc_info=True)

    def _close_writer(self, writer: JsonlEventWriter | None) -> None:
        if writer is None:
            return
        try:
            writer.close()
        except Exception:
            logger.debug("Failed to close input event writer", exc_info=True)

    @staticmethod
    def _channel_api_state(enabled: bool, status: str, active: bool) -> str:
        if not enabled:
            return "disabled"
        if status == "failed":
            return "failed"
        if active and status == "ok":
            return "recording"
        return status


def locate_screen(screens: list[dict[str, Any]], x: int, y: int) -> dict[str, Any]:
    for screen in screens:
        left = int(screen.get("left") or 0)
        top = int(screen.get("top") or 0)
        width = int(screen.get("width") or 0)
        height = int(screen.get("height") or 0)
        if left <= x < left + width and top <= y < top + height:
            return {
                "screen_index": int(screen.get("screen_index") or screen.get("index")),
                "screen_status": "recorded_screen",
            }
    return {"screen_index": None, "screen_status": "outside_recorded_screens"}


def normalize_mouse_button(button: Any) -> str:
    raw_name = getattr(button, "name", None) or str(button).split(".")[-1]
    name = str(raw_name).lower()
    if name in {"left", "right", "middle"}:
        return name
    return re.sub(r"[^a-z0-9_+-]+", "_", name).strip("_") or "unknown"


def normalize_keyboard_key(key: Any) -> tuple[str, str] | None:
    name = keyboard_key_name(key)
    if name in MODIFIER_KEYS:
        return MODIFIER_KEYS[name], "modifier"
    if name in SPECIAL_KEYS:
        return SPECIAL_KEYS[name], "special"
    if re.fullmatch(r"f([1-9]|1[0-2])", name):
        return name.upper(), "special"

    char = keyboard_key_char(key)
    if char is None and len(name) == 1:
        char = name
    if char is None:
        return None
    normalized = normalize_keyboard_char(char)
    if normalized is None:
        return None
    return normalized, "char"


def keyboard_key_id(key: Any) -> str:
    name = keyboard_key_name(key)
    char = keyboard_key_char(key)
    return f"{name}:{char}" if char is not None else name


def keyboard_key_name(key: Any) -> str:
    if isinstance(key, str):
        raw = key
    else:
        raw = getattr(key, "name", None) or str(key)
    raw = raw.replace("Key.", "").replace("'", "").strip()
    return raw.lower()


def keyboard_key_char(key: Any) -> str | None:
    char = getattr(key, "char", None)
    if char is None and isinstance(key, str) and len(key) == 1:
        char = key
    if not isinstance(char, str) or not char:
        return None
    return char


def normalize_keyboard_char(char: str) -> str | None:
    if len(char) != 1:
        return None
    codepoint = ord(char)
    if 1 <= codepoint <= 26:
        return chr(codepoint + 64)
    if char.isalpha():
        return char.upper()
    if char.isdigit():
        return char
    if char.isprintable() and not char.isspace():
        return char
    return None


def sanitize_error(exc: Exception | str) -> str:
    message = str(exc)
    message = re.sub(r"\s+", " ", message).strip()
    if len(message) > ERROR_MESSAGE_LIMIT:
        return f"{message[: ERROR_MESSAGE_LIMIT - 3]}..."
    return message or "Unknown input listener error."
