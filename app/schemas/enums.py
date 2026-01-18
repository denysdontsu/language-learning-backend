from app.utils.enum_utils import validate_enum_dict_properties

from enum import Enum

# Enums for models and schemas
class ExerciseTypeEnum(str, Enum):
    """Available exercise types."""
    SENTENCE_TRANSLATION = 'sentence_translation'
    MULTIPLE_CHOICE = 'multiple_choice'
    FILL_BLANK = 'fill_blank'

    __INSTRUCTIONS = {
        'sentence_translation': 'Translate the following text',
        'multiple_choice': 'Choose the correct answer from the options below',
        'fill_blank': 'Fill in the blank with the correct word'
    }

    __DISPLAY_NAME = {
        'sentence_translation': 'Sentence translation',
        'multiple_choice': 'Multiple choice',
        'fill_blank': 'Fill in the blank',
    }

    @property
    def instruction(self) -> str:
        """Instruction for the exercise type."""
        return self.__INSTRUCTIONS[self.value]

    @property
    def display_name(self) -> str:
        """Display name for the exercise type."""
        return self.__DISPLAY_NAME[self.value]

    @classmethod
    def get_all_types(cls) -> dict[str, str]:
        """Returns all exercise types with instructions."""
        return {ex_type.value: ex_type.instruction for ex_type in cls}

    @classmethod
    def validate_properties(cls) -> None:
        """Validates that internal dictionaries match enum values."""
        validate_enum_dict_properties(
            cls,
            INSTRUCTIONS=cls.__INSTRUCTIONS,
            DISPLAY_NAME=cls.__DISPLAY_NAME
        )

ExerciseTypeEnum.validate_properties()


class LanguageLevelEnum(str, Enum):
    """CEFR Language levels."""
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

    __DESCRIPTIONS = {
        'A1': 'Beginner',
        'A2': 'Elementary',
        'B1': 'Intermediate',
        'B2': 'Upper Intermediate',
        'C1': 'Advanced',
        'C2': 'Proficient'
    }

    @property
    def description(self) -> str:
        """Description of the language level."""
        return self.__DESCRIPTIONS[self.value]

    @classmethod
    def get_all_language_levels(cls) -> dict[str, str]:
        """Returns all language levels with descriptions."""
        return {lang.value: lang.description for lang in cls}

    @classmethod
    def validate_properties(cls) -> None:
        """Validates that internal dictionaries match enum values."""
        validate_enum_dict_properties(
            cls,
            DESCRIPTIONS=cls.__DESCRIPTIONS
        )

LanguageLevelEnum.validate_properties()


class LanguageEnum(str, Enum):
    """Available languages in ISO 639-1 format."""
    UK = 'uk'
    EN = 'en'
    DE = 'de'

    __NAMES = {
        'uk': 'Ukrainian',
        'en': 'English',
        'de': 'German'
    }

    @property
    def full_name(self) -> str:
        """Full languages name"""
        return self.__NAMES[self.value]

    @classmethod
    def get_all_languages(cls) -> dict[str, str]:
        """Returns all available languages with their full name."""
        return {code.value: code.full_name for code in cls}

    @classmethod
    def validate_properties(cls) -> None:
        """Validates that internal dictionaries match enum values."""
        validate_enum_dict_properties(
            cls,
            NAMES=cls.__NAMES
        )

LanguageEnum.validate_properties()


class ExerciseStatusEnum(str, Enum):
    """Available exercise status."""
    CORRECT = 'correct'
    INCORRECT = 'incorrect'
    SKIP = 'skip'

    __EXCLUDE_AT = {
        'correct': 336, # 14 days
        'skip': 72,  # 3 days
        'incorrect': 0
    }

    @property
    def exclude_at_hours(self) -> int:
        """Get exclusion period in hours for this status."""
        return self.__EXCLUDE_AT[self.value]

    @classmethod
    def validate_properties(cls) -> None:
        """Validates that internal dictionaries match enum values."""
        return validate_enum_dict_properties(
            ExerciseStatusEnum,
            EXCLUDE_AT=cls.__EXCLUDE_AT)

ExerciseStatusEnum.validate_properties()