from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from . import config
from .utils import timestamp_for_filename


logger = logging.getLogger(__name__)

VIDEO_SUFFIXES = {".mp4", ".avi", ".mkv", ".webm"}
AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}


class VideoMuxerError(RuntimeError):
    pass


class VideoMuxerValidationError(VideoMuxerError):
    pass


class VideoMuxerDependencyError(VideoMuxerError):
    pass


class VideoMuxer:
    def __init__(self, recordings_dir: Path | None = None) -> None:
        self.recordings_dir = recordings_dir or config.RECORDINGS_DIR

    def merge(
        self,
        *,
        video_file: str,
        mic_audio_file: str | None = None,
        system_audio_file: str | None = None,
    ) -> dict[str, Any]:
        video_path = self.resolve_recording_file(video_file, VIDEO_SUFFIXES)
        audio_paths = self.resolve_audio_files(mic_audio_file, system_audio_file)
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise VideoMuxerDependencyError("FFmpeg не найден. Установите FFmpeg или добавьте его в PATH.")

        output_path = self.next_output_path(video_path)
        command = self.build_ffmpeg_command(ffmpeg_path, video_path, audio_paths, output_path)
        logger.info("Starting video mux: video=%s audio=%s output=%s", video_path.name, [item.name for item in audio_paths], output_path.name)

        try:
            completed = subprocess.run(
                command,
                cwd=str(self.recordings_dir),
                capture_output=True,
                text=True,
                timeout=60 * 60,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            output_path.unlink(missing_ok=True)
            raise VideoMuxerError("Не удалось собрать видео: FFmpeg не завершился вовремя.") from exc
        except OSError as exc:
            output_path.unlink(missing_ok=True)
            raise VideoMuxerError(f"Не удалось собрать видео: {exc}") from exc

        if completed.returncode != 0:
            output_path.unlink(missing_ok=True)
            details = (completed.stderr or completed.stdout or "").strip()
            raise VideoMuxerError(f"Не удалось собрать видео: {details or 'FFmpeg завершился с ошибкой.'}")

        if not output_path.is_file() or output_path.stat().st_size == 0:
            output_path.unlink(missing_ok=True)
            raise VideoMuxerError("Не удалось собрать видео: выходной файл не был создан.")

        return {
            "status": "completed",
            "output_file": output_path.name,
            "output_path": str(output_path),
        }

    def resolve_audio_files(self, mic_audio_file: str | None, system_audio_file: str | None) -> list[Path]:
        audio_paths: list[Path] = []
        if mic_audio_file:
            audio_paths.append(self.resolve_recording_file(mic_audio_file, AUDIO_SUFFIXES))
        if system_audio_file:
            audio_paths.append(self.resolve_recording_file(system_audio_file, AUDIO_SUFFIXES))
        if not audio_paths:
            raise VideoMuxerValidationError("Выберите хотя бы один аудиофайл для объединения.")
        return audio_paths

    def resolve_recording_file(self, file_name: str | None, allowed_suffixes: set[str]) -> Path:
        requested_name = (file_name or "").strip()
        requested_path = Path(requested_name)
        if not requested_name or requested_name != requested_path.name or ":" in requested_name:
            raise VideoMuxerValidationError("Некорректный выбор файла.")

        path = (self.recordings_dir / requested_name).resolve()
        recordings_dir = self.recordings_dir.resolve()
        try:
            is_inside = path.is_relative_to(recordings_dir)
        except AttributeError:
            is_inside = recordings_dir == path or recordings_dir in path.parents
        if not is_inside:
            raise VideoMuxerValidationError("Некорректный выбор файла.")
        if not path.is_file():
            raise VideoMuxerValidationError("Файл не найден.")
        if path.suffix.lower() not in allowed_suffixes:
            raise VideoMuxerValidationError("Некорректный выбор файла.")
        return path

    def next_output_path(self, video_path: Path) -> Path:
        timestamp = timestamp_for_filename()
        source_stem = video_path.stem
        prefix = f"merged_{source_stem}_{timestamp}"
        output_path = self.recordings_dir / f"{prefix}.mp4"
        counter = 2
        while output_path.exists():
            output_path = self.recordings_dir / f"{prefix}_{counter}.mp4"
            counter += 1
        return output_path

    def build_ffmpeg_command(
        self,
        ffmpeg_path: str,
        video_path: Path,
        audio_paths: list[Path],
        output_path: Path,
    ) -> list[str]:
        if len(audio_paths) == 1:
            return [
                ffmpeg_path,
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_paths[0]),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(output_path),
            ]

        if len(audio_paths) == 2:
            return [
                ffmpeg_path,
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_paths[0]),
                "-i",
                str(audio_paths[1]),
                "-filter_complex",
                "[1:a][2:a]amix=inputs=2:duration=longest:normalize=0[a]",
                "-map",
                "0:v:0",
                "-map",
                "[a]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(output_path),
            ]

        raise VideoMuxerValidationError("Выберите один или два аудиофайла для объединения.")
