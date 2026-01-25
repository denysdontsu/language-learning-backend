from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_exercise_history import get_history_with_exercise_by_id
from app.schemas.user_exercise_history import ExerciseHistoryRead


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
