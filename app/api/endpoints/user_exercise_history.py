from typing import Literal

from fastapi import APIRouter, Query
from watchfiles import awatch

from app.api.dependencies import db_dependency, pagination_dependency, current_active_user_dependency
from app.crud.user_exercise_history import get_exercise_history_by_user
from app.schemas.enums import LanguageLevelEnum, LanguageEnum, ExerciseStatusEnum
from app.schemas.user_exercise_history import ExerciseHistoryBrief, ExerciseHistoryRead
from app.services.user_exercise_history import get_exercise_history_by_id_service

router = APIRouter(prefix='/history', tags=['History'])

@router.get('/',
            response_model=list[ExerciseHistoryBrief],
            summary='Get user exercise history')
async def get_exercise_history(
        db: db_dependency,
        user: current_active_user_dependency,
        pagination: pagination_dependency,
        order: Literal['asc', 'desc'] = Query('desc', description='Sort order by completion date'),
        language: LanguageEnum | None = Query(None, description='Filter by practiced language'),
        difficult_level: LanguageLevelEnum | None = Query(None, description='Filter by difficulty level'),
        status: ExerciseStatusEnum | None = Query(None, description='Filter by completion status')
) -> list[ExerciseHistoryBrief]:
    """
    Get authenticated user's exercise history with optional filters.

    Returns list of completed exercises ordered by completion time.
    Each record includes minimal exercise info for list display.

    Query Parameters:
        order: Sort by completion date (asc/desc, default: desc)
        language: Filter by practiced language (matches question or answer)
        difficult_level: Filter by CEFR level (A1-C2)
        status: Filter by result (correct, incorrect, skip)
        limit: Max records to return (from pagination dependency)
        offset: Records to skip (from pagination dependency)

    Returns:
        List of exercise history records with nested exercise data
    """
    offset, limit = pagination

    result = await get_exercise_history_by_user(
        db,
        user.id,
        language,
        difficult_level,
        status,
        limit,
        offset,
        order
    )
    return [ExerciseHistoryBrief.model_validate(o) for o in result]


@router.get('/{history_id}',
            response_model=ExerciseHistoryRead,
            summary='Get exercise history record by ID')
async def get_exercise_history_record(
        db: db_dependency,
        user: current_active_user_dependency,
        history_id: int
) -> ExerciseHistoryRead:
    """
    Get detailed information about single exercise history record.

    Includes full exercise details with correct answer, options,
    translation, and explanation for review.

    Path Parameters:
        history_id: Exercise history record ID

    Returns:
        Detailed exercise history record with complete exercise information

    Raises:
        404: History record not found or doesn't belong to authenticated user
    """
    return await get_exercise_history_by_id_service(db, user.id, history_id)