from datetime import date
from typing import Literal

from fastapi import APIRouter, Query

from app.api.dependencies import db_dependency, pagination_dependency, current_active_user_dependency
from app.crud.user_exercise_history import get_exercise_history_by_user
from app.schemas.enums import LanguageLevelEnum, LanguageEnum, ExerciseStatusEnum
from app.schemas.user_exercise_history import ExerciseHistoryBrief, ExerciseHistoryRead
from app.services.user_exercise_history import get_exercise_history_by_id_service
from app.utils.helpers import parse_date_range

router = APIRouter(prefix='/history', tags=['History'])

@router.get('/',
            response_model=list[ExerciseHistoryBrief],
            summary='Get user exercise history')
async def get_exercise_history(
        db: db_dependency,
        user: current_active_user_dependency,
        pagination: pagination_dependency,

        # Sorting
        order: Literal['asc', 'desc'] = Query(
            'desc',
            description='Sort order by completion date (ascending or descending)'
        ),

        # Filters
        language: LanguageEnum | None = Query(
            None,
            description='Filter by practiced language'
        ),
        difficult_level: LanguageLevelEnum | None = Query(
            None,
            description='Filter by difficulty level'
        ),
        status: ExerciseStatusEnum | None = Query(
            None,
            description='Filter by completion status'
        ),

        # Date filters: Quick periods OR custom range
        period: Literal['7d', '30d', '3m', '1y', 'all']  | None = Query(
            None,
            description='Quick time period (overrides date_from/date_to if set)'
        ),
        date_from: date | None = Query(
            None,
            description='Filter from date (YYYY-MM-DD, inclusive)'),
        date_to: date | None = Query(
            None,
            description='Filter to date (YYYY-MM-DD, inclusive)'
        )
) -> list[ExerciseHistoryBrief]:
    """
    Get authenticated user's exercise history with optional filters.

    Returns a paginated list of completed exercises ordered by completion time.
    Each record includes brief exercise info for list display or overview views.

    Date filtering can be applied using either:
    - a predefined period (e.g. last 7 days), or
    - a custom date range via date_from and date_to.

    If both period and custom dates are provided, period takes precedence.

    Query Parameters:
        order: Sort by completion date (asc/desc, default: desc)
        language: Filter by practiced language (matches question or answer)
        difficult_level: Filter by CEFR level (A1-C2)
        status: Filter by result (correct, incorrect, skip)
        period: Quick date range selector (7d, 30d, 3m, 1y, all)
        date_from: Custom start date for filtering (inclusive)
        date_to: Custom end date for filtering (inclusive)
        limit: Max records to return (from pagination dependency)
        offset: Records to skip (from pagination dependency)

    Returns:
        List of exercise history records with nested exercise data
    """
    offset, limit = pagination

    # Parse date range
    date_from, date_to = parse_date_range(period, date_from, date_to)

    result = await get_exercise_history_by_user(
        db,
        user.id,
        language,
        difficult_level,
        status,
        date_from,
        date_to,
        order,
        limit,
        offset
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