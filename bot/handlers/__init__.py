from aiogram import Router
from .start import start_router
from .speakers import speakers_router
from .experts import experts_router
from .questions import questions_router
from .company import company_router
from .event import event_router
from .schedule import schedule_router
from .surveys import survey_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(speakers_router)
main_router.include_router(experts_router)
main_router.include_router(questions_router)
main_router.include_router(company_router)
main_router.include_router(event_router)
main_router.include_router(schedule_router)
main_router.include_router(survey_router)

__all__ = [
    'main_router',
]
