from typing import Type
from enum import Enum


def validate_enum_dict_properties(enum_class: Type[Enum], **property_dicts) -> None:
    """
    Validates that dictionary keys exactly match enum values.

    Args:
        enum_class: Enum class to validate against
        **property_dicts: Dictionaries whose keys should match enum values

    Raises:
        ValueError: If any dictionary has missing keys
    """
    enum_values = {enum.value for enum in enum_class}
    for dict_name, prod_dict in property_dicts.items():
        missing = enum_values - prod_dict.keys()
        if missing:
                raise ValueError(
                    f"{enum_class.__name__}: fields {missing} are missing in '{dict_name}'")
