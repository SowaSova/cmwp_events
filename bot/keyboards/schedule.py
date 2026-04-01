from dual_bot import InlineKeyboardMarkup, InlineKeyboardBuilder
from typing import List, Optional

from database.models import Session, Topic, Speaker
from database import get_topic_by_id


def get_schedule_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для раздела "Расписание".
    """
    builder = InlineKeyboardBuilder()
    
    # builder.button(
    #     text="Модератор",
    #     callback_data="moderator"
    # )
    
    builder.button(
        text="Сессии",
        callback_data="sessions"
    )
    
    builder.button(
        text="🔙",
        callback_data="start"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_sessions_keyboard(sessions: List[Session], with_moderator: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком сессий.
    
    Args:
        sessions: Список сессий
        with_moderator: Добавлять ли кнопку Модератор
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками
    """
    builder = InlineKeyboardBuilder()
    
    for session in sessions:
        builder.button(
            text=session.title,
            callback_data=f"session:{session.id}"
        )
    
    # if with_moderator:
    #     builder.button(
    #         text="🙋🏼‍♂️ Модератор",
    #         callback_data="moderator"
    #     )
    
    builder.button(
        text="🔙",
        callback_data="start"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_topics_keyboard(topics: List[Topic], session_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком тем для сессии.
    """
    builder = InlineKeyboardBuilder()
    
    for topic in topics:
        builder.button(
            text=topic.title,
            callback_data=f"topic:{topic.id}"
        )
    
    builder.button(
        text="🔙",
        callback_data="schedule"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_schedule_speakers_keyboard(speakers: List[Speaker], topic_id: int, session_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком спикеров для темы.
    """
    builder = InlineKeyboardBuilder()
    
    for speaker in speakers:
        builder.button(
            text=f"{speaker.name}",
            callback_data=f"schedule_speaker:{speaker.id}:{topic_id}"
        )

    builder.button(text="🔙", callback_data=f"session:{session_id}")
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_schedule_speaker_detail_keyboard(speaker_id: int, topic_id: Optional[int] = None, session_id: Optional[int] = None, is_last: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детальной информации о спикере.
    
    Args:
        speaker_id: ID спикера
        topic_id: ID темы (опционально)
        session_id: ID сессии (опционально)
        is_last: Флаг, указывающий, что это последний спикер в списке
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками
    """
    builder = InlineKeyboardBuilder()

    if topic_id and session_id:
        builder.button(
            text="⁉️ Задать вопрос",
            callback_data=f"ask_question:{speaker_id}:{topic_id}:{session_id}"
        )
    elif topic_id:
        builder.button(
            text="⁉️ Задать вопрос",
            callback_data=f"ask_question:{speaker_id}:{topic_id}"
        )
    else:
        builder.button(
            text="⁉️ Задать вопрос",
            callback_data=f"ask_question:{speaker_id}"
        )
    
    # Добавляем кнопку "Назад" только для последнего спикера
    if is_last:
        builder.button(
            text="🔙",
            callback_data=f"back_to_topic:{topic_id}"
        )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_moderator_keyboard(moderator_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для информации о модераторе.
    
    Args:
        moderator_id: ID модератора (опционально)
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками
    """
    builder = InlineKeyboardBuilder()
    
    if moderator_id:
        builder.button(
            text="⁉️ Задать вопрос",
            callback_data=f"ask_question:{moderator_id}"
        )
    
    builder.button(
        text="🔙",
        callback_data="schedule"
    )
    
    builder.adjust(1)
    
    return builder.as_markup() 