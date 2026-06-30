# Standard library
from typing import Literal

# Third-party
from fastapi import APIRouter, Query

# Dependencies
from app.api.dependencies import db_dependency

# Schemas
from app.schemas import (
    LanguageEnum,
    AdminUserStatistics,
    PlatformStatistics
)

# Services
from app.services.admin.statistics import (
    get_user_statistics_complete_admin,
    get_platform_statistics
)

router = APIRouter(
    prefix='/statistics',
    tags=['Admin / Statistics'],
)


@router.get('/',
            response_model=PlatformStatistics,
            summary = 'Get detailed platform statistics')
async def get_platform_statistics_endpoint(
        db: db_dependency,
        period: Literal['7d', '30d', '3m', '1y', 'all'] = Query(
            'all',
            description='Time period for statistics (7 days, 30 days, 3 months, 1 year, or all time)'
        )
) -> PlatformStatistics:
    """
    Get platform-wide statistics overview.

    Admin only endpoint that provides aggregated metrics across all users
    and exercises on the platform.

    Query Parameters:
    - period: Time period for statistics calculation (7d, 30d, 3m, 1y, all)

    Response Structure:
    - total_users: Total number of registered users
    - active_users: Number of users active in the selected period
    - total_exercises: Total number of exercises in the platform
    - active_exercises: Number of exercises currently active (not archived)
    - avg_accuracy: Average accuracy percentage across all attempts
    - total_attempts: Total number of exercise attempts (excluding skipped)
    - daily_active_users: Number of users active today

    Returns:
    PlatformStatistics: Aggregated platform statistics
    """
    return await get_platform_statistics(db, period)


@router.get('/{user_id}',
            response_model=AdminUserStatistics,
            summary='Get detailed user performance statistics')
async def get_user_performance_statistics(
        db: db_dependency,
        user_id: int,
        language: LanguageEnum = Query(
            None,
            description='Filter by language (null = all languages)'
        ),
        period: Literal['7d', '30d', '3m', '1y', 'all'] = Query(
            'all',
            description='Time period for statistics (7 days, 30 days, 3 months, 1 year, or all time)'
        )
) -> AdminUserStatistics:
    """
    Get complete user statistics including overview and performance analysis.

    Admin only endpoint that provides comprehensive statistics for any user.
    Combines overview metrics (general progress) with detailed performance
    analysis (by difficulty level and topics).

    Query Parameters:
    - language: Filter by specific language (default: all languages)
    - period: Time period for statistics calculation (7d, 30d, 3m, 1y, all)

    Path Parameters:
    - user_id: ID of user to get statistics for

    Response Structure:
    - user: Basic user information (id, username, is_active, native_language)
    - overview: General progress metrics
        * total_exercises: All exercises (including skipped)
        * total_answered: Answered exercises only
        * accuracy: Percentage of correct answers
        * total_study_hours: Time spent studying
        * current_streak_days: Consecutive practice days
        * is_today_completed: Practiced today or not
    - performance: Detailed performance analysis
        * by_difficulty: Stats per CEFR level (A1-C2), mastery status and progress
        * top_topics: 5 best performing topics by accuracy
        * weak_topics: 5 topics needing practice (min 20 exercises)
        * suggested_level: Recommended next difficulty level (only with language filter)

    Returns:
    AdminUserStatistics: Complete user statistics

    Raises:
    404: User not found
    """
    return await get_user_statistics_complete_admin(db, user_id, language, period)