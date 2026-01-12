from typing import Union

from fastapi import APIRouter

from app.api.dependencies import db_dependency, current_active_user_dependency
from app.schemas.user import UserBriefWithLang, UserBrief, UserUpdate
from app.services.user import get_user_profile, update_user_profile

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


@router.patch('/',
              response_model=UserBrief,
              summary='Update user profile')
async def update_user_prof(
        db: db_dependency,
        user: current_active_user_dependency,
        data: UserUpdate
) -> UserBrief:
    """
    Update current user profile fields.

    Allows updating email, name, username, and native language.
    Only provided fields will be updated (partial update).

    Request body (all fields optional):
    - email: New email address (must be unique)
    - name: New full name
    - username: New username (must be unique)
    - native_language: New native language code ()

    Returns:
        UserBrief: Updated user profile

    Raises:
        HTTPException: 409 if email or username already taken
        HTTPException: 400 if invalid data provided
    """
    return await update_user_profile(db, user, data)