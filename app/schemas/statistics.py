from pydantic import BaseModel, ConfigDict, field_validator, Field


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