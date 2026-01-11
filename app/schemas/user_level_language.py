from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import LanguageLevelEnum, LanguageEnum

if TYPE_CHECKING:
    from app.schemas.user import UserBrief


class UserLanguageBase(BaseModel):
    """Base fields for user language level."""
    language: LanguageEnum
    level: LanguageLevelEnum

    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True
    )


class UserLanguageLevelUpdate(BaseModel):
    """Schema for adding language for user's learning list."""
    level: LanguageLevelEnum | None = Field(
        default=None,
        description=(
            'Current language proficiency level (CEFR).'
            'On creation: defaults to A1 if not provided.'
            'On update: keeps existing level if not provided.'
        )
    )
    make_active: bool = Field(
        default=False,
        description='Set this language as active learning language'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': [
                {'level': 'B2'},
                {'make_active': True},
                {'level': 'B1', 'make_active': True}
            ]
        }
    )


class UserLanguageBrief(UserLanguageBase):
    """Brief schema for user language level response."""
    id: int

    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'language': 'en',
                'level': 'B2',
            }
        }
    )


class UserLanguageRead(UserLanguageBrief):
    """Schema for user language level response (admin only)."""
    user: 'UserBrief'
    created_at: datetime

    model_config = ConfigDict(
        use_enum_values=True,
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
                'language': 'en',
                'level': 'B2',
                'created_at': '2024-12-20T12:30:00Z'
                }
            }
        )