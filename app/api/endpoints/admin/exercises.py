from fastapi import APIRouter, status

from app.api.dependencies import db_dependency
from app.crud.admin.exercise import create_exercise
from app.schemas.exercise import ExerciseRead, ExerciseCreate


router = APIRouter(
    prefix='/exercises',
    tags=['Admin / Exercises'],
)

@router.post('/',
             response_model=ExerciseRead,
             status_code=status.HTTP_201_CREATED,
             summary='Create new exercise')
async def create_exercise_endpoint(
        db: db_dependency,
        data: ExerciseCreate
) -> ExerciseRead:
    """
    Create a new exercise.

    Admin only. Creates exercise with automatic validation of:
    - Options for multiple_choice type (required)
    - Translation pair completeness (both fields or both None)
    - Translation usage rules (not allowed for fill_blank)
    - Topic normalization to title case

    Request Body:
        ExerciseCreate with exercise data

    Returns:
        Created exercise with generated ID and metadata

    Raises:
        400: Validation error (invalid options, translation rules)
        403: Non-admin user attempting access
    """
    created_exercise = await create_exercise(db, data)

    return ExerciseRead.model_validate(created_exercise)