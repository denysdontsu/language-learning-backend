from typing import Literal

from fastapi import APIRouter, Query

from app.api.dependencies import db_dependency, current_active_user_dependency
from app.schemas.enums import LanguageEnum
from app.schemas.statistics import OverviewResponse, PerformanceResponse
from app.services.statistics import get_basic_statistics, get_performance_statistics

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


@router.get('/performance',
            response_model=PerformanceResponse,
            summary='Get detailed performance statistics')
async def get_user_performance_statistics(
        db: db_dependency,
        user: current_active_user_dependency,
        language: LanguageEnum = Query(
            None,
            description='Filter by language (null = all languages)'
        ),
        period: Literal['7d', '30d', '3m', '1y', 'all'] = Query(
            'all',
            description='Time period for statistics (7 days, 30 days, 3 months, 1 year, or all time)'
        )
) -> PerformanceResponse:
    """
    Get detailed performance statistics by difficulty and topics.

    Returns:
    - Accuracy and mastery status per CEFR level (A1-C2)
    - Top 5 topics by accuracy
    - Weak topics needing practice (accuracy < 60%, min 20 exercises)

    Filters:
    - language: Optional language filter (null = all languages)
    - period: Time period (7d, 30d, 3m, 1y, all)

    Performance metrics:
    - by_difficulty: Stats for each CEFR level with mastery status
    - top_topics: Best performing topics (highest accuracy)
    - weak_topics: Topics needing practice (low accuracy, sufficient attempts)

    Mastery criteria:
    - Difficulty level: accuracy >= 80% and total >= 100 exercises
    - Topic status: mastered (85%+), good (70-85%), learning (50-70%), needs_practice (<50%)
    """
    return await get_performance_statistics(db, user.id, language, period)


