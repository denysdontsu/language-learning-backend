import re

from pydantic_core.core_schema import ValidationInfo

from app.schemas.enums import ExerciseTypeEnum, ExerciseStatusEnum
from app.schemas.common import Options

# Reserved values that cannot be used in string fields
RESERVED_VALUES = {'none', 'null', 'true', 'false', 'admin'}


def validate_password_strength(
        password: str
) -> str:
    """Validate password contains letter and digit."""
    if password != password.strip():
        raise ValueError("Password cannot start or end with whitespace")
    if not re.search(r'[A-Za-z]', password):
        raise ValueError('Password must contain at least one letter')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')
    return password


def validate_question_translation_pair(
        question_translation: str,
        question_translation_language: str) -> None:

    """
    Validate that question translation and its language are both provided or both null.

    Rules:
    - Both fields must be set together, OR
    - Both fields must be null
    - Having only one field set is invalid

    Args:
        question_translation: Translation text (optional)
        question_translation_language: Language code of translation (optional)

    Raises:
        ValueError: If only one of the two fields is provided
    """
    if  (question_translation is None) != (question_translation_language is None):
        raise ValueError("Both 'question_translation' and 'question_translation_language' "
                         "must be provided together or both be null.")


def validate_exercise_options(
        exercise_type: ExerciseTypeEnum,
        options: Options | None
) -> None:
    """
    Validate that options are provided correctly based on exercise type.

    Rules:
    - MULTIPLE_CHOICE: Options REQUIRED (must have answer choices A, B, C, D)
    - SENTENCE_TRANSLATION: Options NOT allowed (no choices needed)
    - FILL_BLANK: Options NOT allowed (free text answer)

    Args:
        exercise_type: Type of exercise
        options: Answer options for multiple choice (optional)

    Raises:
        ValueError: If options usage doesn't match exercise type requirements
    """
    if exercise_type == ExerciseTypeEnum.MULTIPLE_CHOICE:
        if options is None:
            raise ValueError("'options' is required when exercise type is 'multiple_choice'")
    elif options is not None:
        raise ValueError(f"Exercise type '{exercise_type.value}' should not have options")


def validate_translation_usage(
        exercise_type: ExerciseTypeEnum,
        question_translation: str
) -> None:
    """
    Validate that question_translation is used appropriately for each exercise type.

    Rules:
    - SENTENCE_TRANSLATION: Translation NOT needed (correct_answer is already the translation)
    - FILL_BLANK: Translation REQUIRED (question and answer are in target language)
    - MULTIPLE_CHOICE: Translation REQUIRED (question and options are in target language)

    Args:
        exercise_type: Type of exercise
        question_translation: Translation text (optional)

    Raises:
        ValueError: If translation usage doesn't match exercise type requirements
    """
    if exercise_type == ExerciseTypeEnum.SENTENCE_TRANSLATION:
        if question_translation is not None:
            raise ValueError("Translation not needed for 'sentence_translation' type. "
                             "The correct_answer field already contains the translation."
            )
    elif exercise_type == ExerciseTypeEnum.FILL_BLANK:
        if question_translation is None:
            raise ValueError(
                "Translation required for 'fill_blank' type. "
                "Question is in target language, translation helps learners understand context."
            )
    elif exercise_type == ExerciseTypeEnum.MULTIPLE_CHOICE:
        if question_translation is None:
            raise ValueError(
                "Translation required for 'multiple_choice' type. "
                "Question is in target language, translation helps learners understand context."
            )


def validate_string_field(
        field: str | None,
        info: ValidationInfo
) -> str | None:
    """
    Validate and sanitize string field.

    Trims whitespace, checks for empty strings, and prevents
    reserved values (case-insensitive).

    Args:
        field: Field value to validate
        info: Pydantic validation info (contains field_name)

    Returns:
        str | None: Sanitized field value or None

    Raises:
        ValueError: If field is empty or contains reserved value
    """
    if field is None:
        return field

    # Convert to string and strip whitespace
    v = str(field).strip()

    # Check if empty after strip
    if not v:
        raise ValueError(f'{info.field_name} cannot be empty or whitespace only')

    # Check reserved values
    if v.lower() in RESERVED_VALUES:
        raise ValueError(f'{info.field_name} cannot be "{v}" (reserved value)')

    return v


def validate_exercise_status(
        status: ExerciseStatusEnum | None,
        user_answer: str | None
) -> None:
    """
    Validate consistency between exercise status and user answer.

    Business rules:
    - SKIP status requires empty user_answer (None or empty string)
    - CORRECT/INCORRECT status requires non-empty user_answer

    Args:
        status: Exercise completion status (correct/incorrect/skip)
        user_answer: User's submitted answer

    Raises:
        ValueError: If status and user_answer are inconsistent
    """
    # Normalize empty string to None for consistent checking
    answer = user_answer.strip() if user_answer else None

    if answer and status == ExerciseStatusEnum.SKIP:
        raise ValueError("'user_answer' must be empty for 'skip' status")
    elif not answer and status in (ExerciseStatusEnum.CORRECT, ExerciseStatusEnum.INCORRECT):
        raise ValueError(f"'user_answer' is required for '{status.value}' status")

