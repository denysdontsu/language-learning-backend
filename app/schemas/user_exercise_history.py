from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.exercise import ExerciseBrief
from app.schemas.user import UserBrief


class ExerciseHistoryBase(BaseModel):
    """Base user exercise history fields."""
    # Foreign Key
    exercise_id: int

    # Base info
    user_answer: str = Field(min_length=1)
    is_correct: bool
    time_spent_seconds: int = Field(gt=0)


class ExerciseHistoryCreate(ExerciseHistoryBase):
    """Schema for crete user exercise history."""
    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'exercise_id': 2,
                'user_answer': 'go',
                'is_correct': False,
                'time_spent_seconds': 43,
            }
        }
    )


class ExerciseHistoryUpdate(BaseModel):
    """Schema for update user exercise history (for admin)."""
    # Base info
    user_answer: str | None
    is_correct: bool | None
    time_spent_seconds: int | None = Field(None, gt=0)

    # Metadata
    completed_at: datetime | None

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'user_answer': 'went',
                'is_correct': True,
                'time_spent_seconds': 88,
                'completed_at': '2024-12-20T12:30:00Z'
            }
        }
    )


class ExerciseHistoryBrief(ExerciseHistoryBase):
    """Brief schema for user exercise history response."""
    id: int
    user_id: int
    completed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'user_id': 1,
                'exercise_id': 1,
                'user_answer': 'went',
                'is_correct': True,
                'time_spent_seconds': 43,
                'completed_at': '2024-12-20T12:30:00Z'
            }
        }
    )


class ExerciseHistoryRead(BaseModel):
    """Schema for user exercise history response."""
    id: int
    user: UserBrief
    exercise: ExerciseBrief
    user_answer: str
    is_correct: bool
    time_spent_seconds: int = Field(gt=0)
    completed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'user': {
                    'id': 1,
                    'email': 'example@mail.com',
                    'name': 'Denis',
                    'username': 'denisD',
                    'native_language': 'uk'
                },
                'exercise': {
                    'id': 1,
                    'topic': 'Past Simple Verbs',
                    'difficult_level': 'A2',
                    'type': 'multiple_choice',
                    'question_language': 'English',
                    'answer_language': 'Ukrainian'
                },
                'user_answer': 'went',
                'is_correct': True,
                'time_spent_seconds': 43,
                'completed_at': '2024-12-20T12:30:00Z'
            }
        }
    )