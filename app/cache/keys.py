# Standard library
from typing import Literal

# Schemas
from app.schemas import LanguageEnum


class CacheKeys:
    TOPICS_TTL = 3600
    STATS_OVERVIEW_TTL = 180
    STATS_PERFORMANCE_TTL = 180

    _TOPICS_KEY = 'exercises:topics'
    _STATS_OVERVIEW_KEY = 'stats:overview'
    _STATS_PERFORMANCE_KEY = 'stats:performance'

    @classmethod
    def topics(cls, native: LanguageEnum, active: LanguageEnum) -> str:
        """
        Exact key for topics cache per language pair.

        Args:
            native: User's native language
            active: User's active learning language
        """
        return f'{cls._TOPICS_KEY}:{native.value}:{active.value}'

    @classmethod
    def topics_pattern(cls) -> str:
        """
        Wildcard pattern to invalidate all topics cache entries.

        Used when a new exercise is created — topics may have changed
        for any language pair.
        """
        return f'{cls._TOPICS_KEY}:*'

    @classmethod
    def stats_overview(
            cls,
            user_id: int,
            language: LanguageEnum | None = None,
            period: Literal['7d', '30d', '3m', '1y', 'all'] | None = None,
    ) -> str:
        """
        Exact key for stats overview cache.

        Args:
            user_id: User ID
            language: Language filter, or None for all languages aggregate
            period: Time period filter, or None defaults to 'all'
        """
        lang = language.value if language else 'all'
        p = period or 'all'
        return f'{cls._STATS_OVERVIEW_KEY}:{user_id}:{lang}:{p}'

    @classmethod
    def stats_overview_pattern(
            cls,
            user_id: int,
            language: LanguageEnum | None = None
    ) -> str:
        """
        Pattern to invalidate stats overview for user.

        Args:
            user_id: User ID
            language: Specific language to invalidate, or None to invalidate
                      the all-languages aggregate key
        """
        if language:
            return f'{cls._STATS_OVERVIEW_KEY}:{user_id}:{language.value}:*'
        else:
            return f'{cls._STATS_OVERVIEW_KEY}:{user_id}:all:*'

    @classmethod
    def stats_performance(
            cls,
            user_id: int,
            language: LanguageEnum | None = None,
            period: Literal['7d', '30d', '3m', '1y', 'all'] | None = None,
    ) -> str:
        """
        Exact key for stats performance cache.

        Args:
            user_id: User ID
            language: Language filter, or None for all languages aggregate
            period: Time period filter, or None defaults to 'all'
        """
        lang = language.value if language else 'all'
        p = period or 'all'
        return f'{cls._STATS_PERFORMANCE_KEY}:{user_id}:{lang}:{p}'

    @classmethod
    def stats_performance_pattern(
            cls,
            user_id: int,
            language: LanguageEnum | None = None
    ) -> str:
        """
        Pattern to invalidate stats performance for user.

        Args:
            user_id: User ID
            language: Specific language to invalidate, or None to invalidate
                      the all-languages aggregate key
        """
        if language:
            return f'{cls._STATS_PERFORMANCE_KEY}:{user_id}:{language.value}:*'
        else:
            return f'{cls._STATS_PERFORMANCE_KEY}:{user_id}:all:*'