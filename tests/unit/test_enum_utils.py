import pytest
from enum import Enum

from app.utils.enum_utils import validate_enum_dict_properties


def test_validate_raises_when_key_missing():
    class TestEnum(str, Enum):
        A = 'a'
        B = 'b'

    with pytest.raises(ValueError, match="missing"):
        validate_enum_dict_properties(TestEnum, MY_DICT={'a': 'value'})

def test_validate_passes_when_all_keys_present():
    class TestEnum(str, Enum):
        A = 'a'
        B = 'b'

    validate_enum_dict_properties(TestEnum, MY_DICT={'a': 'x', 'b': 'y'})