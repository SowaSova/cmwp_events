from dual_bot import State, StatesGroup


class SpeakerSearch(StatesGroup):
    """Состояния для поиска спикеров"""
    waiting_for_query = State()  # Ожидание ввода запроса поиска
    viewing_speaker = State()  # Просмотр информации о спикере


class ExpertSearch(StatesGroup):
    """Состояния для поиска экспертов"""
    waiting_for_query = State()  # Ожидание ввода запроса поиска
    viewing_expert = State()  # Просмотр информации об эксперте


class AskQuestionStates(StatesGroup):
    """Состояния для процесса задания вопроса"""
    waiting_for_speaker = State()  # Ожидание выбора спикера
    waiting_for_expert = State()   # Ожидание выбора эксперта
    waiting_for_question = State()  # Ожидание ввода вопроса
    waiting_for_name = State()  # Ожидание ввода ФИО
    waiting_for_contacts = State()  # Ожидание ввода контактной информации
    confirm_question = State()  # Подтверждение вопроса 