# Standard library
from datetime import date

# Third-party
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

# Models
from app.models import User, UserLevelLanguage

# Schemas
from app.schemas import (
    UserRoleEnum,
    LanguageEnum,
    LanguageLevelEnum
)

async def get_users(
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
        limit: int | None = 50,
        offset: int | None = 0
) -> list[User]:
    """
    Fetch users from database with filtering.

    Excludes the requesting admin from results and eagerly loads
    active learning language relationship when needed.

    Args:
        db: Database session
        admin_id: Admin user ID to exclude from results
        search: Search by email or username
        role: Filter by user role
        native_language: Filter by native language
        active_learning_language: Filter by active learning language
        level: Filter by active language level
        is_active: Filter by account status
        created_after: Filter users created after this datetime
        created_before: Filter users created before this datetime
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List of User models with eagerly loaded active_learning_language

    Note:
        Always joins active_learning_language to allow filtering,
        even if user doesn't have one set (uses outer join)
    """
    stmt = (
        select(User)
        .outerjoin(User.active_learning_language)
        .options(contains_eager(User.active_learning_language))
        .where(User.id != admin_id)
    )

    # Search filter
    if search:
        stmt = stmt.where(
            or_(
                User.email.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%')
            )
        )

    # Filter by active language level
    if level:
        stmt = stmt.where(UserLevelLanguage.level == level)

    # Filter by active learning language
    if active_learning_language:
        stmt = stmt.where(
            UserLevelLanguage.language == active_learning_language
        )

    # Filter by role
    if role:
        stmt = stmt.where(User.role == role)

    # Filter by native language
    if native_language:
        stmt = stmt.where(User.native_language == native_language)

    # Filter by active status
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    # Filter by registration date range
    if created_after:
        stmt = stmt.where(User.created_at >= created_after)

    if created_before:
        stmt = stmt.where(User.created_at <= created_before)

    # Apply pagination
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())