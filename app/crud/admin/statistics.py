# Standard library
from datetime import datetime, UTC
from typing import Literal

# Third-party
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

# Models
from app.models import User, UserExerciseHistory, Exercise

# Schemas
from app.schemas import ExerciseStatusEnum

# Utils
from app.utils.helpers import parse_date_range


async def get_platform_statistics_data(
        db: AsyncSession,
        period: Literal['7d', '30d', '3m', '1y', 'all'] = 'all',
) -> dict:
    """
    Fetch raw platform statistics data from database.

    Args:
        db: Database session
        period: Time period for active users calculation

    Returns:
        Dict with raw counts for platform statistics
    """
    date_from, date_to = parse_date_range(
        period=period,
        date_from=None,
        date_to=None
    )

    # Total and active users
    total_users = await db.scalar(
        select(func.count()).select_from(User)
    )

    active_users_stmt = (
        select(func.count(func.distinct(UserExerciseHistory.user_id)))
        .select_from(UserExerciseHistory)
    )
    if date_from:
        active_users_stmt = active_users_stmt.where(
            UserExerciseHistory.completed_at >= date_from
        )
    if date_to:
        active_users_stmt = active_users_stmt.where(
            UserExerciseHistory.completed_at <= date_to
        )
    active_users = await db.scalar(active_users_stmt)

    # Exercises
    total_exercises = await db.scalar(
        select(func.count()).select_from(Exercise)
    )
    active_exercises = await db.scalar(
        select(func.count())
        .select_from(Exercise)
        .where(Exercise.is_active == True)
    )

    # Attempts and accuracy
    attempts_result = await db.execute(
        select(
            func.count().label('total_attempts'),
            func.avg(
                case(
                    (UserExerciseHistory.status == ExerciseStatusEnum.CORRECT, 1),
                    else_=0
                )
            ).label('avg_accuracy')
        )
        .select_from(UserExerciseHistory)
        .where(UserExerciseHistory.status != ExerciseStatusEnum.SKIP)
    )
    attempts_row = attempts_result.one()

    # Daily active users (today UTC)
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_active_users = await db.scalar(
        select(func.count(func.distinct(UserExerciseHistory.user_id)))
        .select_from(UserExerciseHistory)
        .where(UserExerciseHistory.completed_at >= today_start)
    )

    return {
        'total_users': total_users or 0,
        'active_users': active_users or 0,
        'total_exercises': total_exercises or 0,
        'active_exercises': active_exercises or 0,
        'total_attempts': attempts_row.total_attempts or 0,
        'avg_accuracy': float(attempts_row.avg_accuracy or 0),
        'daily_active_users': daily_active_users or 0,
    }