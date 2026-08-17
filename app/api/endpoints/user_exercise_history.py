# Standard library
from datetime import date
from typing import Literal

# Third-party
from fastapi import APIRouter, Query

# Dependencies
from app.api.dependencies import (
    db_dependency,
    pagination_dependency,
    current_active_user_dependency
)

# Schemas
from app.schemas import (
    LanguageLevelEnum,
    LanguageEnum,
    ExerciseStatusEnum,
    ExerciseHistoryBrief,
    ExerciseHistoryRead
)

# Services
from app.services.user_exercise_history import (
    get_exercise_history_by_id_service,
    get_exercise_history_by_user_service
)

router = APIRouter()

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

    Returns paginated history ordered by completion time. Date filtering
    supports predefined periods or custom date ranges — period takes
    precedence if both are provided.

    Query Parameters:
    - order: Sort by completion date (asc/desc, default: desc)
    - language: Filter by practiced language (matches question or answer)
    - difficult_level: Filter by CEFR level (A1-C2)
    - status: Filter by result (correct, incorrect, skip)
    - period: Quick date range (7d, 30d, 3m, 1y, all)
    - date_from: Custom start date (inclusive)
    - date_to: Custom end date (inclusive)
    - limit/offset: Pagination (from dependency)

    Returns:
    list[ExerciseHistoryBrief]: Paginated history records
    """
    offset, limit = pagination

    return await get_exercise_history_by_user_service(
        db=db,
        user_id=user.id,
        language=language,
        difficulty_level=difficult_level,
        status=status,
        period=period,
        date_from=date_from,
        date_to=date_to,
        order=order,
        limit=limit,
        offset=offset,
    )


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