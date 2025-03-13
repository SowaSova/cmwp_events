# Telegram-бот для мероприятий с экспертами

Телеграм-бот для мероприятий, который позволяет пользователям просматривать информацию об экспертах и задавать им вопросы.

## Функциональность

- Авторизация пользователей через deep link
- Проверка подписки на канал
- Просмотр списка экспертов с пагинацией
- Поиск экспертов по имени
- Просмотр детальной информации об эксперте
- Задание вопросов экспертам
- Навигация между экспертами

## Технологии

- Python 3.10+
- aiogram 3.x
- SQLAlchemy
- PostgreSQL
- Docker и Docker Compose

## Установка и запуск

1. Клонировать репозиторий:

```bash
git clone https://github.com/Flesee/experts-tg-bot.git
cd experts-tg-bot
```

2. Создать файл .env с переменными окружения:

```
BOT_TOKEN=your_bot_token
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=events
POSTGRES_HOST=db
POSTGRES_PORT=5432
CHANNEL_ID=your_channel_id
LINK_HASH=your_link_hash
```

3. Запустить с помощью Docker Compose:

```bash
docker-compose up -d
```

## Структура проекта

- `bot/` - основной код бота
  - `handlers/` - обработчики сообщений и callback-запросов
  - `keyboards/` - клавиатуры для взаимодействия с ботом
  - `database/` - модели и функции для работы с базой данных
  - `utils/` - вспомогательные функции
  - `main.py` - точка входа в приложение
- `docker-compose.yml` - конфигурация Docker Compose
- `Dockerfile` - инструкции для сборки Docker-образа

## Лицензия

MIT
