from datetime import date, datetime, timezone, timedelta, time

from app.schemas.enums import ExerciseTypeEnum
from app.schemas.common import Options


def get_correct_option_key(
        exercise_type: ExerciseTypeEnum,
        options: Options | None,
        correct_answer: str
) -> str | None:
    """
    Get option key (A, B, C, D) for correct answer in multiple choice.

    Args:
        exercise_type: Type of exercise
        options: Exercise options (for multiple_choice only)
        correct_answer: Correct answer text

    Returns:
        Option key ('A', 'B', 'C', or 'D') or None
    """
    if exercise_type != ExerciseTypeEnum.MULTIPLE_CHOICE:
        return None

    if not options:
        return None

    # Find key by value
    options = Options.model_dump(options)
    for key, value in options.items():
        if value == correct_answer:
            return key

    return None


def parse_date_range(
        period: str | None,
        date_from: date | None,
        date_to: date | None
) -> tuple[datetime | None, datetime | None]:
    """
    Parse date range from period or custom dates
    and convert to UTC datetime.

    Priority:
    1. period (if set) - returns calculated range
    2. date_from/date_to (if set) - returns as-is
    3. None - returns default (last 30 days)

    Args:
        period: Quick period selector
        date_from: Custom start date
        date_to: Custom end date

    Returns:
        Tuple of (start_datetime_utc, end_datetime_utc)
        Both in UTC timezone
    """
    now_utc = datetime.now(timezone.utc)

    # Priority 1: period
    if period:
        if period == 'all':
            return None, None

        # Calculate days
        period_days = {
            '7d': 7,
            '30d': 30,
            '3m': 90,
            '1y': 365
        }

        days = period_days.get(period, 30)
        start_utc = now_utc - timedelta(days=days)

        start_utc = start_utc.replace(hour=0, minute=0, second=0, microsecond=0)

        return start_utc, now_utc

    # Priority 2: custom dates
    if date_from or date_to:
        start_utc = None
        end_utc = None

        if date_from:
            start_utc = datetime.combine(date_from, time.min, tzinfo=timezone.utc)

        if date_to:
            end_utc = datetime.combine(date_to, time.max, tzinfo=timezone.utc)

        return start_utc, end_utc

    # Priority 3: default (last 30 days)
    default_start = now_utc - timedelta(days=30)
    default_start = default_start.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return default_start, now_utc