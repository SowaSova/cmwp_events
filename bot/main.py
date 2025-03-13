import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import main_router
from middlewares import SubscriptionMiddleware
from utils.logger import logger


async def main():
    # Проверка наличия токена
    if not BOT_TOKEN:
        logger.error("Ошибка: BOT_TOKEN не найден в переменных окружения")
        sys.exit(1)
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    
    # Инициализация хранилища состояний
    storage = MemoryStorage()
    
    # Инициализация диспетчера с хранилищем состояний
    dp = Dispatcher(storage=storage)

    # Регистрация middleware
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())
    
    # Регистрация роутеров
    dp.include_router(main_router)
    
    # Запуск бота
    logger.info("✅ Бот запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("⛔️ Бот остановлен")
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        sys.exit(1)