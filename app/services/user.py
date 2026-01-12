from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import User
from app.crud.user import (
    get_user_with_active_language,
    get_user_by_email,
    get_user_by_username,
    update_user)
from app.schemas.user import UserBriefWithLang, UserBrief, UserUpdate


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


async def update_user_profile(
        db: AsyncSession,
        user: User,
        data: UserUpdate
) -> UserBrief:
    """
    Update user profile with validation.

    Args:
        db: Database session
        user: Current user (from authentication)
        data: Fields to update

    Returns:
        UserBrief: Updated user profile

    Raises:
        HTTPException: 409 if email or username already taken
        HTTPException: 400 if invalid data or database constraint violation
        HTTPException: 500 if unknown database error
    """
    # Extract fields
    update_dict = data.model_dump(exclude_unset=True)

    if not update_dict:
        return UserBrief.model_validate(user)

    # Email uniqueness validation
    if 'email' in update_dict:
        existing = await get_user_by_email(db, update_dict['email'])
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Email already registered'
        )
    # Username uniqueness validation
    if 'username' in update_dict:
        existing = await get_user_by_username(db, update_dict['username'])
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Username already taken'
            )
    # Update with error handling
    try:
        result = await update_user(db, user, update_dict)
    except IntegrityError as e:
        await db.rollback()

        # Parse error type
        if 'not null' in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required field cannot be null'
            )
        elif 'unique constraint' in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Value already exists'
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Database error occurred'
            )

    return UserBrief.model_validate(result)