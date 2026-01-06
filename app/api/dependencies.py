from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import async_session_maker
from app.core.security import decode_access_token, oauth2_scheme
from app.models.user import User
from app.crud.user import get_user_by_id

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide async database session for dependency injection.

    Yields:
        AsyncSession: Database session that will be automatically closed
    """
    async with async_session_maker() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]
"""Database session dependency. Use in endpoint signatures."""

token_dependency = Annotated[str, Depends(oauth2_scheme)]
"""JWT token from Authorization header. Use when token needed directly."""


async def get_current_user(
        db: db_dependency,
        token: token_dependency
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        db: Database session
        token: JWT token extracted from Authorization header

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    try:
        payload = decode_access_token(token)
        user_id = int(payload.sub)

        user = await get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found',
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that authenticated user account is active.

    Args:
        current_user: Authenticated user from get_current_user dependency

    Returns:
        User: Authenticated and active user

    Raises:
        HTTPException: 400 if user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user'
        )
    return current_user

current_user_dependency = Annotated[User, Depends(get_current_active_user)]
"""Active authenticated user. Use in most endpoints requiring authentication."""


async def require_active_language(
        current_user: current_user_dependency
) -> User:
    """
    Verify user has set an active learning language.

    Use for endpoints that require language context (exercises, lessons).

    Args:
        current_user: Active authenticated user

    Returns:
        User: User with active learning language set

    Raises:
        HTTPException: 400 if no active learning language
    """
    if not current_user.active_learning_language_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User must have at least one active learning language'
        )
    return current_user


async def require_admin(
        current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verify user has admin role.

    Use for admin-only endpoints (user management, content moderation).

    Args:
        current_user: Active authenticated user

    Returns:
        User: User with admin role

    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required'
        )
    return current_user


async def get_pagination_params(
        page: int = Query(1, ge=1, description='Page number(started at 1)'),
        size: int = Query(20, ge=1, le=100, description='Items per page (1-100)')
) -> tuple[int, int]:
    """
        Calculate pagination offset and limit from page and size parameters.

        Args:
            page: Page number (1-indexed, default: 1)
            size: Items per page (1-100, default: 20)

        Returns:
            tuple[int, int]: (offset, limit) for database query
        """
    offset = (page - 1) * size
    return offset, size

pagination_dependency = Annotated[tuple[int, int], Depends(get_pagination_params)]
"""Pagination parameters (offset, limit). Use in list endpoints."""
