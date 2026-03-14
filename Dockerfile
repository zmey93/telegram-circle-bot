# Базовый образ — Python 3.12 slim
FROM python:3.12-slim

# Устанавливаем системные зависимости: ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем requirements сначала (для кэша слоёв Docker)
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Создаём папку для временных файлов
RUN mkdir -p temp

# Запускаем бота
CMD ["python", "bot.py"]
