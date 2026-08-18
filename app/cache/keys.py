# Standard library
from typing import Literal

# Schemas
from app.schemas import LanguageEnum


class CacheKeys:
    TOPICS_TTL = 3600

    _TOPICS_KEY = 'exercises:topics'

    @classmethod
    def topics(cls, native: LanguageEnum, active: LanguageEnum) -> str:
        """Exact key for topics cache."""
        return f'{cls._TOPICS_KEY}:{native.value}:{active.value}'

    @classmethod
    def topics_pattern(cls) -> str:
        """Wildcard pattern for topics cache invalidation."""
        return f'{cls._TOPICS_KEY}:*'