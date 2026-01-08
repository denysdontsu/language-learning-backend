from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.crud.user import get_user_by_email, create_user, get_user_by_username
from app.core.security import hash_password


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
    new_user = await create_user(db, data, hashed_password)

    return new_user