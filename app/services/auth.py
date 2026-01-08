from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.user import (
    get_user_by_email,
    create_user_with_language,
    create_user,
    get_user_by_username)
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateWithLanguage, UserBriefWithLang
from app.schemas.user_level_language import UserLanguageBase


async def register_user_simple(
        db: AsyncSession,
        data: UserCreate
) -> User:
    """
        Register a new user.

        Business rules:
        - Email must be unique
        - Password is hashed before saving
        - New user is active by default

        Args:
            db: Database session
            data: User creation data

        Returns:
            User: Created user

        Raises:
            HTTPException: 409 if email already exists
        """
    # Email uniqueness validation
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This email is already registered'
        )
    # Username uniqueness validation
    existing = await get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This username is already registered'
        )
    # Password hashing (Argon2)
    hashed_password = hash_password(data.password)
    # Create user
    new_user = await create_user(db, data, hashed_password)

    return new_user


async def register_user_with_language(
        db: AsyncSession,
        data: UserCreateWithLanguage,
) -> UserBriefWithLang:
    """
    Register user with active learning language.

    Complete registration flow that creates user account and
    sets up initial learning language in single transaction.

    Business rules:
    - Email must be unique
    - Username must be unique
    - Password is hashed before storage (Argon2)
    - User and language created in single transaction
    - New user is active by default

    Args:
        db: Database session
        data: User registration data with language

    Returns:
        UserBriefWithLang: Created user with embedded language info

    Raises:
        HTTPException: 400 if email or username already exists
    """
    # Email uniqueness validation
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This email is already registered'
        )
    # Username uniqueness validation
    existing = await get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This username is already registered'
        )
    # Password hashing (Argon2)
    hashed_password = hash_password(data.password)
    # Create user with language
    new_user = await create_user_with_language(db, data, hashed_password)

    # Construct response with embedded language
    return UserBriefWithLang(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        username=new_user.username,
        native_language=new_user.native_language,
        active_learning_language=UserLanguageBase(
            language=data.active_learning_language,
            level=data.active_language_level
        )
    )