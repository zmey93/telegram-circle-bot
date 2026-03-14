import subprocess
import os


def convert_to_video_note(input_path: str, output_path: str) -> bool:
    """
    Конвертирует обычное видео в формат для video note (кружочек).
    - Обрезает до квадрата (crop)
    - Масштабирует до 640x640
    - Ограничивает длительность до 59 секунд
    """
    try:
        command = [
            "ffmpeg",
            "-i", input_path,
            "-t", "59",
            "-vf",
            "crop=min(iw\\,ih):min(iw\\,ih),scale=640:640",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-y",
            output_path
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        raise RuntimeError("ffmpeg не найден. Убедитесь, что ffmpeg установлен и добавлен в PATH.")
