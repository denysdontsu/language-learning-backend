# Third-party
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# Cache
from app.cache import CacheKeys, cache_manager

# CRUD
from app.crud.admin.exercise import update_exercise, create_exercise

# Schemas
from app.schemas import ExerciseUpdate, ExerciseCreate, ExerciseRead, Options

# Utils
from app.utils.normalizers import normalize_topic
from app.utils.db_helpers import get_exercise_or_404
from app.utils.validators import (
    validate_exercise_options,
    validate_question_translation_pair,
    validate_translation_usage
)

async def create_exercise_service(
        db: AsyncSession,
        data: ExerciseCreate
) -> ExerciseRead:
    """
    Create new exercise.

    Invalidates all topics cache entries across all language pairs
    to ensure new exercise topics appear immediately.

    Args:
        db: Database session
        data: Exercise creation data

    Returns:
        ExerciseRead: Created exercise
    """
    new_exercise = await create_exercise(db, data)
    await db.commit()

    # Clear cache
    await cache_manager.delete_pattern(CacheKeys.topics_pattern())

    return ExerciseRead.model_validate(new_exercise)


async def update_exercise_service(
        db: AsyncSession,
        exercise_id: int,
        update_data: ExerciseUpdate
) -> ExerciseRead:
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
        Updated exercise pydentic model ExerciseRead

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
        return ExerciseRead.model_validate(exercise)

    # Normalize topic if provided
    if update_dict.get('topic'):
        update_dict['topic'] = normalize_topic(update_dict['topic'])
    raw_options = update_dict.get('options', exercise.options)
    merged_options = Options.model_validate(raw_options) if raw_options else None

    # Merge with existing data for validation
    merged_data = {
        'type': update_dict.get('type', exercise.type),
        'options': update_dict.get('options', merged_options),
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
    await db.commit()

    # Clear cache
    await cache_manager.delete_pattern(CacheKeys.topics_pattern())

    return ExerciseRead.model_validate(updated_exercise)