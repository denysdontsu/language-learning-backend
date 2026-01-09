from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from  app.models.user_level_language import UserLevelLanguage
from app.schemas.enums import LanguageEnum, LanguageLevelEnum


async def get_language_by_id(
        db: AsyncSession,
        language_level_id: int
) -> UserLevelLanguage | None:
    """
    Get user language entry by ID.

    Args:
        db: Database session
        language_level_id: Language entry ID

    Returns:
        UserLevelLanguage | None: Language entry if found, None otherwise
    """
    return await db.get(UserLevelLanguage, language_level_id)


async def get_all_user_languages(
        db: AsyncSession,
        user_id: int
) -> Sequence[UserLevelLanguage]:
    """
    Get all languages user is learning.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Sequence[UserLevelLanguage]: List of user's language entries
    """
    stmt = select(UserLevelLanguage).where(UserLevelLanguage.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_user_language(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum,
        level: LanguageLevelEnum
) -> UserLevelLanguage:
    """
    Add new language to user's learning list.

    Args:
        db: Database session
        user_id: User ID
        language: Language to add
        level: Initial proficiency level

    Returns:
        UserLevelLanguage: Created language entry
    """
    new_user_language = UserLevelLanguage(
        user_id=user_id,
        language=language,
        level=level
    )
    db.add(new_user_language)
    await db.commit()
    await db.refresh(new_user_language)

    return new_user_language


async def update_user_language(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum,
        level: LanguageLevelEnum
) -> UserLevelLanguage | None:
    """
    Update user's language proficiency level.

    Args:
        db: Database session
        user_id: User ID
        language: Language to update
        level: New proficiency level

    Returns:
        UserLevelLanguage | None: Updated entry or None if not found

    Raises:
        NoResultFound: If language entry doesn't exist
    """
    # Find existing entry
    stmt = select(UserLevelLanguage).where(
        UserLevelLanguage.user_id == user_id,
        UserLevelLanguage.language == language
    )
    result = await db.execute(stmt)
    user_language = result.scalar_one_or_none()

    if not user_language:
        return None

    # Update level
    user_language.level = level
    await db.commit()
    await db.refresh(user_language)

    return user_language


