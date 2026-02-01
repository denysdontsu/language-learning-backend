from datetime import date

from fastapi import APIRouter, Query, HTTPException, status

from app.api.dependencies import db_dependency, current_admin_dependency, pagination_dependency
from app.crud.user import get_user_with_active_language
from app.schemas.enums import LanguageEnum, UserRoleEnum, LanguageLevelEnum
from app.schemas.user import UserRead
from app.services.admin import get_users_by_admin


router = APIRouter(prefix='/admin', tags=['Admin'])

@router.get('/users',
            response_model=list[UserRead],
            summary='Get users list with filters')
async def get_users_endpoint(
        db: db_dependency,
        admin: current_admin_dependency,
        pagination: pagination_dependency,

        # Filters
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