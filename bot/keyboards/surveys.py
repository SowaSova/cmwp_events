from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from database.models import SurveyOption


def get_start_survey_keyboard(survey_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для начала опроса.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📝 Пройти опрос",
        callback_data=f"start_survey:{survey_id}"
    )
    
    return builder.as_markup()


def get_survey_options_keyboard(options: List[SurveyOption], question_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с вариантами ответов на вопрос.
    """
    builder = InlineKeyboardBuilder()
    
    for option in options:
        builder.button(
            text=option.text,
            callback_data=f"survey_option:{question_id}:{option.id}"
        )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_survey_completed_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для завершения опроса.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙 Вернуться в главное меню",
        callback_data="start"
    )
    
    return builder.as_markup() 