# Standard library
import asyncio
from typing import Literal

# Third-party
from sqlalchemy.ext.asyncio import AsyncSession

# Cache
from app.cache import CacheKeys, cache_manager

# CRUD
from app.crud.admin.statistics import get_platform_statistics_data

# Schemas
from app.schemas import (
    LanguageEnum,
    UserBrief,
    AdminUserStatistics,
    PlatformStatistics
)

# Services
from app.services.statistics import get_basic_statistics, get_performance_statistics

# Utils
from app.utils.db_helpers import get_user_or_404


async def get_user_statistics_complete_admin(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum | None = None,
        period: Literal['7d', '30d', '3m', '1y', 'all'] = 'all',
) -> AdminUserStatistics:
    """
    Get complete user statistics (overview + performance) for admin view.

    Fetches user's comprehensive statistics including both overview metrics
    and detailed performance analysis. Executes overview and performance
    queries in parallel for optimal performance.

    Statistics include:

    Overview metrics:
    - total_exercises: Total exercises (including skipped)
    - total_answered: Exercises excluding skipped
    - accuracy: Percentage of correct answers (0-100)
    - total_study_hours: Total time spent on exercises
    - current_streak_days: Consecutive practice days
    - is_today_completed: Whether practiced today

    Performance metrics:
    - by_difficulty: Statistics per CEFR level (A1-C2)
      * accuracy: Accuracy percentage
      * total_answered: Number of exercises
      * mastered: True if accuracy >= 80% and total >= 100
      * in_progress: True if 20 <= total < 100
    - top_topics: 5 topics with highest accuracy
    - weak_topics: 5 topics with lowest accuracy (min 20 exercises)
    - suggested_level: Recommended next difficulty level

    Args:
        db: Database session (async)
        user_id: User ID to fetch statistics for
        language: Optional language filter (None = all languages)
        period: Time period for statistics:
            - '7d': Last 7 days
            - '30d': Last 30 days
            - '3m': Last 3 months
            - '1y': Last year
            - 'all': All time (default)

    Returns:
        AdminUserStatistics: Complete user statistics containing:
        - user: UserBrief (id, username, is_active, native_language)
        - overview: UserStatisticsOverview
        - performance: UserStatisticsPerformance

    Raises:
        HTTPException 404: User not found

    Performance:
        Executes two queries in parallel (asyncio.gather):
        - Overview query: ~100-200ms
        - Performance query: ~300-500ms
        Total: ~300-500ms (parallel execution)
    """
    user = await get_user_or_404(db, user_id)

    # Fetch history for period
    overview, performance = await asyncio.gather(
        get_basic_statistics(db, user_id, language, period),
        get_performance_statistics(db, user_id, language, period)
    )

    return AdminUserStatistics(
        user=UserBrief.model_validate(user),
        overview=overview,
        performance=performance
    )


async def get_platform_statistics(
        db: AsyncSession,
        period: Literal['7d', '30d', '3m', '1y', 'all'] = 'all',
) -> PlatformStatistics:
    """
    Get platform-wide statistics.

    Calculates:
    - Total and active registered users
    - Total and active exercises
    - Average accuracy across all attempts
    - Total number of attempts
    - Daily active users (today)

    Args:
        db: Database session
        period: Time period for active users calculation

    Returns:
        PlatformStatistics with aggregated platform metrics
    """
    # Check cache
    cache_key = CacheKeys.platform_stats(period)
    cached = await cache_manager.get(cache_key)
    if cached:
        return PlatformStatistics.model_validate(cached)

    data = await get_platform_statistics_data(db=db, period=period)
    platform_stats = _calculate_platform_statistics(data)

    # Save cache
    await cache_manager.set(
        cache_key,
        PlatformStatistics.model_dump(platform_stats),
        CacheKeys.PLATFORM_STATS_TTL
    )

    return platform_stats

def _calculate_platform_statistics(data: dict) -> PlatformStatistics:
    """
    Build PlatformStatistics model from raw data.

    Args:
        data: Raw counts and metrics from database

    Returns:
        PlatformStatistics response model
    """
    avg_accuracy = data['avg_accuracy'] * 100 if data['avg_accuracy'] <= 1 else data['avg_accuracy']

    return PlatformStatistics(
        total_users=data['total_users'],
        active_users=data['active_users'],
        total_exercises=data['total_exercises'],
        active_exercises=data['active_exercises'],
        avg_accuracy=avg_accuracy,
        total_attempts=data['total_attempts'],
        daily_active_users=data['daily_active_users'],
    )