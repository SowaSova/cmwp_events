from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from database.models import Expert


def get_experts_keyboard(experts: List[Expert], current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком экспертов и пагинацией.
    
    Args:
        experts: Список экспертов
        current_page: Текущая страница
        total_pages: Общее количество страниц
        
    Returns:
        InlineKeyboardMarkup: Клавиатура со списком экспертов и пагинацией
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с экспертами
    for expert in experts:
        builder.button(
            text=expert.name,
            callback_data=f"expert_{expert.id}"
        )
    
    builder.adjust(1)
    
    # # Если страниц больше одной, добавляем кнопки навигации
    # if total_pages > 1:
    #     navigation_buttons = []
        
    #     # Кнопка "Назад" (если не на первой странице)
    #     if current_page > 1:
    #         navigation_buttons.append(InlineKeyboardButton(
    #             text="◀️",
    #             callback_data=f"experts_page_{current_page - 1}"
    #         ))
    #     else:
    #         # Пустая кнопка, если на первой странице
    #         navigation_buttons.append(InlineKeyboardButton(
    #             text=" ",
    #             callback_data="empty"
    #         ))
        
    #     # Кнопка "Поиск"
    #     navigation_buttons.append(InlineKeyboardButton(
    #         text="Поиск",
    #         callback_data="search_experts"
    #     ))
        
    #     # Кнопка "Вперед" (если не на последней странице)
    #     if current_page < total_pages:
    #         navigation_buttons.append(InlineKeyboardButton(
    #             text="▶️",
    #             callback_data=f"experts_page_{current_page + 1}"
    #         ))
    #     else:
    #         # Пустая кнопка, если на последней странице
    #         navigation_buttons.append(InlineKeyboardButton(
    #             text=" ",
    #             callback_data="empty"
    #         ))
        
    #     # Добавляем строку с кнопками навигации
    #     builder.row(*navigation_buttons)
    # else:
    #     # Если страница всего одна, добавляем только кнопку поиска
    #     builder.row(InlineKeyboardButton(
    #         text="Поиск",
    #         callback_data="search_experts"
    #     ))
    
    # Добавляем кнопку "Назад" в главное меню
    builder.row(InlineKeyboardButton(
        text="🔙",
        callback_data="company"
    ))
    
    return builder.as_markup()


def get_expert_detail_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации об эксперте.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙",
        callback_data="experts"
    )
    
    return builder.as_markup()


def get_expert_detail_with_slider_keyboard(expert_id: int, current_position: int, total_experts: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации об эксперте с кнопками навигации между экспертами.
    
    Args:
        expert_id: ID текущего эксперта
        current_position: Текущая позиция эксперта в списке
        total_experts: Общее количество экспертов
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками навигации и действий
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем слайдер для навигации между экспертами
    navigation_buttons = []
    
    # Кнопка "Назад" (если не на первом эксперте)
    if current_position > 1:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"expert_nav_{current_position - 1}"
        ))
    else:
        # Пустая кнопка, если на первом эксперте
        navigation_buttons.append(InlineKeyboardButton(
            text=" ",
            callback_data="empty"
        ))
    
    # Кнопка с текущей позицией и общим количеством
    navigation_buttons.append(InlineKeyboardButton(
        text=f"{current_position}/{total_experts}",
        callback_data="empty"
    ))
    
    # Кнопка "Вперед" (если не на последнем эксперте)
    if current_position < total_experts:
        navigation_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"expert_nav_{current_position + 1}"
        ))
    else:
        # Пустая кнопка, если на последнем эксперте
        navigation_buttons.append(InlineKeyboardButton(
            text=" ",
            callback_data="empty"
        ))
    
    # Добавляем строку с кнопками навигации
    builder.row(*navigation_buttons)

    builder.button(
        text="✉️ Оставить заявку",
        callback_data=f"ask_expert_{expert_id}"
    )

    builder.button(
        text="🔙",
        callback_data="experts"
    )

    builder.adjust(3, 1, 1)
    
    return builder.as_markup()


def get_expert_search_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для поиска экспертов.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Отмена",
        callback_data="experts"
    )
    
    return builder.as_markup()


def get_expert_search_results_keyboard(experts: List[Expert]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с результатами поиска экспертов.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с экспертами
    for expert in experts:
        builder.button(
            text=expert.name,
            callback_data=f"expert_{expert.id}"
        )

    builder.adjust(1)
    
    # Добавляем кнопку "Назад к списку экспертов"
    builder.row(InlineKeyboardButton(
        text="🔙",
        callback_data="experts"
    ))
    
    return builder.as_markup() 