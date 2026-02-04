from datetime import date

from fastapi import APIRouter, Query, HTTPException, status

from app.api.dependencies import db_dependency, current_admin_dependency, pagination_dependency
from app.crud.admin import create_exercise
from app.crud.user import get_user_with_active_language
from app.schemas.enums import LanguageEnum, UserRoleEnum, LanguageLevelEnum
from app.schemas.exercise import ExerciseRead, ExerciseCreate
from app.schemas.user import UserRead, UserUpdateByAdmin
from app.schemas.user_level_language import UserLanguageLevelUpdate, UserLanguageBrief
from app.services.admin import (
    get_users_by_admin,
    update_user_by_admin_service,
    update_language_by_admin_service
)

router = APIRouter(prefix='/admin', tags=['Admin'])

@router.get('/users',
            response_model=list[UserRead],
            summary='Get users list with filters')
async def get_users_endpoint(
        db: db_dependency,
        admin: current_admin_dependency,
        pagination: pagination_dependency,

        # Filters
        search: str | None = Query(None,
            description='Search by email or username'),
        role: UserRoleEnum = Query(None,
            description='Filter by user role'),
        native_language: LanguageEnum = Query(None,
            description='Filter by native language'),
        active_learning_language: LanguageEnum = Query(None,
            description='Filter by active learning language'),
        level: LanguageLevelEnum = Query(None,
            description='Filter by active language level'),
        is_active: bool = Query(None,
            description='Filter by active status'),
        created_after: date = Query(None,
            description='Filter users registered after date (YYYY-MM-DD, inclusive)'),
        created_before: date = Query(None,
            description='Filter users registered before date (YYYY-MM-DD, inclusive)')
) -> list[UserRead]:
    """
    Get paginated list of users with optional filters.

    Admin only. Returns all users except the requesting admin.
    Supports filtering by role, languages, activity status, and registration date.

    Query Parameters:
        search: Search by email or username
        role: Filter by user role (user/admin)
        native_language: Filter by native language
        active_learning_language: Filter by currently active learning language
        level: Filter by active language level (A1-C2)
        is_active: Filter by account status (true/false)
        created_after: Show users registered after this date
        created_before: Show users registered before this date
        limit: Max records to return (from pagination)
        offset: Records to skip (from pagination)

    Returns:
        List of users with their active learning language and account details

    Note:
        Filters for active_learning_language and level only apply to users
        who have set an active learning language
    """
    result = await get_users_by_admin(
        db,
        admin.id,
        search,
        role,
        native_language,
        active_learning_language,
        level,
        is_active,
        created_after,
        created_before,
        pagination,
    )

    return result


@router.get('/users/{user_id}',
           response_model=UserRead,
           summary='Get user details by ID')
async def get_user_endpoint(
        db: db_dependency,
        admin: current_admin_dependency,
        user_id: int
) -> UserRead:
    """
    Get detailed information about specific user by ID.

    Admin only. Returns user profile with account information
    and active learning language if set.

    Path Parameters:
        user_id: User ID to retrieve

    Returns:
        User details including role, active status, active learning
        language, and registration date

    Raises:
        404: User not found
        403: Non-admin user attempting access
    """
    user = await get_user_with_active_language(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User id:{user_id} not found'
        )

    return UserRead.model_validate(user)


@router.patch('/users/{user_id}',
              response_model=UserRead,
              summary='Update user')
async def update_user_by_admin_endpoint(
        db: db_dependency,
        admin: current_admin_dependency,
        user_id: int,
        data_user: UserUpdateByAdmin,
) -> UserRead:
    """
    Update user profile and account settings.

    Admin only. Allows updating:
    - Basic profile info (email, username, name, native language)
    - Admin-specific fields (role, active status)

    Path Parameters:
        user_id: User ID to update

    Request Body:
        UserUpdateByAdmin with fields to update (all optional)

    Returns:
        Updated user profile

    Raises:
        400: Validation error
        403: Cannot modify own role/status
        404: User not found
        409: Email/username already taken
    """
    updated_user = await update_user_by_admin_service(
        db,
        admin.id,
        user_id,
        data_user
    )
    return UserRead.model_validate(updated_user)


@router.post('users/{user_id}/languages/{language}',
              response_model=UserLanguageBrief,
              summary='Add or update user learning language')
async def update_or_create_user_language_endpoint(
        db: db_dependency,
        admin: current_admin_dependency,
        user_id: int,
        language: LanguageEnum,
        data: UserLanguageLevelUpdate
) -> UserLanguageBrief:
    """
    Add new language to learning list or update existing one.

    Admin only. Creates language if not exists, updates level if exists.
    Can optionally set as active learning language.

    If language already in learning list:
    - Updates proficiency level if provided
    - Returns existing entry if level not provided

    If language not in learning list:
    - Adds language with specified level (defaults to A1)

    Active language behavior:
        - Set make_active=true to explicitly activate
        - Auto-activates if user has no active language (first language)

    Path Parameters:
        user_id: User ID to modify
        language: Language code (en, uk, de)

    Request Body:
        UserLanguageLevelUpdate (optional):
        - level: CEFR level (A1-C2), defaults to A1 for new languages
        - make_active: Set as active language (default: false)

    Returns:
        UserLanguageBrief: Created or updated language entry (201 Created)

    Raises:
        404: User not found
        400: Invalid language or level
    """
    updated_user_language = await update_language_by_admin_service(
        db,
        user_id,
        language,
        data
    )
    return UserLanguageBrief.model_validate(updated_user_language)


@router.post('/exercises',
             response_model=ExerciseRead,
             status_code=status.HTTP_201_CREATED,
             summary='Create new exercise')
async def create_exercise_endpoint(
        db: db_dependency,
        admin: current_admin_dependency,
        data: ExerciseCreate
) -> ExerciseRead:
    """
    Create a new exercise.

    Admin only. Creates exercise with automatic validation of:
    - Options for multiple_choice type (required)
    - Translation pair completeness (both fields or both None)
    - Translation usage rules (not allowed for fill_blank)
    - Topic normalization to title case

    Request Body:
        ExerciseCreate with exercise data

    Returns:
        Created exercise with generated ID and metadata

    Raises:
        400: Validation error (invalid options, translation rules)
        403: Non-admin user attempting access
    """
    created_exercise = await create_exercise(db, data)

    return ExerciseRead.model_validate(created_exercise)