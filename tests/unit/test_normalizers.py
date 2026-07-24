# Standard library
import pytest
from contextlib import nullcontext as does_not_raise

# Utils
from app.utils.normalizers import normalize_topic, normalize_answer


z


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