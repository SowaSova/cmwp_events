from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_to_experts_keyboard(from_expert_view: bool = False, expert_id: int = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад к экспертам" или "Назад к эксперту".
    
    Args:
        from_expert_view: Если True, возвращает к просмотру экспертов, иначе к выбору экспертов для вопроса
        expert_id: ID эксперта, к которому нужно вернуться (если пользователь пришел из просмотра эксперта)
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад к экспертам" или "Назад к эксперту"
    """
    builder = InlineKeyboardBuilder()
    
    if from_expert_view and expert_id:
        # Если пользователь пришел из просмотра эксперта и известен ID эксперта,
        # создаем кнопку для возврата к этому эксперту
        builder.button(
            text="🔙 Назад к эксперту",
            callback_data=f"expert_{expert_id}"
        )
    else:
        builder.button(
            text="🔙 Назад к экспертам",
            callback_data="experts" if from_expert_view else "ask_question_experts"
        )
    
    return builder.as_markup()


def get_skip_name_keyboard(from_expert_view: bool = False, expert_id: int = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Пропустить" и "Назад к экспертам" или "Назад к эксперту".
    
    Args:
        from_expert_view: Если True, возвращает к просмотру экспертов, иначе к выбору экспертов для вопроса
        expert_id: ID эксперта, к которому нужно вернуться (если пользователь пришел из просмотра эксперта)
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Пропустить" и "Назад к экспертам" или "Назад к эксперту"
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Пропустить ➡️",
        callback_data="skip_name"
    )
    
    if from_expert_view and expert_id:
        # Если пользователь пришел из просмотра эксперта и известен ID эксперта,
        # создаем кнопку для возврата к этому эксперту
        builder.button(
            text="🔙 Назад к эксперту",
            callback_data=f"expert_{expert_id}"
        )
    else:
        builder.button(
            text="🔙 Назад к экспертам",
            callback_data="experts" if from_expert_view else "ask_question_experts"
        )
    
    builder.adjust(1)
    return builder.as_markup()


def get_confirm_question_keyboard(from_expert_view: bool = False, expert_id: int = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Готово" и "Назад к экспертам" или "Назад к эксперту".
    
    Args:
        from_expert_view: Если True, возвращает к просмотру экспертов, иначе к выбору экспертов для вопроса
        expert_id: ID эксперта, к которому нужно вернуться (если пользователь пришел из просмотра эксперта)
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Готово" и "Назад к экспертам" или "Назад к эксперту"
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Готово",
        callback_data="confirm_question"
    )
    
    if from_expert_view and expert_id:
        # Если пользователь пришел из просмотра эксперта и известен ID эксперта,
        # создаем кнопку для возврата к этому эксперту
        builder.button(
            text="🔙 Назад к эксперту",
            callback_data=f"expert_{expert_id}"
        )
    else:
        # Иначе создаем кнопку для возврата к списку экспертов
        builder.button(
            text="🔙 Назад к экспертам",
            callback_data="experts" if from_expert_view else "ask_question_experts"
        )
    
    builder.adjust(1)  # Размещаем кнопки в одну колонку
    return builder.as_markup() 