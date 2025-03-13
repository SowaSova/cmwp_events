from aiogram.fsm.state import State, StatesGroup


class ExpertSearch(StatesGroup):
    """Состояния для поиска экспертов"""
    waiting_for_query = State()
    viewing_expert = State()  # Состояние просмотра информации об эксперте


class AskQuestionStates(StatesGroup):
    """Состояния для процесса задания вопроса"""
    waiting_for_expert = State()  # Ожидание выбора эксперта
    waiting_for_question = State()  # Ожидание ввода вопроса
    waiting_for_name = State()  # Ожидание ввода ФИО
    confirm_question = State()  # Подтверждение вопроса 