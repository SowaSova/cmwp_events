import asyncio
import logging
import sys
from dual_bot import Bot, Dispatcher, F

from config import BOT_TOKEN, MAX_BOT_TOKEN, LICENSE_KEY
from handlers import main_router
from middlewares.auth import AuthMiddleware
from middlewares.subscription import SubscriptionMiddleware
from utils.logger import logger
from scheduler import init_scheduler


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout
    )

    # Проверка наличия токена
    if not BOT_TOKEN:
        logger.error("Ошибка: BOT_TOKEN не найден в переменных окружения")
        sys.exit(1)

    if not LICENSE_KEY:
        logger.error("Ошибка: LICENSE_KEY не найден в переменных окружения")
        sys.exit(1)

    # Инициализация бота (Telegram + MAX)
    bot = Bot(
        telegram_token=BOT_TOKEN,
        max_token=MAX_BOT_TOKEN or None,
        parse_mode="HTML",
        license_key=LICENSE_KEY,
    )

    # Инициализация диспетчера
    dp = Dispatcher()

    # Регистрация команд бота через startup hook
    @dp.startup
    async def on_startup():
        if bot.telegram:
            from aiogram.types import BotCommand
            await bot.telegram.set_my_commands([
                BotCommand(command="start", description="Запустить бота")
            ])

    # Регистрация middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    # dp.message.middleware(SubscriptionMiddleware())
    # dp.callback_query.middleware(SubscriptionMiddleware())

    # Настройка фильтра
    dp.message.filter(F.chat.type == "private")
    dp.callback_query.filter(F.message.chat.type == "private")

    # Регистрация роутеров
    dp.include_router(main_router)

    # Инициализация планировщика опросов
    init_scheduler(bot)

    # Запуск бота
    logger.info("✅ Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("⛔️ Бот остановлен")
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
