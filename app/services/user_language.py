from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_user_by_id, update_active_language
from app.crud.user_language import (
    get_all_user_languages,
    create_user_language,
    update_user_language,
    delete_learning_language)
from app.models import UserLevelLanguage, User
from app.schemas.enums import LanguageEnum, LanguageLevelEnum
from app.schemas.user_level_language import UserLanguageLevelUpdate


async def update_or_create_user_language(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum,
        data: UserLanguageLevelUpdate
) -> UserLevelLanguage:
    """
    Update existing or create new user language entry.

    If language already exists in user's learning list:
    - Updates level if provided in data
    - Returns existing entry if level not provided

    If language doesn't exist:
    - Creates new entry with provided level (defaults to A1)

    Auto-activation behavior:
    - If make_active=True: sets this language as active
    - If no active language exists: sets automatically
    - Otherwise: adds language without activation

    Args:
        db: Database session
        user_id: User ID
        language: Language to add or update
        data: Update data (level, make_active flag)

    Returns:
        UserLevelLanguage: Created or updated language entry
    """
    # Default level to A1 if not provided
    level = data.level if data.level is not None else LanguageLevelEnum.A1

    # Get all user's languages
    user_level_languages = await get_all_user_languages(db, user_id)
    user_languages =[row.language for row in user_level_languages]

    # Create or update language entry
    if language not in user_languages:
        # Create new language entry
        result = await create_user_language(db, user_id, language, level)

    else:
        # Language already exists
        if data.level:
            # Update with new level
            result = await update_user_language(db, user_id, language, data.level)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Failed to update language'
                )
        else:
            # Return existing entry without change
            result = next(
                lang for lang in user_level_languages
                if lang.language == language
            )

    # Set as active if:
        # Explicitly requested (make_active=True)
        # User has no active language (first language)
    user = await get_user_by_id(db, user_id)
    if data.make_active or user.active_learning_language_id is None:
        await update_active_language(db, user, result.id)

    return result


async def delete_user_learning_language(
        db: AsyncSession,
        user: User,
        language: LanguageEnum
) -> None:
    """
    Remove language from user's learning list.

    Validates that:
    - Language exists in user's learning list
    - Language is not the last one
    - Language is not currently active

    Args:
        db: Database session
        user: Current user
        language: Language to remove

    Raises:
        HTTPException: 404 if language not found
        HTTPException: 400 if last language
        HTTPException: 400 if active language
    """
    # Get all user languages
    user_languages = await get_all_user_languages(db, user.id)

    # Find the language to delete
    language_to_delete = next(
        (lang for lang in user_languages if lang.language == language),
        None)
    if not language_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Language {language.value} not found in learning list'
        )

    # Check if last language
    if len(user_languages) == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot remove last language from learning list'
        )

    # Check if active learning language
    if language_to_delete.id == user.active_learning_language_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot remove active learning language. Set another language as active first.'
        )

    await delete_learning_language(db, user.id, language)

