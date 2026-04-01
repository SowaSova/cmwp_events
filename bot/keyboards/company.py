from dual_bot import InlineKeyboardMarkup, InlineKeyboardBuilder
from typing import List

from database.models import CompanyLink


def get_company_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для раздела "О компании".
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "О компании" и "Назад"
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="О компании",
        callback_data="company_info"
    )

    builder.button(
        text="Обсудить проект",
        callback_data="experts"
    )
    
    builder.button(
        text="🔙",
        callback_data="start"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_company_info_keyboard(links: List[CompanyLink] = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для информации о компании.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем ссылки компании, если они есть
    if links:
        for link in links:
            builder.button(
                text=link.title,
                url=link.url
            )
    
    # Добавляем кнопку "Назад"
    builder.button(
        text="🔙",
        callback_data="company"
    )
    
    builder.adjust(1)
    
    return builder.as_markup() 
