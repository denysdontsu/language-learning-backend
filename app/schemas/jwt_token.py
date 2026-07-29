# Standard library
from typing import Literal

# Third-party
from pydantic import BaseModel, Field, field_validator


class JWTPayload(BaseModel):
    """
    JWT token payload schema for validation.

    Validates decoded JWT token structure and types.
    """
    sub: str = Field(description='User ID (subject)')
    role: Literal['admin', 'user'] = Field(default='user', description='User role')
    exp: int = Field(description='Expiration timestamp (Unix)')
    iat: int = Field(description='Issued at timestamp (Unix)')


    @field_validator('iat')
    @classmethod
    def iat_must_be_positive(cls, v: int) -> int:
        """Validate that issued at timestamp is positive."""
        if v <= 0:
            raise ValueError("Issued must be positive")

        return v


    @field_validator('sub')
    @classmethod
    def sub_must_be_positive_numeric(cls, v: str) -> str:
        try:
            sub = int(v)
        except ValueError:
            raise ValueError("'sub' must be a numeric string")
        if sub <= 0:
            raise ValueError("'sub' must be positive")
        return v



