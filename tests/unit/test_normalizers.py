# Standard library
import pytest
from contextlib import nullcontext as does_not_raise

# Utils
from app.utils.normalizers import normalize_topic, normalize_answer


@pytest.mark.parametrize(
    'topic, expected, expectation',
    [
        ('   ', None, pytest.raises(ValueError, match='Topic cannot be empty or whitespace only')),
        ('GRAMMAR', 'Grammar', does_not_raise()),
        ('grammar', 'Grammar', does_not_raise()),
        ('past SIMPLE', 'Past simple', does_not_raise()),
    ],
    ids=[
        'empty_topic_raises_error',
        'normalize_uppercase',
        'normalize_lowercase',
        'normalize_multiword',
    ]
)
def test_normalize_topic(topic, expected, expectation):
    with expectation:
        result = normalize_topic(topic)
        assert result == expected


@pytest.mark.parametrize(
    'text, expected',
    [
        ('', ''),
        ('  HeLLo\t\tWORLD!!!  ', 'hello world'),
        ('hello...... world,,,,  HI!!!  ', 'hello. world, hi'),
        ("can't", "can't"),
        ('!!!', ''),
        ('hello   world', 'hello world'),
    ],
    ids=[
        'empty_answer',
        'normalize_uppercase_and_whitespace',
        'normalize_trailing_punctuation',
        'preserve_apostrophe',
        'only_punctuation_returns_empty',
        'collapse_multiple_spaces',
    ]
)
def test_normalize_answer(text, expected):
    result = normalize_answer(text)
    assert result == expected