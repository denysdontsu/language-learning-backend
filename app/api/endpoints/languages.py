from fastapi import APIRouter, status

from app.api.dependencies import (
    db_dependency,
    current_active_user_dependency)
from app.crud.user_language import get_all_user_languages
from app.schemas.enums import LanguageEnum
from app.schemas.user_level_language import UserLanguageLevelUpdate, UserLanguageBrief
from app.services.user_language import (
    update_or_create_user_language,
    delete_user_learning_language)

router = APIRouter(prefix='/users/me/languages', tags=['Languages'])


@router.get('/',
            response_model=list[UserLanguageBrief],
            summary="Get user's learning languages")
async def get_learning_languages(
        db: db_dependency,
        user: current_active_user_dependency
):
    """
    Get all languages user is currently learning.

    Returns empty list if user has no learning languages yet.

    Returns:
        list[UserLanguageBrief]: List of languages with proficiency levels (may be empty)
    """
    languages = await get_all_user_languages(db, user.id)

    return languages


@router.post(
    '/{language}',
    status_code=status.HTTP_201_CREATED,
    response_model=UserLanguageBrief,
    summary="Add or update learning language"
)
async def update_or_create_language(
        db: db_dependency,
        user: current_active_user_dependency,
        language: LanguageEnum,
        data: UserLanguageLevelUpdate
):
    """
    Add new language to learning list or update existing one.

    If language already in learning list:
    - Updates proficiency level if provided
    - Returns existing entry if level not provided

    If language not in learning list:
    - Adds language with specified level (defaults to A1)

    Can optionally set language as active learning language.

    Args:
        db: Database session dependency
        user: Currently authenticated and active user
        language: Language code to add/update (path parameter)
        data: Update data (level, make_active flag)

    Returns:
        UserLanguageBrief: Created or updated language entry (201 Created)
    """
    return await update_or_create_user_language(
        db,
        user.id,
        language,
        data
    )


@router.delete(
    '/{language}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Remove language from learning list')
async def delete_user_language(
        db: db_dependency,
        user: current_active_user_dependency,
        language: LanguageEnum
) -> None:
    """
    Remove language from user's learning list.

    Cannot remove:
    - Last language in learning list
    - Currently active learning language

    To remove active language, first set another language as active,
    then remove the desired language.

    Path parameters:
        language: Language code to remove (ISO 639-1)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if language not in learning list
        HTTPException: 400 if trying to remove last language
        HTTPException: 400 if trying to remove active language
    """
    await delete_user_learning_language(db, user, language)
    return None