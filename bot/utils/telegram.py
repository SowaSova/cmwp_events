from aiogram import Bot
from config import CHANNEL_ID
from .logger import logger


async def check_user_subscription(bot: Bot, user_id: int) -> bool:
    """
    Проверяет, подписан ли пользователь на канал.
    """
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        allowed_statuses = ['member', 'administrator', 'creator']
        is_subscribed = member.status in allowed_statuses
        return is_subscribed
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки пользователя {user_id}: {e}")
        return False

