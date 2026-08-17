# Schemas
from app.schemas import LanguageEnum


TOPICS_TTL = 3600

TOPICS_CACHE_KEY = 'exercises:topics'

def get_topics_key(
        native_language: LanguageEnum,
        active_language: LanguageEnum
) -> str:
    """Generate cache key for exercise topics by language pair."""
    return f'{TOPICS_CACHE_KEY}:{native_language.value}:{active_language.value}'