from aiogram import Router
from .start import start_router
from .schedule import schedule_router
from .experts import experts_router
from .questions import questions_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(schedule_router)
main_router.include_router(experts_router)
main_router.include_router(questions_router)

__all__ = [
    'main_router',
]
