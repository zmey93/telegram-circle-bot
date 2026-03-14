# 🎥 Telegram Circle Bot

Телеграм-бот, который принимает видео и отправляет его обратно в виде **кружочка** (video note).

## Технологии

- Python 3.12
- [aiogram 3](https://docs.aiogram.dev/) — асинхронный фреймворк для Telegram Bot API
- ffmpeg — конвертация видео в квадратный формат 640×640
- Docker + Docker Compose

## Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/zmey93/telegram-circle-bot.git
cd telegram-circle-bot
```

### 2. Создай файл `.env`

```env
BOT_TOKEN=твой_токен_от_BotFather
```

### 3. Запусти через Docker Compose

```bash
docker compose up -d --build
```

### 4. Проверь логи

```bash
docker compose logs -f bot
```

## Использование

1. Найди бота в Telegram
2. Отправь команду `/start`
3. Отправь любое видео
4. Получи кружочек 🎉

## Ограничения

| Параметр | Значение |
|----------|----------|
| Макс. длительность | 59 секунд |
| Макс. размер файла | 20 МБ |
| Формат вывода | MP4, 640×640 |

## Структура проекта

```
telegram-circle-bot/
├── bot.py              # Основной файл бота
├── converter.py        # Конвертация через ffmpeg
├── Dockerfile
├── docker-compose.yml
├── .env                # Токен (не коммитить!)
├── .env.example
├── .dockerignore
├── requirements.txt
└── temp/               # Временные файлы (создаётся автоматически)
```

## История изменений

| Версия | Дата | Описание |
|--------|------|----------|
| 1.0.0 | 14.03.2026 | Первоначальный релиз |
