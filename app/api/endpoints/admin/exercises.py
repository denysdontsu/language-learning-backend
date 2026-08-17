# Standard library
from datetime import date
from typing import Literal

# Third-party
from fastapi import APIRouter, status, Query

# Dependencies
from app.api.dependencies import db_dependency, pagination_dependency

# CRUD
from app.crud.admin.exercise import get_exercises, get_exercise_stats

# Schemas
from app.schemas import (
    ExerciseRead,
    ExerciseCreate,
    ExerciseBriefForHistory,
    ExerciseReadWithStats,
    ExerciseUpdate,
    LanguageEnum,
    LanguageLevelEnum,
    ExerciseTypeEnum
)

# Services
from app.services.admin.exercise import (
    update_exercise_service,
    create_exercise_service
)

# Utils
from app.utils.helpers import parse_date_range
from app.utils.normalizers import normalize_topic
from app.utils.db_helpers import get_exercise_or_404


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
    created_exercise = await create_exercise_service(db, data)

    return ExerciseRead.model_validate(created_exercise)


@router.get('/',
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


@router.get('/{exercise_id}',
            response_model=ExerciseReadWithStats,
            summary='Get detailed exercise schemas with all fields and statistics')
async def get_exercise_with_stats_endpoint(
        db: db_dependency,
        exercise_id: int
) -> ExerciseReadWithStats:
    """
    Get detailed exercise information with usage statistics.

    Admin only. Returns complete exercise data including all fields
    and aggregated usage statistics from user attempts.

    Statistics include:
    - Total attempts and unique users
    - Correct/incorrect/skipped counts
    - Accuracy rate (percentage of correct answers)
    - Average completion time (excluding skips)
    - Last usage timestamp

    Path Parameters:
        exercise_id: Exercise ID to retrieve

    Returns:
        Complete exercise with statistics (stats may be None if never attempted)

    Raises:
        404: Exercise not found
    """
    # Get exercise
    exercise = await get_exercise_or_404(db, exercise_id)

    # Get stats
    exercise_stats = await get_exercise_stats(db, exercise_id)

    # Combine into response
    exercise_dict = exercise.__dict__.copy()
    exercise_dict['stats'] = exercise_stats

    return ExerciseReadWithStats.model_validate(exercise_dict)


@router.patch('/{exercise_id}',
              response_model=ExerciseRead,
              summary='Update exercise')
async def update_exercise_endpoint(
        db: db_dependency,
        exercise_id: int,
        data: ExerciseUpdate
) -> ExerciseRead:
    """
    Update exercise fields.

    Admin only. Allows partial updates of exercise data.
    All fields are optional - only provided fields will be updated.

    Validation rules:
    - Options required for multiple_choice type
    - Correct answer must match one of the options (if provided)
    - Translation pairs must be complete (both text and language)
    - Translations only allowed for translation exercise types
    - Topic normalized automatically (lowercase, underscores)

    Path Parameters:
        exercise_id: Exercise ID to update

    Request Body:
        ExerciseUpdate with fields to update (all optional):
        - topic: Exercise topic
        - difficult_level: CEFR level (A1-C2)
        - type: Exercise type
        - question_text: Question content
        - question_language: Question language
        - correct_answer: Correct answer
        - answer_language: Answer language
        - options: Answer options (for multiple_choice)
        - question_translation: Translation of question
        - question_translation_language: Translation language
        - explanation: Learning hint (optional)
        - is_active: Active status

    Returns:
        Updated exercise with all fields

    Raises:
        404: Exercise not found
        400: Validation error (invalid options, translations, etc.)
    """
    updated_exercise = await update_exercise_service(db, exercise_id, data)

    return ExerciseRead.model_validate(updated_exercise)