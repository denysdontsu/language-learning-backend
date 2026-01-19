from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.schemas.enums import ExerciseStatusEnum
from app.schemas.exercise import ExerciseBrief
from app.schemas.user import UserBrief
from app.utils.validators import validate_exercise_status


class ExerciseHistoryBase(BaseModel):
    """Base user exercise history fields."""
    # Foreign Key
    user_id: int
    exercise_id: int

    # Base info
    user_answer: str | None = None
    status: ExerciseStatusEnum
    time_spent_seconds: int = Field(ge=0)


class ExerciseHistoryCreate(ExerciseHistoryBase):
    """Schema for crete user exercise history."""
    model_config = ConfigDict(
        json_schema_extra={
            'example': [
                {
                    'user_is': 1,
                    'exercise_id': 2,
                    'user_answer': 'go',
                    'status': 'incorrect',
                    'time_spent_seconds': 43,
                },
                {
                    'user_is': 1,
                    'exercise_id': 2,
                    'user_answer': None,
                    'status': 'skip',
                    'time_spent_seconds': 43,
                }
            ]
        }
    )

    @model_validator(mode='after')
    def validate_status(self) -> Self:
        """Validate that status and user_answer are consistent."""
        validate_exercise_status(self.status, self.user_answer)
        return self


class ExerciseHistoryUpdate(BaseModel):
    """Schema for update user exercise history (for admin).

    Note: No status validation here since fields are optional
    and can be updated independently.
    """
    # Base info
    user_answer: str | None
    status: ExerciseStatusEnum | None
    time_spent_seconds: int | None = Field(None, ge=0)

    # Metadata
    completed_at: datetime | None

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'user_answer': 'went',
                'status': 'correct',
                'time_spent_seconds': 88,
                'completed_at': '2024-12-20T12:30:00Z'
            }
        }
    )


class ExerciseHistoryBrief(ExerciseHistoryBase):
    """Brief schema for user exercise history response."""
    id: int
    completed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'user_id': 1,
                'exercise_id': 1,
                'user_answer': 'went',
                'status': 'correct',
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
    status: ExerciseStatusEnum
    time_spent_seconds: int = Field(ge=0)
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
                'status': 'correct',
                'time_spent_seconds': 43,
                'completed_at': '2024-12-20T12:30:00Z'
            }
        }
    )