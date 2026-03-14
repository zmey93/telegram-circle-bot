# 🎥 Telegram Circle Bot

Телеграм-бот, который принимает видео и отправляет его обратно в виде **кружочка** (video note).

## Технологии

- Python 3.12
- [aiogram 3](https://docs.aiogram.dev/) — асинхронный фреймворк для Telegram Bot API
- ffmpeg — конвертация видео в квадратный формат 640×640
- Docker + Docker Compose

## Быстрый старт (одна команда)

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/zmey93/telegram-circle-bot/main/install.sh)"
```

Скрипт автоматически:
- Установит Docker (если не установлен)
- Клонирует репозиторий в `/opt/circlebot`
- Запросит `BOT_TOKEN` от @BotFather
- Соберёт и запустит Docker контейнер
- Зарегистрирует команду `circlebot` в системе

## Управление ботом

```bash
circlebot start      # Запустить бота
circlebot stop       # Остановить бота
circlebot restart    # Перезапустить бота
circlebot update     # Обновить (git pull + пересборка)
circlebot status     # Статус контейнера
circlebot logs       # Просмотр логов в реальном времени
circlebot uninstall  # Полное удаление
```

## Ограничения

| Параметр | Значение |
|----------|----------|
| Макс. длительность | 59 секунд |
| Макс. размер файла | 20 МБ |
| Формат вывода | MP4, 640×640 |

## Структура проекта

```
/opt/circlebot/          ← директория установки
├── bot.py              # Основной файл бота
├── converter.py        # Конвертация через ffmpeg
├── Dockerfile
├── docker-compose.yml
├── install.sh          # Скрипт установки
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
| 2.0.0 | 14.03.2026 | Добавлен Docker + Docker Compose |
| 3.0.0 | 14.03.2026 | Установка в /opt/circlebot, скрипт install.sh, команда circlebot |
