from fastapi import APIRouter, status

from app.api.dependencies import user_active_language_dependency, db_dependency
from app.crud.exercise import get_all_topics
from app.schemas.enums import LanguageLevelEnum
from app.schemas.exercise import ExerciseQuestion, ExerciseCorrectAnswer, ExerciseUserAnswer
from app.services.exercise import get_exercise_service, check_and_save_submission

router = APIRouter(prefix='/exercises', tags=['Exercises'])

@router.get('/topics',
           response_model=list[str],
           summary='Get available exercise topics')
async def get_topics(
        db: db_dependency,
        user: user_active_language_dependency
) -> list[str]:
    """
    Get list of available exercise topics for user's language pair.

    Returns topics where exercises can be in both directions:
    - Questions in native language, answers in learning language
    - Questions in learning language, answers in native language
    """
    return await get_all_topics(db, user)


@router.get('/next',
            response_model=ExerciseQuestion,
            summary='Get exercise by topic and difficult level')
async def get_exercise(
        db: db_dependency,
        user: user_active_language_dependency,
        topic: str,
        difficult_level: LanguageLevelEnum | None = None,
        exclude_id: int | None = None
) -> ExerciseQuestion:
    """
    Get random exercise for practice session with spaced repetition.

    Retrieves exercise matching user's language pair and criteria, applying
    intelligent filtering based on completion history.

    Query Parameters:
        topic: Exercise topic (required, case-insensitive, normalized to title case)
        difficult_level: CEFR difficulty level (A1-C2), defaults to user's active language level
        exclude_id: Exercise ID to skip (prevents immediate repeats in session)

    Spaced Repetition Logic:
        - Correct answers: 14-day exclusion (336 hours)
        - Skipped exercises: 3-day exclusion (72 hours)
        - Incorrect answers: Immediate retry allowed (no exclusion)

    Returns:
        Random exercise matching criteria with question text, options (if applicable),
        and instruction based on exercise type

    Raises:
        404: No exercises available for specified criteria
             Suggestions provided: try different difficulty, topic, or wait for timeout

    Example:
        GET /exercises/next?topic=conditions&difficult_level=B1&exclude_id=42
    """
    return await get_exercise_service(db, user, topic, difficult_level, exclude_id)


@router.post('/{exercise_id}/submit',
              response_model=ExerciseCorrectAnswer,
              status_code=status.HTTP_201_CREATED,
              summary='Submit exercise answer')
async def submit_exercise(
        db: db_dependency,
        user: user_active_language_dependency,
        exercise_id: int,
        data: ExerciseUserAnswer
) -> ExerciseCorrectAnswer:
    """
    Submit user's answer for an exercise and save to history.

    Validates the answer, determines correctness, and creates a new history
    record. Returns immediate feedback with correct answer and explanation
    (if available).

    Path Parameters:
    - exercise_id: ID of the exercise being answered

    Request Body:
    - user_answer: User's submitted answer
    - time_spent_seconds: Time taken to answer (in seconds)

    Returns:
        Result with correct answer, user's answer, status, and optional explanation

    Status Determination:
    - correct: User answer matches correct answer exactly
    - incorrect: User answer doesn't match but is not empty
    - skip: User answer is empty or whitespace only
    """
    return await check_and_save_submission(db, user.id, exercise_id, data)