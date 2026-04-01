from dual_bot import InlineKeyboardMarkup, InlineKeyboardBuilder


def get_event_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для раздела "О мероприятии".
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔙",
        callback_data="start"
    )
    
    builder.adjust(1)
    
    return builder.as_markup() 