from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.utils.validators import validate_password_strength
from app.schemas.enums import LanguageEnum

if TYPE_CHECKING:
    from app.schemas.user_level_language import UserLevelBrief


class UserBase(BaseModel):
    """Base user field."""
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    native_language: LanguageEnum


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(
        min_length=8,
        max_length=100,
        description='Password must have letter, digit and special character'
    )
    active_learning_language: LanguageEnum


    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        return validate_password_strength(v)

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'email': 'example@mail.com',
                'name': 'Denis',
                'username': 'denisD',
                'native_language': 'uk',
                'active_learning_language': 'en',
                'password': 'ExamplePass123!'
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for update user data."""
    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    username: str | None = Field(None, min_length=3, max_length=50)
    native_language: LanguageEnum | None = None
    active_learning_language: LanguageEnum | None = None

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'email': None,
                'name': 'Denis',
                'username': None,
                'native_language': None,
                'active_learning_language': 'de'
            }
        }
    )

class UserLogin(BaseModel):
    """Schema for login user."""
    email: EmailStr
    password: str


class UserChangePassword(BaseModel):
    """Schema for change password."""
    old_password: str
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description='New password. Must have letter, digit and special character'
    )

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate new password strength."""
        return validate_password_strength(v)


class UserBrief(UserBase):
    """Brief schema for user response."""
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'email': 'example@mail.com',
                'name': 'Denis',
                'username': 'denisD',
                'native_language': 'uk',
            }
        }
    )


class UserBriefWithLang(UserBrief):
    """User brief schema with detailed active learning language."""
    active_learning_language: 'UserLevelBrief'

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra = {
            'example': {
                'id': 1,
                'email': 'example@mail.com',
                'name': 'Denis',
                'username': 'denisD',
                'native_language': 'uk',
                'active_learning_language': {
                    'id': 1,
                    'language': 'en',
                    'level': 'B2',
                }
            }
        }
    )


class UserRead(UserBriefWithLang):
    """Schema for user response (for admin)."""
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'email': 'example@mail.com',
                'name': 'Denis',
                'username': 'denisD',
                'native_language': 'uk',
                'active_learning_language': {
                    'id': 1,
                    'language': 'en',
                    'level': 'B2',
                },
                'role': 'user',
                'is_active': True,
                'created_at': '2024-12-20T12:30:00Z',
            }
        }
    )
