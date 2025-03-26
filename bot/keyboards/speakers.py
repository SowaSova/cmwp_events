from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from database.models import Speaker


def get_speakers_keyboard(speakers: List[Speaker], current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком спикеров и пагинацией.
    
    Args:
        speakers: Список спикеров
        current_page: Текущая страница
        total_pages: Общее количество страниц
        
    Returns:
        InlineKeyboardMarkup: Клавиатура со списком спикеров и пагинацией
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки со спикерами
    for speaker in speakers:
        builder.button(
            text=speaker.name,
            callback_data=f"speaker_{speaker.id}"
        )
    
    builder.adjust(1)  # Размещаем кнопки в одну колонку
    
    # # Если страниц больше одной, добавляем кнопки навигации
    # if total_pages > 1:
    #     navigation_buttons = []
        
    #     # Кнопка "Назад" (если не на первой странице)
    #     if current_page > 1:
    #         navigation_buttons.append(InlineKeyboardButton(
    #             text="◀️",
    #             callback_data=f"speakers_page_{current_page - 1}"
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
    #         callback_data="search_speakers"
    #     ))
        
    #     # Кнопка "Вперед" (если не на последней странице)
    #     if current_page < total_pages:
    #         navigation_buttons.append(InlineKeyboardButton(
    #             text="▶️",
    #             callback_data=f"speakers_page_{current_page + 1}"
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
    #         callback_data="search_speakers"
    #     ))
    
    # Добавляем кнопку "Назад" в главное меню
    builder.row(InlineKeyboardButton(
        text="🔙",
        callback_data="start"
    ))
    
    return builder.as_markup()


def get_speaker_detail_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации о спикере.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙",
        callback_data="speakers"
    )
    
    return builder.as_markup()


def get_speaker_detail_with_slider_keyboard(speaker_id: int, current_position: int, total_speakers: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации о спикере с кнопками навигации между спикерами.
    
    Args:
        speaker_id: ID текущего спикера
        current_position: Текущая позиция спикера в списке
        total_speakers: Общее количество спикеров
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками навигации и действий
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем слайдер для навигации между спикерами
    navigation_buttons = []
    
    # Кнопка "Назад" (если не на первом спикере)
    if current_position > 1:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"speaker_nav_{current_position - 1}"
        ))
    else:
        # Пустая кнопка, если на первом спикере
        navigation_buttons.append(InlineKeyboardButton(
            text=" ",
            callback_data="empty"
        ))
    
    # Кнопка с текущей позицией и общим количеством
    navigation_buttons.append(InlineKeyboardButton(
        text=f"{current_position}/{total_speakers}",
        callback_data="empty"
    ))
    
    # Кнопка "Вперед" (если не на последнем спикере)
    if current_position < total_speakers:
        navigation_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"speaker_nav_{current_position + 1}"
        ))
    else:
        # Пустая кнопка, если на последнем спикере
        navigation_buttons.append(InlineKeyboardButton(
            text=" ",
            callback_data="empty"
        ))
    
    # Добавляем строку с кнопками навигации
    builder.row(*navigation_buttons)

    builder.button(
        text="⁉️ Задать вопрос",
        callback_data=f"ask_speaker_{speaker_id}"
    )

    builder.button(
        text="🔙",
        callback_data="speakers"
    )

    builder.adjust(3, 1, 1)
    
    return builder.as_markup()


def get_search_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для поиска спикеров.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Отмена",
        callback_data="speakers"
    )
    
    return builder.as_markup()


def get_search_results_keyboard(speakers: List[Speaker]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с результатами поиска спикеров.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки со спикерами
    for speaker in speakers:
        builder.button(
            text=speaker.name,
            callback_data=f"speaker_{speaker.id}"
        )

    builder.adjust(1)
    
    # Добавляем кнопку "Назад к списку спикеров"
    builder.row(InlineKeyboardButton(
        text="🔙",
        callback_data="speakers"
    ))
    
    return builder.as_markup() 