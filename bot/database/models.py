from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


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
    is_authorized = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    questions = relationship("Question", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TelegramUser(telegram_id={self.telegram_id}, username={self.username})>"


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
    expert_id = Column(Integer, ForeignKey('events_expert.id'), nullable=False)
    text = Column(Text, nullable=False)
    user_name = Column(String(255), nullable=True)
    is_answered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    user = relationship("TelegramUser", back_populates="questions")
    expert = relationship("Expert", back_populates="questions")
    
    def __repr__(self):
        return f"<Question(id={self.id}, user_id={self.user_id}, expert_id={self.expert_id})>"
