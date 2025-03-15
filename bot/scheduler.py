from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
import asyncio
import logging

from utils.logger import logger
from database import get_pending_surveys, mark_survey_as_sent, get_all_users
from handlers.surveys import send_survey_to_users


logging.getLogger('apscheduler').setLevel(logging.CRITICAL)
logging.getLogger('apscheduler.executors').setLevel(logging.CRITICAL)
logging.getLogger('apscheduler.scheduler').setLevel(logging.CRITICAL)


class SurveyScheduler:
    """Класс для планирования отправки опросов"""
    
    def __init__(self, bot: Bot):
        """
        Инициализирует планировщик.
        
        Args:
            bot: Экземпляр бота
        """
        self.bot = bot
        # Отключаем логирование при создании планировщика
        self.scheduler = AsyncIOScheduler(logger=None)
        self.is_running = False
    
    def start(self):
        """Запускает планировщик"""
        if not self.is_running:
            # Добавляем задачу проверки опросов каждую минуту
            self.scheduler.add_job(
                self.check_surveys,
                trigger=IntervalTrigger(seconds=60),
                id='check_surveys',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Планировщик опросов запущен")
    
    def stop(self):
        """Останавливает планировщик"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
    
    async def check_surveys(self):
        """Проверяет опросы, которые нужно отправить"""
        try:
            surveys = await get_pending_surveys()
            
            if not surveys:
                return
            
            users = await get_all_users()
            
            if not users:
                return
            
            for survey in surveys:
                await send_survey_to_users(self.bot, survey.id, users)
                await mark_survey_as_sent(survey.id)
                
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Ошибка при проверке опросов: {e}")


survey_scheduler = None


def init_scheduler(bot: Bot):
    """
    Инициализирует планировщик.
    
    Args:
        bot: Экземпляр бота
    """
    global survey_scheduler
    survey_scheduler = SurveyScheduler(bot)
    survey_scheduler.start() 