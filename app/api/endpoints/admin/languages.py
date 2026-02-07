# Third-party
from fastapi import APIRouter

# Dependencies
from app.api.dependencies import db_dependency

# Schemas
from app.schemas import (
    LanguageEnum,
    UserLanguageBrief,
    UserLanguageLevelUpdate
)

# Services
from app.services.admin.language import update_language_by_admin_service

router = APIRouter(
    prefix='/users/{user_id}/languages',
    tags=['Admin / Languages']
)

@router.post('/{language}',
              response_model=UserLanguageBrief,
              summary='Add or update user learning language')
async def update_or_create_user_language_endpoint(
        db: db_dependency,
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