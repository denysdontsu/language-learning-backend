from fastapi import APIRouter

from app.api.dependencies import user_active_language_dependency, db_dependency
from app.crud.exercise import get_all_topics
from app.schemas.enums import LanguageLevelEnum
from app.schemas.exercise import ExerciseQuestion
from app.services.exercise import get_exercise_service

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
    """Get random exercise for practice."""
    return await get_exercise_service(db, user, topic, difficult_level, exclude_id)