from datetime import date, datetime, time, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.admin import get_users
from app.schemas.enums import LanguageEnum, UserRoleEnum, LanguageLevelEnum
from app.schemas.user import UserRead


async def get_users_by_admin(
        db: AsyncSession,
        admin_id: int,
        role: UserRoleEnum | None,
        native_language: LanguageEnum | None,
        active_learning_language: LanguageEnum | None,
        level: LanguageLevelEnum | None,
        is_active: bool | None,
        created_after: date | None,
        created_before: date | None,
        pagination: tuple[int, int]
) -> list[UserRead]:
    """
    Get users list with filtering.

    Converts date filters to datetime and delegates to CRUD layer.

    Args:
        db: Database session
        admin_id: Requesting admin ID (excluded from results)
        role: Optional role filter
        native_language: Optional native language filter
        active_learning_language: Optional active learning language filter
        level: Optional level filter (applies to active language)
        is_active: Optional active status filter
        created_after: Optional start date for registration filter
        created_before: Optional end date for registration filter
        pagination: Tuple of (offset, limit)

    Returns:
        List of UserRead schemas with validation
    """
    offset, limit = pagination

    # Convert dates to datetime with UTC timezone
    if created_after:
        created_after = datetime.combine(created_after, time.min, tzinfo=timezone.utc)

    if created_before:
        created_before = datetime.combine(created_before, time.max, tzinfo=timezone.utc)

    users = await get_users(
        db,
        admin_id,
        role,
        native_language,
        active_learning_language,
        level,
        is_active,
        created_after,
        created_before,
        limit,
        offset
    )

    return [UserRead.model_validate(user) for user in users]