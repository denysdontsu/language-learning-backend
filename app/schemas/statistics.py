from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, Field

from app.schemas.enums import LanguageLevelEnum


class OverviewResponse(BaseModel):
    """Overview statistics response."""
    total_exercises: int = Field(
        description='Total completed exercises, including skipped')
    total_answered: int = Field(
        description='Total completed exercises, excluding skipped')
    accuracy: float = Field(
        description='Accuracy percentage (correct answers / total answered)')
    total_study_hours: float = Field(
        description='Total study time in hours')
    current_streak_days: int = Field(
        description='Consecutive days streak')
    is_today_completed: bool = Field(
        description="Whether at least one exercise was completed today")


    @field_validator('accuracy', 'total_study_hours', mode='after')
    @classmethod
    def round_fields(cls, v: float) -> float:
        """Round float fields to 1 decimal place."""
        return round(v, 1)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'total_exercises': 123,
                'total_answered': 103,
                'accuracy': 70.2,
                'total_study_hours': 4.8,
                'current_streak_days': 67,
                'is_today_completed': True
            }
        }
    )


class DifficultyStats(BaseModel):
    """Statistics for a CEFR difficulty level."""
    accuracy: float = Field(
        description='Accuracy percentage (correct answers / total answered)')
    total_answered: int = Field(
        description='Total answered exercises at this level')
    mastered: bool = Field(
        description='True if accuracy > 80% and total >= 100')
    in_progress: bool = Field(
        description='True if has exercises (>10) but not mastered')

    @field_validator('accuracy', mode='after')
    @classmethod
    def round_fields(cls, v: float) -> float:
        """Round float fields to 1 decimal place."""
        return round(v, 1)

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'accuracy': 90.3,
                'total_answered': 350,
                'mastered': True,
                'in_progress': False
            }
        }
    )

class TopicStats(BaseModel):
    """Statistics for a single topic"""
    name: str = Field(
        description='Topic name')
    accuracy: float = Field(
        description='Accuracy percentage for this topic')
    total_answered: int = Field(
        description='Total answered exercises for this topic')
    status: Literal['mastered', 'good', 'learning', 'needs_practice'] = Field(
        description='Topic mastery status')

    @field_validator('accuracy', mode='after')
    @classmethod
    def round_fields(cls, v: float) -> float:
        """Round float fields to 1 decimal place."""
        return round(v, 1)

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'name': 'Articles',
                'accuracy': 88.8,
                'total_answered': 125,
                'status': 'mastered'
            }
        }
    )


class PerformanceResponse(BaseModel):
    """Performance statistics response with metadata"""
    by_difficulty: dict[str, DifficultyStats] = Field(
        description='Statistics per CEFR level (A1, A2, B1, B2, C1, C2)')
    top_topics: list[TopicStats] = Field(
        description='Top 5 topics by accuracy')
    weak_topics: list[TopicStats] = Field(
        description='Bottom 5 topics needing practice (accuracy < 60%, min 20 exercises)')
    suggested_level: LanguageLevelEnum | None = Field(
        description='Recommended next difficulty level based on performance (only when language filter is applied)'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'by_difficulty': {
                    'A1': {
                        'accuracy': 90.3,
                        'total_answered': 350,
                        'mastered': True,
                        'in_progress': False
                    },
                    'A2': {
                        'accuracy': 73.1,
                        'total_answered': 280,
                        'mastered': False,
                        'in_progress': True
                    }
                },
                'top_topics': [
                    {
                        'name': 'Articles',
                        'accuracy': 88.8,
                        'total_answered': 125,
                        'status': 'mastered'
                    }
                ],
                'weak_topics': [
                    {
                        'name': 'Prepositions',
                        'accuracy': 50.0,
                        'total_answered': 88,
                        'status': 'needs_practice'
                    }
                ],
                'suggested_level': 'B1'
            }
        }
    )