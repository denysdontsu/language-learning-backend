from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import LanguageLevelEnum, LanguageEnum
from app.schemas.user import UserBrief


class UserLevelBase(BaseModel):
    """Base fields for user language level."""
    language: LanguageEnum
    level: LanguageLevelEnum


class UserLevelCreate(UserLevelBase):
    """Schema for adding language for user's learning list."""
    level: LanguageLevelEnum = Field(
        default=LanguageLevelEnum.A1,
        description='Current language proficiency level (CEFR)'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'language': 'en',
                'level': 'B2'
            }
        }
    )


class UserLevelUpdate(BaseModel):
    """Schema for updating language proficiency level."""
    level: LanguageLevelEnum

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'level': 'B2'
            }
        }
    )


class UserLevelBrief(UserLevelBase):
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


class UserLevelRead(UserLevelBase):
    """Schema for user language level response (admin only)."""
    user: UserBrief
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