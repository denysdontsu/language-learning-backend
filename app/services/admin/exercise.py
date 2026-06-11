# Third-party
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# CRUD
from app.crud.admin.exercise import update_exercise

# Model
from app.models import Exercise

# Schemas
from app.schemas import ExerciseUpdate

# Utils
from app.utils.db_helpers import get_exercise_or_404
from app.utils.validators import (
    validate_exercise_options,
    validate_question_translation_pair,
    validate_translation_usage
)


async def update_exercise_service(
        db: AsyncSession,
        exercise_id: int,
        update_data: ExerciseUpdate
) -> Exercise:
    """
    Update exercise with validation.

    Performs partial update with business logic validation.
    Merges update data with existing exercise to validate
    consistency before applying changes to database.

    Validation logic:
    1. Merge partial updates with existing data
    2. Validate options (required for multiple_choice)
    3. Validate translation pairs (both fields required)
    4. Validate translation usage (only for translation types)
    5. Normalize topic if provided
    6. Update database (only if validation passes)

    Args:
        db: Database session
        exercise_id: Exercise ID to update
        update_data: Partial update data (all fields optional)

    Returns:
        Updated exercise ORM model

    Raises:
        HTTPException 404: Exercise not found
        HTTPException 400: Validation error

    Examples:
        # Update single field
        await update_exercise_service(db, 123, ExerciseUpdate(difficult_level="B2"))

        # Update multiple fields
        await update_exercise_service(db, 123, ExerciseUpdate(
            question_text="New question",
            correct_answer="New answer"
        ))
    """
    exercise = await get_exercise_or_404(db, exercise_id)

    # Extract only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return exercise

    # Normalize topic if provided
    if update_dict.get('topic'):
        from app.utils.normalizers import normalize_topic
        update_data['topic'] = normalize_topic(update_data['topic'])

    # Merge with existing data for validation
    merged_data = {
        'type': update_dict.get('type', exercise.type),
        'options': update_dict.get('options', exercise.options),
        'correct_answer': update_dict.get('correct_answer', exercise.correct_answer),
        'question_translation': update_dict.get('question_translation', exercise.question_translation),
        'question_translation_language': update_dict.get('question_translation_language', exercise.question_translation_language),
    }

    try:
        # Validate options
        validate_exercise_options(
            merged_data['type'],
            merged_data['options'],
            merged_data['correct_answer']
        )

        # Validate translations
        validate_question_translation_pair(
            merged_data['question_translation'],
            merged_data['question_translation_language']
        )

        # Validate translation usage
        validate_translation_usage(
            merged_data['type'],
            merged_data['question_translation']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Update only provided fields
    updated_exercise = await update_exercise(db, exercise, update_dict)

    return updated_exercise