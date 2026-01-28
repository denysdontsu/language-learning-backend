from datetime import datetime, timedelta, timezone
from typing import Literal, NamedTuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_exercise_history import get_exercise_history_by_user
from app.models import UserExerciseHistory
from app.schemas.enums import LanguageLevelEnum, ExerciseStatusEnum, LanguageEnum
from app.schemas.statistics import OverviewResponse
from app.utils.helpers import parse_date_range


class AccuracyStats(NamedTuple):
    """Accuracy statistics from answered exercises."""
    total_answered: int
    accuracy_percent: float

class StreakResult(NamedTuple):
    """Current streak calculation result."""
    days: int
    is_today_completed: bool


async def get_basic_statistics(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum | None = None,
        period: Literal['7d', '30d', '3m', '1y', 'all'] = 'all',
) -> OverviewResponse:
    """
    Get basic statistics for user.

    Calculates OverviewResponse metrics:
    - Total exercises (including and excluding skipped)
    - Accuracy percentage (correct / answered)
    - Current consecutive days streak
    - Whether exercise was done today
    - Total study time in hours

    Args:
        db: Database session
        user_id: User ID
        language: Language filter
        period: Time period for statistics

    Returns:
        OverviewResponse statistics with aggregated statistics
    """
    # Calculate date range from period
    date_from, date_to = parse_date_range(
        period=period,
        date_from=None,
        date_to=None
    )

    # Fetch history for period
    history = await get_exercise_history_by_user(
        db=db,
        user_id=user_id,
        language=language,
        difficulty_level=None,
        status=None,
        date_from=date_from,
        date_to=date_to,
        limit=10000,
        offset=0,
        order='desc'
    )
    overview = _calculate_overview(history)

    return overview


def _calculate_overview(history: list[UserExerciseHistory]) -> OverviewResponse:
    """
    Calculate overview statistics for user's exercise history.

    Includes:
    - Total exercises count (including skipped)
    - Total answered exercises (excluding skipped)
    - Answer accuracy percentage
    - Current activity streak
    - Total study time in hours

    Args:
        history: List of user exercise history records

    Returns:
        OverviewResponse statistics with aggregated statistics
    """
    if not history:
        return OverviewResponse(
            total_exercises=0,
            total_answered=0,
            accuracy=0,
            current_streak_days=0,
            is_today_completed=False,
            total_study_hours=0
        )

    # Total exercises (including skipped)
    total_exercises = len(history)

    # Accuracy statistics (excluding skipped)
    accuracy_stats = _calculate_accuracy_stats(history)

    # Current streak
    streak_result = _calculate_current_streak(history)

    # Total study hours
    total_seconds = sum(h.time_spent_seconds for h in history)
    total_hours = total_seconds / 3600

    return OverviewResponse(
        total_exercises=total_exercises,
        total_answered=accuracy_stats.total_answered,
        accuracy=accuracy_stats.accuracy_percent,
        current_streak_days=streak_result.days,
        is_today_completed=streak_result.is_today_completed,
        total_study_hours=total_hours
    )

def _calculate_accuracy_stats(
        history: list[UserExerciseHistory],
        difficulty_level: LanguageLevelEnum | None = None
) -> AccuracyStats:
    """
    Calculate accuracy statistics from exercise history.

    Accuracy is calculated only from answered exercises
    (i.e. skipped exercises are excluded).

    Args:
        history: List of user exercise history records
        difficulty_level: Optional difficulty level filter

    Returns:
        AccuracyStats with total answered count and accuracy percentage
    """
    # Optional difficulty filter
    if difficulty_level:
        history = [h for h in history if h.exercise.difficult_level == difficulty_level]

    # Answered exercises (excluding skipped)
    answered = [h for h in history if h.status != ExerciseStatusEnum.SKIP]
    total_answered = len(answered)

    # Accuracy (only from answered exercises)
    correct = sum(1 for h in history if h.status == ExerciseStatusEnum.CORRECT)
    accuracy = (correct / total_answered * 100) if total_answered > 0 else 0.0

    return AccuracyStats(total_answered=total_answered, accuracy_percent=accuracy)

def _calculate_current_streak(history: list[UserExerciseHistory]) -> StreakResult:
    """
    Calculate current consecutive days streak.

    Logic:
    - If exercise done today: streak continues
    - If no exercise today: streak is preserved (grace period)
    - Streak is counted only for strictly consecutive days; missing any day breaks the streak.

    Args:
        history: List of user exercise history records

    Returns:
        StreakResult with days count and today completion status
    """
    # Get unique dates, sorted descending
    days = sorted(
        set(h.completed_at.date() for h in history),
        reverse=True
    )
    streak = 0
    is_today = False

    if not days:
        return StreakResult(days=streak, is_today_completed=is_today)

    today = datetime.now(timezone.utc).date()

    # Check if exercise was done today
    if days[0] == today:
        # Count from today
        is_today = True
        for n, data in enumerate(days):
            extracted_day = today - timedelta(days=n)
            if extracted_day == data:
                streak += 1
            else:

                break

    else:
        # Count from yesterday (today has grace period)
        is_today = False
        for n, data in enumerate(days):
            extracted_day = today - timedelta(days=n+1)
            if extracted_day == data:
                streak += 1
            else:
                break

    return StreakResult(days=streak, is_today_completed=is_today)