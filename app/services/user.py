from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import User
from app.crud.user import get_user_with_active_language
from app.schemas.user import UserBriefWithLang, UserBrief


async def get_user_profile(
        db: AsyncSession,
        user: User
) -> UserBriefWithLang | UserBrief:
    """
    Get user profile, optionally with active learning language.

    If user has no active learning language, returns basic profile (UserBrief).
    If user has active language, loads it and returns full profile (UserBriefWithLang).

    Args:
        db: Database session
        user: Current user from authentication

    Returns:
        UserBrief: If user has no active learning language
        UserBriefWithLang: If user has active learning language set
    """
    # No active language - return basic profile
    if not user.active_learning_language_id:
         return UserBrief.model_validate(user)

    # Load user with active language relationship
    user_with_lang = await get_user_with_active_language(db, user.id)

    if user_with_lang is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    # Return full profile with language
    return UserBriefWithLang.model_validate(user_with_lang)

