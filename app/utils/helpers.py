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
    for key, value in options.items():
        if value == correct_answer:
            return key

    return None