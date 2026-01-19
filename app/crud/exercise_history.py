from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserExerciseHistory
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