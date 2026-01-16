from fastapi import APIRouter

from app.api.dependencies import user_active_language_dependency, db_dependency
from app.crud.exercise import get_all_topics

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