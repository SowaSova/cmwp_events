from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_to_speakers_keyboard(from_speaker_view: bool = False, speaker_id: int = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад к списку спикеров" или "Назад к спикеру".
    
    Args:
        from_speaker_view: Флаг, указывающий, что пользователь пришел из просмотра спикера
        speaker_id: ID спикера (если from_speaker_view=True)
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад"
    """
    builder = InlineKeyboardBuilder()
    
    if from_speaker_view and speaker_id:
        # Если пользователь пришел из просмотра спикера, добавляем кнопку "Назад к спикеру"
        builder.button(
            text="🔙",
            callback_data=f"speaker_{speaker_id}"
        )
    else:
        # Иначе добавляем кнопку "Назад к списку спикеров"
        builder.button(
            text="🔙",
            callback_data="speakers"
        )
    
    return builder.as_markup()


def get_back_to_experts_keyboard(from_expert_view: bool = False, expert_id: int = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад к списку экспертов" или "Назад к эксперту".
    
    Args:
        from_expert_view: Флаг, указывающий, что пользователь пришел из просмотра эксперта
        expert_id: ID эксперта (если from_expert_view=True)
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад"
    """
    builder = InlineKeyboardBuilder()
    
    if from_expert_view and expert_id:
        # Если пользователь пришел из просмотра эксперта, добавляем кнопку "Назад к эксперту"
        builder.button(
            text="🔙",
            callback_data=f"expert_{expert_id}"
        )
    else:
        # Иначе добавляем кнопку "Назад к списку экспертов"
        builder.button(
            text="🔙",
            callback_data="experts"
        )
    
    return builder.as_markup()


def get_skip_name_keyboard(from_speaker_view: bool = False, recipient_id: int = None, is_expert: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Пропустить" для ввода ФИО.
    
    Args:
        from_speaker_view: Флаг, указывающий, что пользователь пришел из просмотра спикера/эксперта
        recipient_id: ID спикера/эксперта
        is_expert: Флаг, указывающий, что recipient_id относится к эксперту
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Пропустить" и "Отмена"
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Пропустить",
        callback_data="skip_name"
    )
    
    if is_expert:
        if from_speaker_view and recipient_id:
            builder.button(
                text="Отмена",
                callback_data=f"expert_{recipient_id}"
            )
        else:
            builder.button(
                text="Отмена",
                callback_data="experts"
            )
    else:
        if from_speaker_view and recipient_id:
            builder.button(
                text="Отмена",
                callback_data=f"speaker_{recipient_id}"
            )
        else:
            builder.button(
                text="Отмена",
                callback_data="speakers"
            )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_skip_contacts_keyboard(from_speaker_view: bool = False, recipient_id: int = None, is_expert: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Пропустить" для ввода контактной информации.
    
    Args:
        from_speaker_view: Флаг, указывающий, что пользователь пришел из просмотра спикера/эксперта
        recipient_id: ID спикера/эксперта
        is_expert: Флаг, указывающий, что recipient_id относится к эксперту
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Пропустить" и "Отмена"
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Пропустить",
        callback_data="skip_contacts"
    )
    
    if is_expert:
        if from_speaker_view and recipient_id:
            builder.button(
                text="Отмена",
                callback_data=f"expert_{recipient_id}"
            )
        else:
            builder.button(
                text="Отмена",
                callback_data="experts"
            )
    else:
        if from_speaker_view and recipient_id:
            builder.button(
                text="Отмена",
                callback_data=f"speaker_{recipient_id}"
            )
        else:
            builder.button(
                text="Отмена",
                callback_data="speakers"
            )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_confirm_question_keyboard(from_speaker_view: bool = False, recipient_id: int = None, is_expert: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения вопроса.
    
    Args:
        from_speaker_view: Флаг, указывающий, что пользователь пришел из просмотра спикера/эксперта
        recipient_id: ID спикера/эксперта
        is_expert: Флаг, указывающий, что recipient_id относится к эксперту
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Отправить" и "Отмена"
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Отправить",
        callback_data="confirm_question"
    )
    
    if is_expert:
        if from_speaker_view and recipient_id:
            builder.button(
                text="Отмена",
                callback_data=f"expert_{recipient_id}"
            )
        else:
            builder.button(
                text="Отмена",
                callback_data="experts"
            )
    else:
        if from_speaker_view and recipient_id:
            builder.button(
                text="Отмена",
                callback_data=f"speaker_{recipient_id}"
            )
        else:
            builder.button(
                text="Отмена",
                callback_data="speakers"
            )
    
    builder.adjust(1)
    
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой отмены.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Отмена".
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙",
        callback_data="cancel_question"
    )
    
    return builder.as_markup()


def get_home_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой возврата на главную страницу.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "На главную".
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="На главную",
        callback_data="start"
    )
    
    return builder.as_markup() 