from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_event_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для раздела "О мероприятии".
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Назад",
        callback_data="start"
    )
    
    builder.adjust(1)
    
    return builder.as_markup() 