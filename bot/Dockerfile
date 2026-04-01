FROM python:3.12-slim

WORKDIR /app

# Установка необходимых зависимостей для компиляции
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Настройка временной зоны
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Установка зависимостей
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка dual_bot из dist/
COPY dist/ /dist
RUN pip install --no-cache-dir /dist

# Копирование проекта
COPY bot/ .

# Запуск бота
CMD ["python", "main.py"] 