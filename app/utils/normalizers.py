import re
import string


def normalize_topic(topic: str) -> str:
    """
    Normalize topic string to title case.

    Rules:
    - Strip whitespace
    - First letter uppercase, rest lowercase
    - Preserves multi-word topics (e.g., "past SIMPLE" → "Past simple")

    Args:
        topic: Raw topic string

    Returns:
        Normalized topic string

    Raises:
        ValueError: If topic is empty after stripping
    """
    topic_strip = topic.strip()
    if not topic_strip:
        raise ValueError("Topic cannot be empty or whitespace only")

    # Capitalize only first letter, rest lowercase
    return topic_strip[0].upper() + topic_strip[1:].lower()


def normalize_answer(text: str) -> str:
    """
    Normalize user answer for flexible comparison.

    Rules:
    - Lowercase, strip whitespace
    - Remove trailing punctuation
    - Collapse multiple spaces
    - Remove repeated punctuation
    """
    text = text.strip().lower()
    text = text.rstrip(string.punctuation)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([' + re.escape(string.punctuation) + r'])\1+', r'\1', text)

    return text