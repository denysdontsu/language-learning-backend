from datetime import date, datetime, time, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.admin import get_users
from app.crud.user import get_user_with_active_language
from app.models import User
from app.schemas.enums import LanguageEnum, UserRoleEnum, LanguageLevelEnum
from app.schemas.user import UserRead, UserUpdateByAdmin
from app.services.user import update_user_profile


async def get_users_by_admin(
        db: AsyncSession,
        admin_id: int,
        search: str | None,
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
        search: Optional search by email or username
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
        search,
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


async def update_user_by_admin_service(
        db: AsyncSession,
        admin_id: int,
        user_id: int,
        data: UserUpdateByAdmin,
) -> User:
    """
    Update user profile by admin.

    Validates user existence and delegates to shared update logic.
    Handles both regular profile fields and admin-specific fields.

    Args:
        db: Database session
        admin_id: Admin ID performing the update
        user_id: User ID to update
        data: Update data (all fields optional)

    Returns:
        User: Updated User ORM model

    Raises:
        HTTPException 403: Admin cannot modify your own role or active status
        HTTPException 404: User not found
        HTTPException 409: Email/username conflict
        HTTPException 400: Validation error
    """
    # Prevent admin from changing own critical fields
    if admin_id == user_id:
        if data.role is not None or data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Cannot modify your own role or active status'
            )

    # Get user with active language
    current_user = await get_user_with_active_language(db, user_id)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} don't exist"
        )

    # Delegate to shared update logic
    updated_user = await update_user_profile(db, current_user, data)

    return updated_user