# Standard library
import pytest
from contextlib import nullcontext as does_not_raise

# Schemas
from app.schemas import ExerciseTypeEnum, ExerciseStatusEnum

# Utils
from app.utils.validators import (
    validate_password_strength,
    validate_question_translation_pair,
    validate_exercise_options,
    validate_translation_usage,
    validate_exercise_status,
    _validate_string_value
)

# Tests
from test_helpers import OPTIONS


@pytest.mark.parametrize(
    'password, expected, expectation',
    [
        (' password1 ', None, pytest.raises(
            ValueError, match='Password cannot start or end with whitespace')),
        ('12345678', None, pytest.raises(
            ValueError, match='Password must contain at least one letter')),
        ('password', None, pytest.raises(
            ValueError, match='Password must contain at least one digit')),
        ('password1', 'password1', does_not_raise()),
        ('pass word1', 'pass word1', does_not_raise())
    ],
    ids=[
        'cannot_start_or_end_with_whitespace',
        'cannot_contains_only_digital',
        'cannot_contains_only_letter',
        'correct_password',
        'password_with_space_is_valid'
    ]
)
def test_validate_password_strength(password, expected, expectation):
    with expectation:
        result = validate_password_strength(password)
        assert result == expected


@pytest.mark.parametrize(
    'question_translation, question_translation_language, expect, expectation',
    [
        ('uk', None, None, pytest.raises(ValueError, match='must be provided together or both be null')),
        (None, 'uk', None, pytest.raises(ValueError, match='must be provided together or both be null')),
        (None, None, None, does_not_raise()),
        ('uk', 'uk', None, does_not_raise())
    ],
    ids=[
        'missing_language',
        'missing_translation',
        'both_missing',
        'both_present',
    ]
)
def test_validate_question_translation_pair(
        question_translation,
        question_translation_language,
        expect,
        expectation
):
    with expectation:
        validate_question_translation_pair(
            question_translation,
            question_translation_language
        )


@pytest.mark.parametrize(
    'exercise_type, options, correct_answer, expectation',
    [
        (ExerciseTypeEnum.MULTIPLE_CHOICE, None, None, pytest.raises(
            ValueError, match="'options' is required when exercise type is 'multiple_choice'")),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, OPTIONS, 'have', pytest.raises(
            ValueError, match="Correct answer 'have' not found in options.")),
        (ExerciseTypeEnum.SENTENCE_TRANSLATION, OPTIONS, None, pytest.raises(
            ValueError, match="Exercise type 'sentence_translation' should not have options")),
        (ExerciseTypeEnum.FILL_BLANK, OPTIONS, None, pytest.raises(
            ValueError, match="Exercise type 'fill_blank' should not have options")),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, OPTIONS, None, pytest.raises(
            ValueError, match="not found in options")),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, OPTIONS, 'go', does_not_raise())
    ],
    ids=[
        'multiple_choice_missing_options',
        'correct_answer_not_in_options',
        'sentence_translation_with_options',
        'fill_blank_with_options',
        'multiple_choice_with_none_answer',
        'valid_multiple_choice',
    ]
)
def test_validate_exercise_options(
        exercise_type,
        options,
        correct_answer,
        expectation
):
    with expectation:
        validate_exercise_options(
            exercise_type,
            options,
            correct_answer
        )


@pytest.mark.parametrize(
    'exercise_type, question_translation, expectation',
    [
        (ExerciseTypeEnum.SENTENCE_TRANSLATION, 'Hello word', pytest.raises(
            ValueError, match="Translation not needed for 'sentence_translation' type.")),
        (ExerciseTypeEnum.FILL_BLANK, None, pytest.raises(
            ValueError, match="Translation required for 'fill_blank' type.")),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, None, pytest.raises(
            ValueError, match="Translation required for 'multiple_choice' type.")),
        (ExerciseTypeEnum.SENTENCE_TRANSLATION, None, does_not_raise()),
        (ExerciseTypeEnum.FILL_BLANK, 'Hello word', does_not_raise()),
        (ExerciseTypeEnum.MULTIPLE_CHOICE, 'Hello word', does_not_raise())
    ],
    ids=[
        'sentence_translation_with_translation',
        'fill_blank_without_translation',
        'multiple_choice_without_translation',
        'sentence_translation_without_translation',
        'fill_blank_with_translation',
        'multiple_choice_with_translation'
    ]
)
def test_validate_translation_usage(exercise_type, question_translation, expectation):
    with expectation:
        validate_translation_usage(
            exercise_type,
            question_translation
        )


@pytest.mark.parametrize(
    'field, field_name, expected, expectation',
    [
        (None, 'username', None, does_not_raise()),
        ('  ', 'username', None, pytest.raises(
            ValueError, match='cannot be empty or whitespace only')),
        ('admin', 'username', None, pytest.raises(
            ValueError, match='reserved value')),
        ('  hello  ', 'username', 'hello', does_not_raise()),
        ('null', 'topic', None, pytest.raises(
            ValueError, match='reserved value')),
    ],
    ids=[
        'none_returns_none',
        'whitespace_only_raises',
        'reserved_value_raises',
        'strips_whitespace',
        'null_is_reserved',
    ]
)
def test_validate_string_field(field, field_name, expected, expectation):
    with expectation:
        result = _validate_string_value(field, field_name)
        if expected is not None:
            assert result == expected


@pytest.mark.parametrize(
    'status, user_answer, expectation',
    [
        (ExerciseStatusEnum.SKIP, 'answer', pytest.raises(
            ValueError, match="'user_answer' must be empty for 'skip' status")),
        (ExerciseStatusEnum.CORRECT, None, pytest.raises(
            ValueError, match="'user_answer' is required for 'correct' status")),
        (ExerciseStatusEnum.INCORRECT, None, pytest.raises(
            ValueError, match="'user_answer' is required for 'incorrect' status")),
        (ExerciseStatusEnum.CORRECT, '   ', pytest.raises(
            ValueError, match="'user_answer' is required for 'correct' status")),
        (ExerciseStatusEnum.SKIP, None, does_not_raise()),
        (ExerciseStatusEnum.CORRECT, 'answer', does_not_raise()),
        (ExerciseStatusEnum.INCORRECT, 'answer', does_not_raise()),
    ],
    ids=[
        'skip_status_with_answer',
        'correct_status_with_empty_answer',
        'incorrect_status_with_empty_answer',
        'correct_status_with_blank_answer',
        'skip_status_with_empty_answer',
        'correct_status_with_answer',
        'incorrect_status_with_answer'
    ]
)
def test_validate_exercise_status(status, user_answer, expectation):
    with expectation:
        validate_exercise_status(status, user_answer)