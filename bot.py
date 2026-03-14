import asyncio
import os
import logging
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from converter import convert_to_video_note, MAX_DURATION

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TZ = pytz.timezone(os.getenv("TZ", "Europe/Moscow"))


class MoscowFormatter(logging.Formatter):
    """Formatter с временем по Московскому времени"""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=TZ)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")


handler = logging.StreamHandler()
handler.setFormatter(MoscowFormatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я конвертирую видео в кружочки.\n\n"
        f"📹 Отправь мне видео до {MAX_DURATION // 60} минут, и я верну его кружочком!\n"
        "⚠️ Для длинных видео битрейт автоматически снижается для вписывания в 12 МБ."
    )


@dp.message(F.video)
async def handle_video(message: Message):
    """Обработчик входящих видео"""
    user_id = message.from_user.id
    video = message.video

    duration_str = f"{video.duration // 60}:{video.duration % 60:02d}" if video.duration else "?"
    status_msg = await message.answer(
        f"⏳ Обрабатываю видео ({duration_str}), подождите...\n"
        "🔄 Длинные видео могут обрабатываться дольше."
    )

    input_path = os.path.join(TEMP_DIR, f"{user_id}_input.mp4")
    output_path = os.path.join(TEMP_DIR, f"{user_id}_output.mp4")

    try:
        if video.duration and video.duration > MAX_DURATION:
            await status_msg.edit_text(
                f"❌ Видео слишком длинное: {video.duration // 60}м {video.duration % 60}с.\n"
                f"Максимальная длительность: {MAX_DURATION // 60} минут."
            )
            return

        logger.info(f"Скачиваем видео от пользователя {user_id}")
        file = await bot.get_file(video.file_id)
        await bot.download_file(file.file_path, destination=input_path)

        logger.info(f"Конвертируем видео для пользователя {user_id}")
        success = convert_to_video_note(input_path, output_path)

        if not success:
            await status_msg.edit_text(
                "❌ Ошибка при конвертации.\n"
                "Возможно видео слишком длинное и не влезает в 12 МБ даже с минимальным битрейтом."
            )
            return

        logger.info(f"Отправляем кружочек пользователю {user_id}")
        with open(output_path, "rb") as f:
            video_data = f.read()
        input_file = BufferedInputFile(video_data, filename="circle.mp4")
        await message.answer_video_note(video_note=input_file)
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка. Убедитесь, что:\n"
            f"• Видео не длиннее {MAX_DURATION // 60} минут\n"
            "• Размер файла не превышает 50 МБ (ограничение Bot API)\n"
            "• Формат файла поддерживается (MP4, AVI, MOV)"
        )
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Удалён временный файл: {path}")


@dp.message(F.document)
async def handle_document(message: Message):
    """Обработчик видео, отправленных как документ"""
    mime = message.document.mime_type or ""
    if mime.startswith("video/"):
        await message.answer(
            "⚠️ Вы отправили видео как файл.\n"
            "Пожалуйста, отправьте его как обычное видео (не файл), "
            "чтобы я мог его обработать."
        )
    else:
        await message.answer("❌ Я работаю только с видео файлами.")


async def main():
    logger.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
