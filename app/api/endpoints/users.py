from typing import Union

from fastapi import APIRouter

from app.api.dependencies import db_dependency, current_active_user_dependency
from app.schemas.user import UserBriefWithLang, UserBrief
from app.services.user import get_user_profile

router = APIRouter(prefix='/users/me', tags=['Users']) # или правильнее User?

@router.get('/',
            response_model= Union[UserBriefWithLang, UserBrief],
            summary='Get current user profile')
async def get_current_user(
        db: db_dependency,
        user: current_active_user_dependency
):
    """
    Get current authenticated user profile.

    Returns user profile with active learning language if set,
    otherwise returns basic profile without language information.

    Response variants:
    - UserBriefWithLang: If user has active learning language
      (includes id, email, username, name, native_language, active_learning_language)
    - UserBrief: If user has no active learning language
      (includes id, email, username, name, native_language)

    Returns:
        UserBriefWithLang | UserBrief: User profile
    """
    return await get_user_profile(db, user)
