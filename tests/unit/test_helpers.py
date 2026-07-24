# Standard library
from contextlib import nullcontext as does_not_raise
from datetime import date, datetime, timezone

# Third-party
import pytest
from fastapi import HTTPException

# Schemas
from app.schemas import ExerciseTypeEnum
from app.schemas.common import Options

# Utils
from app.utils.helpers import get_correct_option_key, parse_date_range

OPTIONS = Options.model_validate({'A': 'go', 'B': 'went', 'C': 'gone', 'D': 'going'})


@pytest.mark.parametrize(
    'exercise_type, options, correct_answer, expected',
    [
        (ExerciseTypeEnum.MULTIPLE_CHOICE, OPTIONS, 'go', 'A'),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, OPTIONS, 'have', None),
        (ExerciseTypeEnum.SENTENCE_TRANSLATION, None, 'go', None),
        (ExerciseTypeEnum.FILL_BLANK, OPTIONS, 'go', None),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, None, 'go', None),
    ],
    ids=[
        'multiple_choice_correct_answer_returns_key',
        'multiple_choice_answer_not_in_options_returns_none',
        'sentence_translation_always_returns_none',
        'fill_blank_always_returns_none',
        'multiple_choice_no_options_returns_none',
    ]
)
def test_get_correct_option_key(exercise_type, options, correct_answer, expected):
    result = get_correct_option_key(exercise_type, options, correct_answer)
    assert result == expected


@pytest.mark.parametrize(
    'period, date_from, date_to, expected, expectation',
    [
        (None, date(2000, 9, 18), date(1999, 9, 18), None,
            pytest.raises(HTTPException, match='date_from cannot be after date_to')),
        (None, date(2030, 9, 18), None, None,
            pytest.raises(HTTPException, match='date_from cannot be in the future')),
        (None, None, None, None, does_not_raise()),
        (None, date(1999, 9, 18), date(2000, 9, 18), (
            datetime(1999, 9, 18, 0, 0, tzinfo=timezone.utc),
            datetime(2000, 9, 18, 23, 59, 59, 999999, tzinfo=timezone.utc)
        ), does_not_raise()),
        ('all', None, None, (None, None), does_not_raise()),
        ('7d', None, None, None, does_not_raise()),
    ],
    ids=[
        'date_to_before_date_from',
        'date_from_in_future',
        'no_dates_no_period_returns_default',
        'valid_date_range',
        'period_all_returns_none',
        'period_7d_returns_range',
    ]
)
def test_parse_date_range(period, date_from, date_to, expected, expectation):
    with expectation:
        result = parse_date_range(period, date_from, date_to)
        if expected is not None:
            assert result == expected
        else:
            assert result is not None