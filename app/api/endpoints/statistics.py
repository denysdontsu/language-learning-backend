from typing import Literal

from fastapi import APIRouter, Query

from app.api.dependencies import db_dependency, current_active_user_dependency
from app.schemas.enums import LanguageEnum
from app.schemas.statistics import OverviewResponse
from app.services.statistics import get_basic_statistics

router = APIRouter(prefix='/users/me/statistics', tags=['Statistics'])


@router.get('/',
            response_model=OverviewResponse,
            summary='Get current user statistics overview')
async def get_user_statistics(
        db: db_dependency,
        user: current_active_user_dependency,
        language: LanguageEnum | None = Query(
                    None,
            description='Filter by language (null = all languages)'
        ),
        period: Literal['7d', '30d', '3m', '1y', 'all'] = Query(
            'all',
            description= 'Time period for statistics (7 days, 30 days, 3 months, 1 year, or all time)'
        )
) -> OverviewResponse:
    """
    Get user statistics overview for specified period and language.

    Returns aggregated metrics:
    - Total exercises completed (including and excluding skipped)
    - Overall accuracy percentage (from answered exercises)
    - Current consecutive days streak
    - Whether at least one exercise was completed today
    - Total study time in hours

    Filters:
    - language: Optional language filter (null = all languages)
    - period: Time period (7d, 30d, 3m, 1y, all)

    Without language filter, aggregates across all practiced languages.
    With language filter, shows statistics for that language only.
    """
    return await get_basic_statistics(db, user.id, language, period)