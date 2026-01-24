from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import db_dependency
from app.schemas.user import (
    UserCreate,
    UserCreateWithLanguage,
    UserBrief,
    UserBriefWithLang,
    UserLogin)
from app.services.auth import (
    register_user_simple,
    register_user_with_language,
    authenticate_user)

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
            - Language fields: language, level and level description

    Raises:
        HTTPException: 400 if email already registered
        HTTPException: 400 if username already taken
        HTTPException: 422 if validation fails (weak password, invalid language code, etc.)
    """
    return await register_user_with_language(db, user_data)


@router.post('/token',
             status_code=status.HTTP_200_OK,
             summary='OAuth2 compatible login for Swagger UI')
async def login_oauth2(
        db: db_dependency,
        data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user via OAuth2 password flow.

    OAuth2-compatible endpoint for Swagger UI authentication.
    Uses form data with username and password fields.

    Args:
        db: Database session
        data: OAuth2 form data with username (email) and password

    Returns:
        dict: Token response with access_token and token_type 'bearer'

    Raises:
        HTTPException: 401 if credentials invalid (wrong email or password)
        HTTPException: 403 if account is disabled
    """
    token = await authenticate_user(db, data.username, data.password)

    return {
        'access_token': token,
        'token_type': 'bearer'
    }

@router.post('/login',
             status_code=status.HTTP_200_OK,
             summary='JSON login endpoint for frontend applications')
async def login(
        db: db_dependency,
        data: UserLogin
):
    """
    Authenticate user with email and password.

    JSON-based login endpoint for frontend applications.
    Accepts email instead of username for authentication.

    Args:
        db: Database session
        data: Login credentials with email and password

    Returns:
        dict: Token response with access_token and token_type ('bearer')

    Raises:
        HTTPException: 401 if credentials invalid (wrong email or password)
        HTTPException: 403 if account is disabled
    """
    token = await authenticate_user(db, data.email, data.password)

    return {
        'access_token': token,
        'token_type': 'bearer'
    }