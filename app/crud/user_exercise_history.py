from typing import Literal
from datetime import datetime

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from app.models import UserExerciseHistory, Exercise
from app.schemas.enums import LanguageEnum, LanguageLevelEnum, ExerciseStatusEnum
from app.schemas.user_exercise_history import ExerciseHistoryCreate


async def create_user_history(
        db: AsyncSession,
        data: ExerciseHistoryCreate,
) -> UserExerciseHistory:
    """
    Create new exercise history record.

    Saves user's exercise attempt to history for spaced repetition
    and progress tracking.

    Args:
        db: Database session
        data: History record data

    Returns:
        Created UserExerciseHistory record
    """
    new_history = UserExerciseHistory(
        user_id=data.user_id,
        exercise_id=data.exercise_id,
        user_answer=data.user_answer,
        status=data.status,
        time_spent_seconds=data.time_spent_seconds
    )
    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

    return new_history


async def get_exercise_history_by_user(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum | None,
        difficulty_level: LanguageLevelEnum | None,
        status: ExerciseStatusEnum | None,
        date_from: datetime | None,
        date_to: datetime | None,
        order: Literal['asc', 'desc'] = 'desc',
        limit: int = 50,
        offset: int = 0
) -> list[UserExerciseHistory]:
    """
    Get user's exercise history with filtering and pagination.

    Args:
        db: Database session
        user_id: User ID
        language: Filter by practiced language (question or answer)
        difficulty_level: Filter by difficulty level
        status: Filter by completion status (correct/incorrect/skip)
        date_from: Filter exercises from this date (inclusive, UTC)
        date_to: Filter exercises to this date (inclusive, UTC)
        order: Sort order by completion date ('asc' or 'desc')
        limit: Maximum number of records to return
        offset: Number of records to skip (for pagination)

    Returns:
        List of UserExerciseHistory records with joined Exercise data
    """
    # Base query with eager loading
    stmt = (
        select(UserExerciseHistory)
        .join(UserExerciseHistory.exercise)
        .options(contains_eager(UserExerciseHistory.exercise))
        .where(UserExerciseHistory.user_id == user_id)
    )

    # Date range
    if date_from:
        stmt = stmt.where(
            UserExerciseHistory.completed_at >= date_from
        )

    if date_to:
        stmt = stmt.where(
            UserExerciseHistory.completed_at <= date_to
        )

    # Apply filters
    if difficulty_level:
        stmt = stmt.where(
            Exercise.difficult_level == difficulty_level
        )

    if language:
        # Match language in either question or answer
        stmt = stmt.where(
            or_(
                Exercise.question_language == language,
                Exercise.answer_language == language
            )
        )

    if status:
        stmt = stmt.where(
            UserExerciseHistory.status == status
        )

    # Apply sorting
    if order == 'desc':
        stmt = stmt.order_by(UserExerciseHistory.completed_at.desc())
    else:
        stmt = stmt.order_by(UserExerciseHistory.completed_at.asc())

    # Apply pagination
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_history_with_exercise_by_id(
        db: AsyncSession,
        user_id: int,
        history_id: int,
) -> UserExerciseHistory | None:
    """
    Get exercise history record with eagerly loaded exercise data.

    Args:
        db: Database session
        user_id: Optional user ID for filtering (security)
        history_id: Exercise history record ID

    Returns:
        UserExerciseHistory with joined Exercise or None if not found
    """
    stmt = (select(UserExerciseHistory)
            .join(UserExerciseHistory.exercise)
            .options(contains_eager(UserExerciseHistory.exercise))
            .where(UserExerciseHistory.id == history_id))

    #  Apply user filter if provided (for authorization)
    if user_id is not None:
        stmt = stmt.where(UserExerciseHistory.user_id == user_id)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()