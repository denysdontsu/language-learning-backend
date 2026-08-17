# Standard library
from datetime import date
from typing import Literal

# Third-party
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# CRUD
from app.crud.user_exercise_history import get_history_with_exercise_by_id, get_exercise_history_by_user

# Schemas
from app.schemas import ExerciseHistoryRead, LanguageEnum, LanguageLevelEnum, ExerciseStatusEnum, ExerciseHistoryBrief
from app.utils.helpers import parse_date_range


async def get_exercise_history_by_user_service(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum | None,
        difficulty_level: LanguageLevelEnum | None,
        status: ExerciseStatusEnum | None,
        period: Literal['7d', '30d', '3m', '1y', 'all'] | None,
        date_from: date | None,
        date_to: date | None,
        order: Literal['asc', 'desc'],
        limit: int,
        offset: int,
) -> list[ExerciseHistoryBrief]:
    """
    Get paginated exercise history for a user with filtering.

    Applies date range parsing (period takes precedence over custom dates),
    then fetches and serializes history records.

    Args:
        db: Database session
        user_id: User ID to fetch history for
        language: Filter by practiced language (matches question or answer)
        difficulty_level: Filter by CEFR level
        status: Filter by completion status
        period: Quick date range (overrides date_from/date_to if set)
        date_from: Custom start date (inclusive)
        date_to: Custom end date (inclusive)
        order: Sort order by completion date
        limit: Maximum records to return
        offset: Records to skip for pagination

    Returns:
        List of serialized exercise history records
    """
    # Parse date range (period takes precedence)
    parsed_from, parsed_to = parse_date_range(period, date_from, date_to)

    result = await get_exercise_history_by_user(
        db=db,
        user_id=user_id,
        language=language,
        difficulty_level=difficulty_level,
        status=status,
        date_from=parsed_from,
        date_to=parsed_to,
        order=order,
        limit=limit,
        offset=offset,
    )

    return [ExerciseHistoryBrief.model_validate(o) for o in result]

async def get_exercise_history_by_id_service(
        db: AsyncSession,
        user_id: int,
        history_id: int
) -> ExerciseHistoryRead:
    """
    Get exercise history record by ID with authorization check.

    Args:
        db: Database session
        user_id: Current user ID (for authorization)
        history_id: Exercise history record ID

    Returns:
        ExerciseHistoryRead with full exercise details

    Raises:
        HTTPException 404: Record not found or doesn't belong to user

    Security:
        Returns 404 instead of 403 to not reveal existence of other users' records
    """
    history = await get_history_with_exercise_by_id(db, user_id, history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Exercise history record {history_id} not found'
        )

    return ExerciseHistoryRead.model_validate(history)
