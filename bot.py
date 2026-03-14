import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from converter import convert_to_video_note

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
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
        "📹 Просто отправь мне видео, и я верну его в виде кружочка!"
    )


@dp.message(F.video)
async def handle_video(message: Message):
    """Обработчик входящих видео"""
    user_id = message.from_user.id
    video = message.video

    status_msg = await message.answer("⏳ Обрабатываю видео, подождите...")

    input_path = os.path.join(TEMP_DIR, f"{user_id}_input.mp4")
    output_path = os.path.join(TEMP_DIR, f"{user_id}_output.mp4")

    try:
        logger.info(f"Скачиваем видео от пользователя {user_id}")
        file = await bot.get_file(video.file_id)
        await bot.download_file(file.file_path, destination=input_path)

        logger.info(f"Конвертируем видео для пользователя {user_id}")
        success = convert_to_video_note(input_path, output_path)

        if not success:
            await status_msg.edit_text("❌ Ошибка при конвертации видео. Попробуйте другой файл.")
            return

        logger.info(f"Отправляем кружочек пользователю {user_id}")
        with open(output_path, "rb") as video_file:
            await message.answer_video_note(video_note=video_file)

        await status_msg.delete()

    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка. Убедитесь, что:\n"
            "• Видео не длиннее 59 секунд\n"
            "• Размер файла не превышает 20 МБ\n"
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
