from datetime import datetime, timedelta, timezone
from typing import Literal, NamedTuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_exercise_history import get_exercise_history_by_user
from app.models import UserExerciseHistory
from app.schemas.enums import LanguageLevelEnum, ExerciseStatusEnum, LanguageEnum
from app.schemas.statistics import OverviewResponse, PerformanceResponse, DifficultyStats, TopicStats
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


async def get_performance_statistics(
        db: AsyncSession,
        user_id: int,
        language: LanguageEnum | None,
        period: Literal['7d', '30d', '3m', '1y', 'all'] = 'all',
) -> PerformanceResponse:
    """
    Get performance statistics by difficulty and topics.

    Calculates:
    - Accuracy and mastery status per CEFR level
    - Top 5 topics by accuracy
    - Weak topics needing practice

    Args:
        db: Database session
        user_id: User ID
        language: Optional language filter
        period: Time period for statistics

    Returns:
        PerformanceResponse with difficulty and topic statistics
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

    return _calculate_performance_statistics(history)


def _calculate_performance_statistics(
        history: list[UserExerciseHistory]
) -> PerformanceResponse:
    """
    Calculate performance statistics from exercise history.

    Aggregates:
    - Statistics per CEFR difficulty level
    - Top performing topics
    - Weak topics needing practice

    Args:
        history: List of user exercise history records

    Returns:
        PerformanceResponse with difficulty and topic statistics
    """
    by_difficulty = _calculate_by_difficulty(history)
    top_topics = _calculate_top_topics(history)
    weak_topics = _calculate_top_topics(
        history,
        best_first=False,
        min_total=20,
        max_accuracy=60.0
    )

    return PerformanceResponse(
        by_difficulty=by_difficulty,
        top_topics=top_topics,
        weak_topics=weak_topics
    )


def _calculate_by_difficulty(
        history: list[UserExerciseHistory],
) -> dict[str, DifficultyStats]:
    """
    Calculate statistics per CEFR difficulty level.

    For each level (A1-C2):
    - Accuracy from answered exercises
    - Total answered count
    - Mastered: accuracy >= 80% and total >= 100
    - In progress: total > 10 and not mastered

    Args:
        history: List of user exercise history records

    Returns:
        Dict mapping level name (A1, A2, ...) to stats
    """
    by_level = {}

    for level in LanguageLevelEnum:
        # Calculate accuracy for this level
        accuracy_stats = _calculate_accuracy_stats(history, level)

        # Determine master status
        mastered = (accuracy_stats.accuracy_percent >= 80
                    and accuracy_stats.total_answered >= 100)

        # Determine if in progress
        in_progress = (accuracy_stats.total_answered > 10
                    and not mastered)

        stats = DifficultyStats(
            accuracy=accuracy_stats.accuracy_percent,
            total_answered=accuracy_stats.total_answered,
            mastered=mastered,
            in_progress=in_progress
        )

        by_level[level.value] = stats

    return by_level


def _calculate_top_topics(
        history: list[UserExerciseHistory],
        limit: int = 5,
        best_first: bool = True,
        min_total: int = 0,
        max_accuracy: float | None = None
) -> list[TopicStats]:
    """
    Calculate top or weak topics with optional filtering.

    Returns top N topics sorted by accuracy. Can filter by minimum
    exercise count and maximum accuracy for finding weak topics.

    Args:
        history: List of user exercise history records
        limit: Maximum number of topics to return (default: 5)
        best_first: Sort order - True for best first, False for worst first
        min_total: Minimum answered exercises threshold (for weak topics)
        max_accuracy: Maximum accuracy threshold (for weak topics)

    Returns:
        List of TopicStats sorted by accuracy
    """
    if not history:
        return []

    # Aggregate by topic
    topics = {}
    for h in history:
        topic = h.exercise.topic

        if topic not in topics:
            topics[topic] = {'total': 0, 'correct': 0}

        # Count only answered (exclude skipped)
        if h.status != ExerciseStatusEnum.SKIP:
            topics[topic]['total'] += 1

            if h.status == ExerciseStatusEnum.CORRECT:
                topics[topic]['correct'] += 1

    # Calculate accuracy for all topics
    for topic, data in topics.items():
        if data['total'] == 0:
            continue

        data['accuracy'] = (
                data['correct'] / data['total'] * 100
                if data['total'] > 0 else 0.0
        )

    # Apply filters (for weak topics)
    if min_total > 0 or max_accuracy is not None:
        topics = {
            topic: data
            for topic, data in topics.items()
            if (
                data['total'] >= min_total
                and (max_accuracy is None or data['accuracy'] <= max_accuracy)
            )
        }

    # Sort by accuracy (descending) and take top N
    sorted_top_topics = sorted(
        topics.items(),
        key=lambda i: i[1]['accuracy'],
        reverse=best_first
    )[:limit]

    # Build result with status calculation (only for selected topics)
    result = []
    for topic, stats in sorted_top_topics:
        accuracy = stats['accuracy']
        if accuracy >= 85:
            status = 'mastered'
        elif accuracy >= 70:
            status = 'good'
        elif accuracy >= 50:
            status = 'learning'
        else:
            status = 'needs_practice'

        result.append(
            TopicStats(
                name=topic,
                accuracy=stats['accuracy'],
                total_answered=stats['total'],
                status=status
            )
        )

    return result