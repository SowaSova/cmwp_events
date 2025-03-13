from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from database.models import Expert


def get_experts_keyboard(experts: List[Expert], current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком экспертов и пагинацией.
    
    Args:
        experts: Список экспертов для отображения
        current_page: Текущая страница пагинации
        total_pages: Общее количество страниц
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками экспертов и пагинацией
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с экспертами
    for expert in experts:
        builder.button(
            text=expert.name,
            callback_data=f"expert_{expert.id}"
        )
    
    # Размещаем кнопки в одну колонку
    builder.adjust(1)
    
    # Добавляем кнопки пагинации, если страниц больше одной
    if total_pages > 1:
        navigation_buttons = []
        
        # Кнопка "Назад" (если не на первой странице)
        if current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="◀️",
                callback_data=f"experts_page_{current_page - 1}"
            ))
        else:
            # Пустая кнопка, если на первой странице
            navigation_buttons.append(InlineKeyboardButton(
                text=" ",
                callback_data="empty"
            ))
        
        # Кнопка поиска (в центре)
        navigation_buttons.append(InlineKeyboardButton(
            text="🔍 Поиск",
            callback_data="search_experts"
        ))
        
        # Кнопка "Вперед" (если не на последней странице)
        if current_page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(
                text="▶️",
                callback_data=f"experts_page_{current_page + 1}"
            ))
        else:
            # Пустая кнопка, если на последней странице
            navigation_buttons.append(InlineKeyboardButton(
                text=" ",
                callback_data="empty"
            ))
        
        # Добавляем строку с кнопками навигации
        builder.row(*navigation_buttons)
    else:
        # Если всего одна страница, добавляем только кнопку поиска
        builder.row(InlineKeyboardButton(
            text="🔍 Поиск",
            callback_data="search_experts"
        ))

    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="start"
    ))
    
    return builder.as_markup()


def get_expert_detail_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации об эксперте.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔙 Назад к списку экспертов",
        callback_data="experts"
    )
    
    return builder.as_markup()


def get_expert_detail_with_slider_keyboard(expert_id: int, current_position: int, total_experts: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации об эксперте с слайдером для навигации.
    
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
    
    # Добавляем кнопку "Задать вопрос"
    builder.button(
        text="✏️ Задать вопрос",
        callback_data=f"ask_expert_{expert_id}"
    )
    
    # Добавляем кнопку "Назад к списку экспертов"
    builder.button(
        text="🔙 Назад к списку экспертов",
        callback_data="experts"
    )
    
    # Размещаем кнопки: первая строка - 3 кнопки навигации, остальные - по 1 кнопке
    builder.adjust(3, 1, 1)
    
    return builder.as_markup()


def get_search_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для поиска экспертов.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❌ Отмена",
        callback_data="experts"
    )
    
    return builder.as_markup()

def get_ask_search_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для поиска экспертов при задании вопроса.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❌ Отмена",
        callback_data="ask_question"
    )

    return builder.as_markup()


def get_search_results_keyboard(experts: List[Expert]) -> InlineKeyboardMarkup:
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
        text="🔙 Назад к списку экспертов",
        callback_data="experts"
    ))
    
    return builder.as_markup()


def get_ask_experts_keyboard(experts: List[Expert], current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком экспертов для задания вопроса и пагинацией.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с экспертами
    for expert in experts:
        builder.button(
            text=expert.name,
            callback_data=f"ask_expert_{expert.id}"
        )

    builder.adjust(1)

    if total_pages > 1:
        navigation_buttons = []

        if current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="◀️",
                callback_data=f"ask_experts_page_{current_page - 1}"
            ))
        else:
            navigation_buttons.append(InlineKeyboardButton(
                text=" ",
                callback_data="empty"
            ))

        navigation_buttons.append(InlineKeyboardButton(
            text="🔍 Поиск",
            callback_data="ask_search_experts"
        ))

        if current_page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(
                text="▶️",
                callback_data=f"ask_experts_page_{current_page + 1}"
            ))
        else:
            navigation_buttons.append(InlineKeyboardButton(
                text=" ",
                callback_data="empty"
            ))

        builder.row(*navigation_buttons)
    else:
        builder.row(InlineKeyboardButton(
            text="🔍 Поиск",
            callback_data="ask_search_experts"
        ))

    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="start"
    ))
    
    return builder.as_markup()


def get_ask_search_results_keyboard(experts: List[Expert]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с результатами поиска экспертов для задания вопроса.
    """
    builder = InlineKeyboardBuilder()

    for expert in experts:
        builder.button(
            text=expert.name,
            callback_data=f"ask_expert_{expert.id}"
        )

    builder.button(
        text="🔙 Назад к списку экспертов",
        callback_data="ask_question_experts"
    )

    builder.adjust(1)
    
    return builder.as_markup() 