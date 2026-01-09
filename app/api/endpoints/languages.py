from fastapi import APIRouter

from app.api.dependencies import (
    db_dependency,
    user_active_language_dependency)
from app.crud.user_language import get_all_user_languages
from app.schemas.user_level_language import UserLanguageBrief

router = APIRouter(prefix='/users/me/languages', tags=['Languages'])


@router.get('/',
            response_model=list[UserLanguageBrief],
            summary="Get user's learning languages")
async def get_learning_languages(
        db: db_dependency,
        user: user_active_language_dependency
):
    """
    Get all languages user is currently learning.

    Returns empty list if user has no learning languages yet.
    Requires user to have at least one active learning language.

    Returns:
        list[UserLanguageBrief]: List of languages with proficiency levels
    """
    languages = await get_all_user_languages(db, user.id)

    return languages