from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.exercise import get_exercise, get_exercise_by_id
from app.crud.user_exercise_history import create_user_history
from app.models import User
from app.schemas.enums import LanguageLevelEnum, ExerciseStatusEnum
from app.schemas.exercise import ExerciseQuestion, ExerciseUserAnswer, ExerciseCorrectAnswer
from app.schemas.user_exercise_history import ExerciseHistoryCreate
from app.utils.normalizers import normalize_topic, normalize_answer


async def get_exercise_service(
        db: AsyncSession,
        user: User,
        topic: str,
        difficult_level: LanguageLevelEnum | None,
        exclude_id: int | None
) -> ExerciseQuestion:
    """
    Get random exercise for user practice session.

    Selects exercise matching specified criteria with intelligent filtering:
    - Bidirectional language pair matching (native ↔ learning)
    - Spaced repetition exclusion (recently completed exercises)
    - Optional difficulty override (defaults to user's active language level)

    Args:
        db: Database session
        user: Current user with active learning language
        topic: Exercise topic (normalized to title case)
        difficult_level: Difficulty level override (None = user's level)
        exclude_id: Exercise ID to skip (e.g., previously shown)

    Returns:
        ExerciseQuestion: Random exercise matching criteria

    Raises:
        HTTPException 404: No exercises available with suggestions
    """
    # Normalize topic
    topic = normalize_topic(topic)

    # Default difficulty to user's level
    if not difficult_level:
            difficult_level = user.active_learning_language.level

    # Get exercise
    exercise = await get_exercise(
        db,
        user.id,
        topic,
        difficult_level,
        user.native_language,
        user.active_learning_language.language,
        exclude_id
    )
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'message': f'No exercises available for topic "{topic}" at level {difficult_level.value}',
                'suggestions': [
                    'Try changing difficulty level',
                    'Try different topic',
                    'Come back later (some exercises may be on timeout)'
                ]
            }
        )

    return  ExerciseQuestion.model_validate(exercise)


async def check_and_save_submission(
        db: AsyncSession,
        user_id: int,
        exercise_id: int,
        data: ExerciseUserAnswer
) -> ExerciseCorrectAnswer:
    """
    Check exercise answer and save submission to history.

    Validates user's answer against correct answer, determines status,
    and creates history record for spaced repetition tracking.

    Args:
        db: Database session
        user_id: User ID submitting the answer
        exercise_id: Exercise being answered
        data: User's answer and time spent

    Returns:
        ExerciseCorrectAnswer with result and feedback

    Raises:
        HTTPException 404: If exercise not found
    """
    # Get exercise
    exercise = await get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Exercise with id {exercise_id} not found'
        )

    user_answer_normalized = normalize_answer(data.user_answer)
    correct_answer_normalized = normalize_answer(exercise.correct_answer)

    # Determine status and correctness
    if not user_answer_normalized:
        answer_status = ExerciseStatusEnum.SKIP
        is_correct = False
    elif user_answer_normalized == correct_answer_normalized:
        answer_status = ExerciseStatusEnum.CORRECT
        is_correct = True
    else:
        answer_status = ExerciseStatusEnum.INCORRECT
        is_correct = False

    # Create history record
    new_history = ExerciseHistoryCreate(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=data.user_answer if user_answer_normalized else None,
        status=answer_status,
        time_spent_seconds=data.time_spent_seconds
    )
    await create_user_history(db, new_history)

    # Build response
    response_model = ExerciseCorrectAnswer(
        id=exercise.id,
        topic=exercise.topic,
        difficult_level=exercise.difficult_level,
        type=exercise.type,
        question_text=exercise.question_text,
        options=exercise.options,
        correct_answer=exercise.correct_answer,
        user_answer=data.user_answer,
        is_correct=is_correct,
        status=answer_status,
        question_translation=exercise.question_translation,
        explanation=None # AI-generated explanation in language_app v2
    )

    return response_model