from sqlalchemy import or_, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Exercise, User


async def get_all_topics(
        db: AsyncSession,
        user: User
) -> list[str]:
    """
    Get all unique exercise topics available for user's language pair.

    Returns topics where exercises can be:
    - Native → Learning language
    - Learning → Native language

    Args:
        db: Database session
        user: User with loaded active_learning_language

    Returns:
        List of unique topic names sorted alphabetically
    """
    stmt = (select(Exercise.topic)
        .distinct()
        .where(
            or_(
                and_(
                    Exercise.question_language == user.native_language,
                    Exercise.answer_language == user.active_learning_language.language
                ),
                and_(Exercise.question_language == user.active_learning_language.language,
                     Exercise.answer_language == user.native_language
                ),
            )
        )
        .order_by(Exercise.topic)
    )
    result = await db.execute(stmt)
    topics = result.scalars().all()
    return list(topics)