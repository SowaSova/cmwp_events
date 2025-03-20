from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CONTACT_SUPPORT_URL, CHANNEL_URL


def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Создает главную клавиатуру с основными разделами.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="О мероприятии",
        callback_data="event_info"
    )

    builder.button(
        text="Расписание",
        callback_data="schedule"
    )
    
    builder.button(
        text="Задать вопрос спикеру",
        callback_data="speakers"
    )
    
    builder.button(
        text="CMWP",
        callback_data="company"
    )

    builder.button(
        text="💬 Чат мероприятия",
        url=CHANNEL_URL
    )

    builder.button(
        text="🆘 Поддержка",
        url=CONTACT_SUPPORT_URL
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад".
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад".
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙 Назад",
        callback_data="start"
    )
    
    return builder.as_markup()


def get_home_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "На главную"
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🏠 На главную",
        callback_data="start"
    )
    
    return builder.as_markup()
    
