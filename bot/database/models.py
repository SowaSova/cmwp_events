from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, BigInteger, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base

# Определение промежуточной таблицы для связи many-to-many между Topic и Speaker
events_topic_speakers = Table(
    'events_topic_speakers',
    Base.metadata,
    Column('topic_id', Integer, ForeignKey('events_topic.id'), primary_key=True),
    Column('speaker_id', Integer, ForeignKey('events_speaker.id'), primary_key=True)
)

class WelcomeMessage(Base):
    """Модель приветственного сообщения"""
    __tablename__ = 'events_welcomemessage'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WelcomeMessage(id={self.id})>"


class Schedule(Base):
    """Модель расписания"""
    __tablename__ = 'events_schedule'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Schedule(id={self.id})>"


class TelegramUser(Base):
    """Модель пользователя Telegram"""
    __tablename__ = 'events_telegramuser'
    
    telegram_id = Column(BigInteger, primary_key=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    real_name = Column(String(255), nullable=True)
    contacts = Column(String(255), nullable=True)
    is_authorized = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    questions = relationship("Question", back_populates="user", cascade="all, delete-orphan")
    survey_responses = relationship("SurveyResponse", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TelegramUser(telegram_id={self.telegram_id}, full_name={self.full_name})>"


class Speaker(Base):
    """Модель спикера"""
    __tablename__ = 'events_speaker'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    photo = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    is_moderator = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    questions = relationship("Question", back_populates="speaker", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Speaker(id={self.id}, name={self.name})>"


class Expert(Base):
    """Модель эксперта"""
    __tablename__ = 'events_expert'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    photo = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    questions = relationship("Question", back_populates="expert", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Expert(id={self.id}, name={self.name})>"


class Question(Base):
    """Модель вопроса"""
    __tablename__ = 'events_question'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('events_telegramuser.telegram_id'), nullable=False)
    speaker_id = Column(Integer, ForeignKey('events_speaker.id'), nullable=True)
    expert_id = Column(Integer, ForeignKey('events_expert.id'), nullable=True)
    text = Column(Text, nullable=False)
    user_name = Column(String(255), nullable=True)
    is_answered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    user = relationship("TelegramUser", back_populates="questions")
    speaker = relationship("Speaker", back_populates="questions")
    expert = relationship("Expert", back_populates="questions")
    
    def __repr__(self):
        if self.speaker_id:
            return f"<Question(id={self.id}, user_id={self.user_id}, speaker_id={self.speaker_id})>"
        else:
            return f"<Question(id={self.id}, user_id={self.user_id}, expert_id={self.expert_id})>"


class CompanyInfo(Base):
    """Модель информации о компании"""
    __tablename__ = 'events_companyinfo'
    
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    media = Column(String(255), nullable=True)
    media_type = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    links = relationship("CompanyLink", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CompanyInfo(id={self.id})>"


class CompanyLink(Base):
    """Модель ссылки компании"""
    __tablename__ = 'events_companylink'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('events_companyinfo.id'), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    order = Column(Integer, default=0)
    
    # Отношения
    company = relationship("CompanyInfo", back_populates="links")
    
    def __repr__(self):
        return f"<CompanyLink(id={self.id}, title={self.title})>"


class Survey(Base):
    """Модель опроса"""
    __tablename__ = 'events_survey'
    
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    questions = relationship("SurveyQuestion", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("SurveyResponse", back_populates="survey", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Survey(id={self.id})>"


class SurveyQuestion(Base):
    """Модель вопроса опроса"""
    __tablename__ = 'events_surveyquestion'
    
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('events_survey.id'), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    
    # Отношения
    survey = relationship("Survey", back_populates="questions")
    options = relationship("SurveyOption", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SurveyQuestion(id={self.id}, text={self.text[:20]}...)>"


class SurveyOption(Base):
    """Модель варианта ответа на вопрос опроса"""
    __tablename__ = 'events_surveyquestionoption'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('events_surveyquestion.id'), nullable=False)
    text = Column(String(255), nullable=False)
    order = Column(Integer, default=0)
    
    # Отношения
    question = relationship("SurveyQuestion", back_populates="options")
    
    def __repr__(self):
        return f"<SurveyOption(id={self.id}, text={self.text})>"


class SurveyResponse(Base):
    """Модель ответа пользователя на опрос"""
    __tablename__ = 'events_surveyresponse'
    
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('events_survey.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('events_telegramuser.telegram_id'), nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Отношения
    survey = relationship("Survey", back_populates="responses")
    user = relationship("TelegramUser", back_populates="survey_responses")
    option_responses = relationship("SurveyOptionResponse", back_populates="response", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SurveyResponse(id={self.id}, survey_id={self.survey_id}, user_id={self.user_id})>"


class SurveyOptionResponse(Base):
    """Модель выбранного варианта ответа"""
    __tablename__ = 'events_surveyoptionresponse'
    
    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey('events_surveyresponse.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('events_surveyquestion.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('events_surveyquestionoption.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    response = relationship("SurveyResponse", back_populates="option_responses")
    question = relationship("SurveyQuestion")
    selected_option = relationship(
        "SurveyOption",
        primaryjoin="SurveyOptionResponse.selected_option_id == SurveyOption.id"
    )
    
    def __repr__(self):
        return f"<SurveyOptionResponse(id={self.id}, question_id={self.question_id}, selected_option_id={self.selected_option_id})>"


class AfterQuestionText(Base):
    """Модель текста после вопроса"""
    __tablename__ = 'events_afterquestiontext'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AfterQuestionText(id={self.id})>"


class EventInfo(Base):
    """Модель информации о мероприятии"""
    __tablename__ = 'events_eventinfo'
    
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    media = Column(String(255), nullable=True)
    media_type = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EventInfo(id={self.id})>"


class Session(Base):
    """Модель сессии мероприятия"""
    __tablename__ = 'events_session'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    topics = relationship("Topic", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, title={self.title})>"


class Topic(Base):
    """Модель темы в рамках сессии"""
    __tablename__ = 'events_topic'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('events_session.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    session = relationship("Session", back_populates="topics")
    speakers = relationship(
        "Speaker",
        secondary=events_topic_speakers,
        backref="topics"
    )
    
    def __repr__(self):
        return f"<Topic(id={self.id}, title={self.title})>"
