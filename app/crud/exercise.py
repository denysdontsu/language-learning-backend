from datetime import timedelta

from sqlalchemy import or_, and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Exercise, User, UserExerciseHistory
from app.schemas.enums import (
    LanguageLevelEnum,
    LanguageEnum,
    ExerciseStatusEnum,
    ExerciseTypeEnum)


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


async def get_exercise(
        db: AsyncSession,
        user_id: int,
        topic: str,
        difficult_level: LanguageLevelEnum,
        native_lang: LanguageEnum,
        active_lang: LanguageEnum,
        exclude_id: int | None
) -> Exercise | None:
    """
    Get random exercise matching criteria, excluding recently completed.

    Exclusion rules:
    - Correct answer: exclude for 14 days
    - Skipped: exclude for 3 days
    - Incorrect: no exclusion (can retry immediately)

    Args:
        db: Database session
        user_id: User ID for history filtering
        topic: Exercise topic
        difficult_level: Exercise difficulty
        native_lang: User's native language
        active_lang: User's active learning language
        exclude_id: Exercise ID to exclude (e.g., last shown)

    Returns:
        Random exercise or None if no exercises available
    """
    # Subquery: exercises with active timeout
    timeout_subquery = (
        select(UserExerciseHistory.exercise_id)
        .where(
            UserExerciseHistory.user_id == user_id,
            or_(
                # Correct: exclude for 14 days
                and_(
                    UserExerciseHistory.status == ExerciseStatusEnum.CORRECT,
                    UserExerciseHistory.completed_at >=
                        func.now() - timedelta(hours=ExerciseStatusEnum.CORRECT.exclude_at_hours)
                ),
                # Skip: exclude for 3 days
                and_(
                    UserExerciseHistory.status == ExerciseStatusEnum.SKIP,
                    UserExerciseHistory.completed_at
                        >= func.now() - timedelta(hours=ExerciseStatusEnum.SKIP.exclude_at_hours)
                )
            )
        )
    )

    # Main query
    stmt = (
        select(Exercise)
        .where(
            # Active exercises only
            Exercise.is_active == True,

            # Match topic and difficulty
            Exercise.topic == topic,
            Exercise.difficult_level == difficult_level,

            # Language matching based on exercise type
            or_(
                # sentence_translation: bidirectional
                and_(
                    Exercise.type == ExerciseTypeEnum.SENTENCE_TRANSLATION,
                    or_(
                        and_(
                            Exercise.question_language == native_lang,
                            Exercise.answer_language == active_lang
                        ),
                        and_(
                            Exercise.question_language == active_lang,
                            Exercise.answer_language == native_lang
                        )
                    )
                ),

                # fill_blank / multiple_choice: question on active language
                and_(
                    Exercise.type.in_([
                        ExerciseTypeEnum.FILL_BLANK,
                        ExerciseTypeEnum.MULTIPLE_CHOICE
                    ]),
                    Exercise.question_language == active_lang,
                    Exercise.question_translation_language == native_lang
                )
            ),

            # Exclude exercises with active timeout
            Exercise.id.not_in(timeout_subquery),

            # Exclude last shown exercise
            Exercise.id != exclude_id if exclude_id else True
        )
        .order_by(func.random())
        .limit(1)
    )
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_exercise_by_id(
        db: AsyncSession,
        exercise_id: int
) -> Exercise | None:
    """
    Get exercise by ID.

    Args:
        db: Database session
        exercise_id: Exercise ID to retrieve

    Returns:
        Exercise if found, None otherwise
    """
    stmt = (select(Exercise).where(
            Exercise.id == exercise_id
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()