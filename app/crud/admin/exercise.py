# Third-party
from sqlalchemy.ext.asyncio import AsyncSession

# Models
from app.models import Exercise

# Schemas
from app.schemas import ExerciseCreate

async def create_exercise(
        db: AsyncSession,
        data: ExerciseCreate
) -> Exercise:
    """
    Create new exercise in database.

    Validation is already performed by ExerciseCreate schema before
    this function is called.

    Args:
        db: Database session
        data: Validated exercise data from ExerciseCreate schema

    Returns:
        Created Exercise model with generated ID and timestamps

    Note:
        - is_active defaults to True (database default)
        - added_at is set automatically by database
        - Topic is already normalized to title case by schema validator
    """
    new_exercise = Exercise(
        topic=data.topic,
        difficult_level=data.difficult_level,
        type=data.type,
        options=data.options,
        question_text=data.question_text,
        question_language=data.question_language,
        correct_answer=data.correct_answer,
        answer_language=data.answer_language,
        question_translation=data.question_translation,
        question_translation_language=data.question_translation_language
    )
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise)

    return new_exercise