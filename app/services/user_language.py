from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_user_by_id, update_active_language
from app.crud.user_language import get_all_user_languages, create_user_language, update_user_language
from app.models import UserLevelLanguage
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

    Optionally sets language as active learning language.

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

    # Set as active learning language if requested
    if data.make_active:
        user = await get_user_by_id(db, user_id)
        await update_active_language(db, user, result.id)

    return result