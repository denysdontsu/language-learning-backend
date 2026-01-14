from typing import Union

from fastapi import APIRouter, status, Request

from app.api.dependencies import db_dependency, current_active_user_dependency, limiter
from app.schemas.user import (
    UserBriefWithLang,
    UserBrief,
    UserUpdate,
    UserChangePassword)
from app.services.user import (
    get_user_profile,
    update_user_profile,
    change_password)

router = APIRouter(prefix='/users/me', tags=['Users'])

@router.get('/',
            response_model= Union[UserBriefWithLang, UserBrief],
            summary='Get current user profile')
async def get_current_user(
        db: db_dependency,
        user: current_active_user_dependency
) -> Union[UserBriefWithLang, UserBrief]:
    """
    Get current authenticated user profile.

    Returns user profile with active learning language if set,
    otherwise returns basic profile without language information.

    Response variants:
    - UserBriefWithLang: If user has active learning language
      (includes id, email, username, name, native_language, active_learning_language)
    - UserBrief: If user has no active learning language
      (includes id, email, username, name, native_language)

    Returns:
        UserBriefWithLang | UserBrief: User profile
    """
    user_orm = await get_user_profile(db, user)

    # Conditional serialization based on active language presence
    if user_orm.active_learning_language_id:
        return UserBriefWithLang.model_validate(user_orm)
    else:
        return UserBrief.model_validate(user_orm)


@router.patch('/',
              response_model=UserBrief,
              summary='Update user profile')
async def update_user_prof(
        db: db_dependency,
        user: current_active_user_dependency,
        data: UserUpdate
) -> UserBrief:
    """
    Update current user profile fields.

    Allows updating email, name, username, and native language.
    Only provided fields will be updated (partial update).

    Request body (all fields optional):
    - email: New email address (must be unique)
    - name: New full name
    - username: New username (must be unique)
    - native_language: New native language code ()

    Returns:
        UserBrief: Updated user profile

    Raises:
        HTTPException: 409 if email or username already taken
        HTTPException: 400 if invalid data provided
    """
    user_orm = await update_user_profile(db, user, data)
    return UserBrief.model_validate(user_orm)


@router.patch('/password',
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Change user password')
@limiter.limit("5/hour")
async def change_user_password(
        request: Request,
        db: db_dependency,
        user: current_active_user_dependency,
        password_data: UserChangePassword
) -> None:
    """
    Change current user password.

    Requires old password verification. New password must be different
    from old password and meet security requirements.

    Rate limit: 5 attempts per hour per IP address to prevent brute-force attacks.

    Request body:
    - old_password: Current password for verification
    - new_password: New password (min 8 chars, letter + digit)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 400 if old password incorrect
        HTTPException: 400 if new password same as old
        HTTPException: 429 if rate limit exceeded
    """
    await change_password(db, user, password_data)
    return None