from fastapi import APIRouter
from . import (
    auth,
    exercises,
    languages,
    statistics,
    user_exercise_history,
    users
)
from .admin import router as admin_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix='/auth', tags=['Authentication'])
api_router.include_router(users.router, prefix='/users/me', tags=['Users'])
api_router.include_router(languages.router, prefix='/users/me/languages', tags=['Languages'])
api_router.include_router(exercises.router, prefix='/exercises', tags=['Exercises'])
api_router.include_router(user_exercise_history.router, prefix='/history', tags=['History'])
api_router.include_router(statistics.router, prefix='/users/me/statistics', tags=['Statistics'])

# Admin routes (already has /admin prefix from admin/__init__.py)
api_router.include_router(admin_router)

__all__ = ['api_router']