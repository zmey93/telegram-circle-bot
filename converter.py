import subprocess
import os
import logging

logger = logging.getLogger(__name__)

# Лимит Telegram для video note — 12 МБ (12582912 байт)
TELEGRAM_MAX_BYTES = 12 * 1024 * 1024  # 12 MB
MAX_DURATION = 300  # 5 минут


def get_duration(input_path: str) -> float:
    """Получает длительность видео в секундах через ffprobe"""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        return float(result.stdout.decode().strip())
    except ValueError:
        return 0.0


def calculate_bitrate(duration_sec: float, max_bytes: int = TELEGRAM_MAX_BYTES) -> int:
    """
    Вычисляет максимальный видеобитрейт (кбит/с),
    чтобы итоговый файл влез в лимит Telegram.
    Формула: (max_bytes * 8) / duration - audio_bitrate
    """
    audio_kbps = 96  # при длинных видео используем 96 kbps
    overhead = 0.92  # 8% запас на контейнер MP4
    total_kbps = (max_bytes * 8 * overhead) / (duration_sec * 1000)
    video_kbps = int(total_kbps - audio_kbps)
    # Минимум 150 kbps — ниже качество становится неприемлемым
    return max(video_kbps, 150)


def convert_to_video_note(input_path: str, output_path: str) -> bool:
    """
    Конвертирует обычное видео в формат для video note (кружочек).
    - Обрезает до квадрата, масштабирует до 640x640
    - Ограничивает длительность до 5 минут
    - Автоматически рассчитывает битрейт для вписывания в 12 МБ
    """
    try:
        # Определяем длительность исходника
        duration = get_duration(input_path)
        actual_duration = min(duration, MAX_DURATION) if duration > 0 else MAX_DURATION
        logger.info(f"Длительность видео: {duration:.1f}с, будет обработано: {actual_duration:.1f}с")

        # Рассчитываем оптимальный битрейт
        video_kbps = calculate_bitrate(actual_duration)
        logger.info(f"Целевой видеобитрейт: {video_kbps} kbps")

        command = [
            "ffmpeg",
            "-i", input_path,
            "-t", str(int(actual_duration)),
            "-vf",
            "crop=min(iw\\,ih):min(iw\\,ih),scale=640:640",
            "-c:v", "libx264",
            "-preset", "fast",
            "-b:v", f"{video_kbps}k",   # таргетный битрейт
            "-maxrate", f"{video_kbps}k",
            "-bufsize", f"{video_kbps * 2}k",
            "-c:a", "aac",
            "-b:a", "96k",
            "-movflags", "+faststart",
            "-y",
            output_path
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600  # 10 минут таймаут для длинных видео
        )

        if result.returncode != 0:
            logger.error(f"ffmpeg ошибка: {result.stderr.decode()}")
            return False

        # Проверяем итоговый размер
        output_size = os.path.getsize(output_path)
        logger.info(f"Размер выходного файла: {output_size / 1024 / 1024:.2f} МБ")

        if output_size > TELEGRAM_MAX_BYTES:
            logger.warning("Файл всё ещё превышает 12 МБ, возможно видео очень длинное")
            return False

        return True

    except subprocess.TimeoutExpired:
        logger.error("Конвертация превысила 10 минут")
        return False
    except FileNotFoundError:
        raise RuntimeError("Не найден ffmpeg/ffprobe. Убедитесь, что они установлены.")
