from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.exercise import get_exercise
from app.models import User
from app.schemas.enums import LanguageLevelEnum
from app.schemas.exercise import ExerciseQuestion
from app.utils.validators import normalize_topic


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



