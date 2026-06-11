# Standard library
from datetime import date
from typing import Literal, Any

# Third-party
from sqlalchemy import or_, select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

# Models
from app.models import Exercise, UserExerciseHistory

# Schemas
from app.schemas import (
    ExerciseTypeEnum,
    LanguageLevelEnum,
    LanguageEnum,
    ExerciseStatusEnum,
    ExerciseCreate
)

async def create_exercise(
        db: AsyncSession,
        data: ExerciseCreate
) -> Exercise:
    """
    Create new exercise in database.

    Validation is already performed by ExerciseCreate schema before
    this function is called.

    Args:
        db: Database session
        data: Validated exercise data from ExerciseCreate schema

    Returns:
        Created Exercise model with generated ID and timestamps

    Note:
        - is_active defaults to True (database default)
        - added_at is set automatically by database
        - Topic is already normalized to title case by schema validator
    """
    new_exercise = Exercise(
        topic=data.topic,
        difficult_level=data.difficult_level,
        type=data.type,
        options=data.options,
        question_text=data.question_text,
        question_language=data.question_language,
        correct_answer=data.correct_answer,
        answer_language=data.answer_language,
        question_translation=data.question_translation,
        question_translation_language=data.question_translation_language
    )
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise)

    return new_exercise


async def get_exercises(
        db: AsyncSession,
        search: str | None,
        topic: str | None,
        difficult_level: LanguageLevelEnum | None,
        exercise_type: ExerciseTypeEnum | None,
        question_language: LanguageEnum | None,
        answer_language: LanguageEnum | None,
        date_from: date | None,
        date_to: date | None,
        is_active: bool | None = True,
        order: Literal['asc', 'desc'] = 'desc',
        limit: int = 50,
        offset: int = 0,
) -> list[Exercise]:
    """
    Retrieve exercises with filtering, sorting, and pagination.

    Supports comprehensive filtering by content, metadata, languages,
    activity status, and creation date range.

    Args:
        db: Database session
        search: Search text in question and answer (case-insensitive partial match)
        topic: Filter by topic (exact match on normalized topic)
        difficult_level: Filter by CEFR level (A1-C2)
        exercise_type: Filter by type (fill_blank, multiple_choice, etc.)
        question_language: Filter by question language
        answer_language: Filter by answer language
        date_from: Show exercises created on or after this datetime (inclusive)
        date_to: Show exercises created on or before this datetime (inclusive)
        is_active: Filter by active status (None = all, True = active only, False = inactive only)
        order: Sort order by added_at ('asc' or 'desc')
        limit: Maximum number of records to return
        offset: Number of records to skip (for pagination)

    Returns:
        list[Exercise]: List of exercises matching criteria (may be empty)
    """
    stmt = select(Exercise)

    # Search filter
    if search:
        stmt = stmt.where(
            or_(
                Exercise.question_text.ilike(f'%{search}%'),
                Exercise.correct_answer.ilike(f'%{search}%')
            )
        )

    # Exercise metadata filters
    if topic:
        stmt = stmt.where(Exercise.topic == topic)
    if difficult_level:
        stmt = stmt.where(Exercise.difficult_level == difficult_level)
    if exercise_type:
        stmt = stmt.where(Exercise.type == exercise_type)

    # Language filters
    if question_language:
        stmt = stmt.where(Exercise.question_language == question_language)
    if answer_language:
        stmt = stmt.where(Exercise.answer_language == answer_language)

    # Active status filter
    if is_active is not None:
        stmt = stmt.where(Exercise.is_active == is_active)

    # Date range filters
    if date_from:
        stmt = stmt.where(Exercise.added_at >= date_from)
    if date_to:
        stmt = stmt.where(Exercise.added_at <= date_to)

    # Sorting
    if order == 'asc':
        stmt = stmt.order_by(Exercise.added_at.asc())
    else:
        stmt = stmt.order_by(Exercise.added_at.desc())

    # Pagination
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_exercise_stats(
        db: AsyncSession,
        exercise_id: int
) -> dict | None:
    """
    Get exercise usage statistics.

    Aggregates data from user_exercise_history to provide insights
    about exercise performance, popularity, and difficulty.

    Args:
        db: Database session
        exercise_id: Exercise ID to get stats for

    Returns:
        Dict with statistics or None if exercise never attempted:
        - total_attempts: Total number of attempts
        - unique_users: Number of unique users
        - correct_count: Correct answers count
        - incorrect_count: Incorrect answers count
        - skipped_count: Skipped count
        - accuracy_rate: Percentage of correct answers (0-100)
        - avg_time_seconds: Average completion time (excluding skips)
        - last_used_at: Last attempt timestamp
    """
    stmt = (
        select(
            # Total attempts
            func.count().label('total_attempts'),

            # Unique users
            func.count(func.distinct(UserExerciseHistory.user_id)).label('unique_users'),

            # Status breakdown
            func.sum(
                case(
                    (UserExerciseHistory.status == ExerciseStatusEnum.CORRECT, 1), else_=None
                )
            ).label('correct_count'),
            func.sum(
                case(
                    (UserExerciseHistory.status == ExerciseStatusEnum.INCORRECT, 1), else_=None
                )
            ).label('incorrect_count'),
            func.sum(
                case(
                    (UserExerciseHistory.status == ExerciseStatusEnum.SKIP, 1), else_=None
                )
            ).label('skipped_count'),

            # Average time (exclude skipped)
            func.avg(
                case(
                    (UserExerciseHistory.status != ExerciseStatusEnum.SKIP,
                    UserExerciseHistory.time_spent_seconds),
                    else_=None
                )
            ).label('avg_time_seconds'),
            # Last usage
            func.max(UserExerciseHistory.completed_at).label('last_used_at')
        ).where(
            UserExerciseHistory.exercise_id == exercise_id
        )
    )
    result = await db.execute(stmt)
    row = result.one_or_none()

    if row is None or row.total_attempts == 0:
        return None

    # Calculate accuracy (exclude skipped)
    answer = row.correct_count + row.incorrect_count
    accuracy_rate = (row.correct_count / answer) * 100 if answer > 0 else 0

    return {
        'total_attempts': row.total_attempts,
        'unique_users': row.unique_users,
        'correct_count': row.correct_count,
        'incorrect_count': row.incorrect_count,
        'skipped_count': row.skipped_count,
        'accuracy_rate': round(accuracy_rate, 1),
        'avg_time_seconds': round(row.avg_time_seconds, 1) if row.avg_time_seconds else None,
        'last_used_at': row.last_used_at
    }


async def update_exercise(
        db: AsyncSession,
        exercise: Exercise,
        update_data: dict[str, Any]
) -> Exercise:
    """
    Update exercise fields.

    Updates only fields present in update_data dictionary.

    Args:
        db: Database session
        exercise: Exercise object to update
        update_data: Dictionary with fields to update

    Returns:
        Exercise: Updated exercise object with refreshed state
    """
    # Update only provided fields
    for field, value in update_data.items():
        setattr(exercise, field, value)

    await db.commit()
    await db.refresh(exercise)
    return exercise