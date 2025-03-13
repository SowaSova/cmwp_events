#!/bin/bash

# Создаем директории для логов и медиа-файлов
mkdir -p /app/logs
mkdir -p /app/media/experts

# Проверяем, существует ли файл wsgi.py
if [ ! -f /app/events_admin/wsgi.py ]; then
    echo "Инициализация Django проекта..."
    django-admin startproject events_admin .
    echo "Django проект успешно инициализирован!"
else
    echo "Django проект уже существует, пропускаем инициализацию."
fi

# Функция для проверки доступности базы данных
wait_for_db() {
    echo "Ожидание готовности базы данных..."
    while ! python << END
import sys
import os
import psycopg2
try:
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'events_db'),
        user=os.environ.get('DB_USER', 'events'),
        password=os.environ.get('DB_PASSWORD', 'events_password'),
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432')
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
    do
        echo "База данных недоступна, ожидание..."
        sleep 1
    done
    echo "База данных готова!"
}

# Ждем готовности базы данных перед применением миграций
wait_for_db

# Создаем директорию для миграций, если её нет
mkdir -p /app/events/migrations

# Применяем миграции
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Создаем суперпользователя, если его нет
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser --noinput || echo "Суперпользователь уже существует"
fi

# Создаем директории для статических файлов, если их нет
mkdir -p /app/static
mkdir -p /app/media

# Собираем статические файлы
python manage.py collectstatic --noinput --clear

# Запускаем Gunicorn для продакшена
echo "Запуск Gunicorn..."
exec gunicorn events_admin.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-file=/app/logs/gunicorn.log --access-logfile=/app/logs/access.log 