from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CHANNEL_URL


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для проверки подписки.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Зайти в группу", url=CHANNEL_URL)
    builder.button(text="Проверить подписку", callback_data="check_subscription")

    builder.adjust(1)
    
    return builder.as_markup() 