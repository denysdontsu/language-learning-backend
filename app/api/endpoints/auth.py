from fastapi import APIRouter, status

from app.api.dependencies import db_dependency
from app.schemas.user import UserCreate, UserCreateWithLanguage, UserBrief, UserBriefWithLang
from app.services.auth import register_user_simple, register_user_with_language

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register',
             status_code=status.HTTP_201_CREATED,
             response_model=UserBrief,
             summary="Simple user registration")
async def register(
        user_data: UserCreate,
        db: db_dependency
):
    """
    Register a new user without language selection.

    Simple registration flow where user can add learning language
    later through profile settings.

    Business rules:
    - Email must be unique across all users
    - Username must be unique across all users
    - Password must meet strength requirements (8+ chars, letter, digit)
    - New user is active by default
    - Password is hashed before storage (Argon2)

    Args:
        user_data: User registration data (email, username, name, native_language, password)
        db: Database session dependency

    Returns:
        UserBrief: Created user profile (id, email, username, name, native_language)

    Raises:
        HTTPException: 400 if email already registered
        HTTPException: 400 if username already taken
        HTTPException: 422 if validation fails (weak password, invalid email, etc.)
    """
    return await register_user_simple(db, user_data)


@router.post('/register/complete',
             status_code=status.HTTP_201_CREATED,
             response_model=UserBriefWithLang,
             summary="User registration with language")
async def register_with_language(
        user_data: UserCreateWithLanguage,
        db: db_dependency
):
    """
    Register a new user with learning language selection.

    Complete registration flow that creates user account and sets up
    initial learning language in single transaction.

    Business rules:
    - Email must be unique across all users
    - Username must be unique across all users
    - Password must meet strength requirements (8+ chars, letter, digit)
    - User and language entry created in single database transaction
    - Language level defaults to A1 if not specified
    - New user is active by default
    - Password is hashed before storage (Argon2)

    Args:
        user_data: Complete registration data including:
            - email, username, name, native_language, password (from base)
            - active_learning_language: Language to learn (ISO 639-1 code)
            - active_language_level: Current proficiency (CEFR: A1-C2, defaults to A1)
        db: Database session dependency

    Returns:
        UserBriefWithLang: Created user profile with embedded active language info
            - User fields: id, email, username, name, native_language
            - Language fields: language, level

    Raises:
        HTTPException: 400 if email already registered
        HTTPException: 400 if username already taken
        HTTPException: 422 if validation fails (weak password, invalid language code, etc.)
    """
    return await register_user_with_language(db, user_data)