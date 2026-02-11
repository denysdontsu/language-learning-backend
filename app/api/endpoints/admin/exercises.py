# Standard library
from datetime import date
from typing import Literal

# Third-party
from fastapi import APIRouter, status, Query

# Dependencies
from app.api.dependencies import db_dependency, pagination_dependency

# CRUD
from app.crud.admin.exercise import create_exercise, get_exercises

# Schemas
from app.schemas import (
    ExerciseRead,
    ExerciseCreate,
    ExerciseBriefForHistory,
    LanguageEnum,
    LanguageLevelEnum,
    ExerciseTypeEnum
)

# Utils
from app.utils.helpers import parse_date_range
from app.utils.normalizers import normalize_topic

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


router.get('/',
           response_model=list[ExerciseBriefForHistory],
           summary='Get exercises list with filtering')
async def get_exercises_endpoint(
        db: db_dependency,
        pagination: pagination_dependency,

        # Search
        search: str | None = Query(
            None,
            description='Search in question and answer text',
            min_length=2,
            max_length=100
        ),

        # Filters
        topic: str | None = Query(
            None,
            description='Filter by topic (exact match)'
        ),
        difficult_level: LanguageLevelEnum | None = Query(
            None,
            description='Filter by difficulty level (A1 - C2)'
        ),
        exercise_type: ExerciseTypeEnum | None = Query(
            None,
            description='Filter by exercise type'
        ),
        question_language: LanguageEnum | None = Query(
            None,
            description='Filter by questing language'
        ),
        answer_language: LanguageEnum | None = Query(
            None,
            description='Filter by answer language'
        ),
        is_active: bool = Query(
            None,
            description='Filter by active status (null = all)'
        ),

        # Date filters
        date_from: date | None = Query(
            None,
            description='Created after date (YYYY-MM-DD, inclusive)'),
        date_to: date | None = Query(
            None,
            description='Created before date (YYYY-MM-DD, inclusive)'
        ),

        # Sorting
        order: Literal['asc', 'desc'] = Query(
            'desc',
            description='Sort order by creation date (ascending or descending)'
        )
) -> list[ExerciseBriefForHistory]:
    """
    Get paginated exercises list with filtering.

    Admin only. Returns exercises matching specified criteria.

    Search:
        - Searches in question_text and correct_answer
        - Case-insensitive partial match (ILIKE)
        - Minimum 2 characters required

    Filters:
        - topic: Exercise topic (e.g., 'grammar', 'vocabulary')
        - difficult_level: CEFR level (A1, A2, B1, B2, C1, C2)
        - type: Exercise type (fill_blank, multiple_choice, etc.)
        - question_language: Language of the question
        - answer_language: Language of the answer
        - is_active: Active status (true/false/null for all)
        - date_from: Show exercises created after this date
        - date_to: Show exercises created before this date

    Pagination:
        - limit: Max records to return (from pagination dependency)
        - offset: Records to skip (from pagination dependency)

    Sorting:
        - order: Sort by added_at timestamp (asc/desc, default: desc)

    Returns:
        List of exercises with brief information (may be empty)
    """
    offset, limit = pagination
    date_from, date_to = parse_date_range(None, date_from, date_to)
    normalized_topic = normalize_topic(topic) if topic else None

    exercises = await get_exercises(
        db,
        search,
        normalized_topic,
        difficult_level,
        exercise_type,
        question_language,
        answer_language,
        date_from,
        date_to,
        is_active,
        order,
        limit,
        offset
    )

    return [ExerciseBriefForHistory.model_validate(exercise) for exercise in exercises]
