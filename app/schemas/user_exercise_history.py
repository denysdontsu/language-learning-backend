from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, ConfigDict, model_validator, computed_field

from app.schemas.enums import ExerciseStatusEnum
from app.schemas.exercise import ExerciseBrief, ExerciseBriefForHistory
from app.utils.validators import validate_exercise_status


class ExerciseHistoryBase(BaseModel):
    """Base user exercise history fields."""
    user_answer: str | None = None
    status: ExerciseStatusEnum
    time_spent_seconds: int = Field(ge=0)


class ExerciseHistoryCreate(ExerciseHistoryBase):
    """Schema for crete user exercise history."""
    user_id: int
    exercise_id: int

    model_config = ConfigDict(
        json_schema_extra={
            'example': [
                {
                    'user_id': 1,
                    'exercise_id': 2,
                    'user_answer': 'go',
                    'status': 'incorrect',
                    'time_spent_seconds': 43,
                },
                {
                    'user_id': 1,
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
    exercise: ExerciseBriefForHistory
    completed_at: datetime

    @computed_field
    @property
    def is_correct(self) -> bool:
        return self.status == ExerciseStatusEnum.CORRECT

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'user_answer': 'Я живу тут 5 років',
                'status': 'correct',
                'time_spent_seconds': 43,
                'completed_at': '2024-12-20T12:30:00Z',
                'is_correct': True,
                'exercise': {
                    'id': 1,
                    'topic': 'Present perfect',
                    'difficult_level': 'B1',
                    'type': 'sentence_translation',
                    'question_text': 'I have lived here for 5 years',
                    'type_display_name': 'Sentence translation'
                }
            }
        }
    )


class ExerciseHistoryRead(ExerciseHistoryBase):
    """Schema for user exercise history response."""
    id: int
    exercise: ExerciseBrief
    completed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'user_answer': 'went',
                'status': 'correct',
                'time_spent_seconds': 43,
                'completed_at': '2024-12-20T12:30:00Z',
                'is_correct': True,
                'exercise': {
                    'id': 2,
                    'topic': 'Past simple verbs',
                    'difficult_level': 'A2',
                    'type': 'multiple_choice',
                    'type_display_name': 'Multiple choice',
                    'options': {
                        'A': 'go',
                        'B': 'went',
                        'C': 'gone',
                        'D': 'going'
                    },
                    'correct_option_key': 'B',
                    # Question
                    'question_text': 'Yesterday I ___ to the store',
                    'question_language': 'en',
                    'question_language_full_name': 'English',
                    # Answer
                    'correct_answer': 'went',
                    'answer_language': 'en',
                    'answer_language_full_name': 'English',
                    # Translation (optional)
                    'question_translation': 'Вчора я пішов у магазин',
                    'question_translation_language': 'uk',
                    'question_translation_full_name': 'Ukrainian',
                    # Metadata
                    'added_at': '2024-12-20T12:30:00Z',
                    'is_active': True,
                    # Explanation (optional, Phase 2)
                    'explanation': None
                }
            }
        }
    )