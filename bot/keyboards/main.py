from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CONTACT_SUPPORT_URL


def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для главного меню.
    """

    builder = InlineKeyboardBuilder()

    builder.button(text="💬 Задать вопрос", callback_data="ask_question")
    builder.button(text="👨‍🏫 Эксперты", callback_data="experts")
    builder.button(text="📅 Расписание", callback_data="schedule")
    builder.button(text="🆘 Поддержка", url=CONTACT_SUPPORT_URL)

    builder.adjust(1)

    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад".
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔙 Назад", callback_data="start")
    
    return builder.as_markup()
