from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_user_by_id
from app.models import UserLevelLanguage
from app.schemas.enums import LanguageEnum
from app.schemas.user_level_language import UserLanguageLevelUpdate
from app.services.user_language import update_or_create_user_language


async def update_language_by_admin_service(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum,
        data: UserLanguageLevelUpdate
) -> UserLevelLanguage:
    """
    Add or update user's learning language (admin service).

    Validates user existence and delegates to shared create-or-update logic.
    Reuses user language management logic from user service.

    Args:
        db: Database session
        user_id: User ID to modify
        language: Language to add or update
        data: Level and activation settings

    Returns:
        UserLevelLanguage: Created or updated language entry

    Raises:
        HTTPException 404: User not found
        HTTPException 500: Failed to update language
    """
    # Validate user exists
    current_user = await get_user_by_id(db, user_id)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {user_id} not found'
        )

    return await update_or_create_user_language(db, user_id, language, data)