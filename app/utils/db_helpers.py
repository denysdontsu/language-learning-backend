# Third-party
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# CRUD
from app.crud.user import get_user_with_active_language, get_user_by_id
from app.crud.exercise import get_exercise_by_id

# Models
from app.models import User, Exercise

async def get_user_or_404(
        db: AsyncSession,
        user_id: int,
        load_active_language: bool = True
) -> User:
    """
    Get user by ID or raise 404.

    Reduces boilerplate in endpoints and services by providing
    a single point for user existence validation.

    Args:
        db: Database session
        user_id: User ID to fetch
        load_active_language: Whether to eagerly load active language (default: True)

    Returns:
        User: User object with optional active language loaded

    Raises:
        HTTPException 404: User not found
    """
    if load_active_language:
        user = await get_user_with_active_language(db, user_id)
    else:
        user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {user_id} not found'
        )

    return user


async def get_exercise_or_404(
        db: AsyncSession,
        exercise_id: int
) -> Exercise:
    """
    Get exercise by ID or raise 404.

    Args:
        db: Database session
        exercise_id: Exercise ID to fetch

    Returns:
        Exercise: Exercise object

    Raises:
        HTTPException 404: Exercise not found
    """
    exercise = await get_exercise_by_id(db, exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Exercise {exercise_id} not found'
        )

    return exercise