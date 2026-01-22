from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    computed_field,
    )

from app.schemas.enums import ExerciseTypeEnum, LanguageLevelEnum, LanguageEnum, ExerciseStatusEnum
from app.schemas.common import Options
from app.utils.helpers import get_correct_option_key
from app.utils.normalizers import normalize_topic
from app.utils.validators import (
    validate_question_translation_pair,
    validate_exercise_options,
    validate_translation_usage)


class ExerciseBase(BaseModel):
    """"Base exercise fields."""
    topic: str = Field(min_length=1, max_length=100)
    difficult_level: LanguageLevelEnum
    type: ExerciseTypeEnum


class ExerciseCreate(ExerciseBase):
    """Schema for creating a new exercise (for admin)."""
    # Question
    question_text: str = Field(min_length=1)
    question_language: LanguageEnum

    # Answer
    correct_answer: str = Field(min_length=1)
    answer_language: LanguageEnum

    # Translation (optional)
    question_translation: str | None = Field(None, min_length=1)
    question_translation_language: LanguageEnum | None = None

    # Options (for type: 'multiple_choice')
    options: Options | None = None

    @field_validator('topic', mode='after')
    @classmethod
    def validate_topic(cls, v):
        """Normalize topic to title case format."""
        return normalize_topic(v)

    @model_validator(mode='after')
    def validate_exercise(self) -> Self:
        """Validate exercise business rules."""
        # Validate options
        validate_exercise_options(self.type, self.options, self.correct_answer)

        # Validate translations
        validate_question_translation_pair(self.question_translation,
                                self.question_translation_language)

        # Validate translation usage
        validate_translation_usage(self.type,
                                   self.question_translation)

        return self

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                # Example 1: Sentence translation
                {
                    'topic': 'Present perfect',
                    'difficult_level': 'B1',
                    'type': 'sentence_translation',
                    'options': None,
                    'question_text': 'I have lived here for 5 years',
                    'question_language': 'en',
                    'correct_answer': 'Я живу тут 5 років',
                    'answer_language': 'uk',
                    'question_translation': None,
                    'question_translation_language': None
                },
                # Example 2: Multiple choice
                {
                    'topic': 'Past simple verbs',
                    'difficult_level': 'A2',
                    'type': 'multiple_choice',
                    'options': {
                        'A': 'go',
                        'B': 'went',
                        'C': 'gone',
                        'D': 'going'
                    },
                    'question_text': 'Yesterday I ___ to the store',
                    'question_language': 'en',
                    'correct_answer': 'went',
                    'answer_language': 'en',
                    'question_translation': 'Вчора я cходив до магазину',
                    'question_translation_language': 'uk'
                },
                # Example 3: Fill in the blank
                {
                    'topic': 'Articles',
                    'difficult_level': 'A1',
                    'type': 'fill_blank',
                    'options': None,
                    'question_text': 'I have ___ apple',
                    'question_language': 'en',
                    'correct_answer': 'an',
                    'answer_language': 'en',
                    'question_translation': 'У мене є яблуко',
                    'question_translation_language': 'uk'
                }
            ]
        }
    )


class ExerciseUpdate(BaseModel):
    """Schema for update exercise (for admin).

    Note:
    Cross-field validations are skipped because fields are optional.
    Validation must be applied after combining update data
    with the persisted exercise.
    """
    # Base info
    topic: str | None = Field(None, min_length=1, max_length=100)
    difficult_level: LanguageLevelEnum | None = None
    type: ExerciseTypeEnum | None = None
    options: Options | None = None

    # Question
    question_text: str | None = Field(None, min_length=1)
    question_language: LanguageEnum | None = None

    # Answer
    correct_answer: str | None = Field(None, min_length=1)
    answer_language: LanguageEnum | None = None

    # Translation (optional)
    question_translation: str | None = Field(None, min_length=1)
    question_translation_language: LanguageEnum | None = None

    @field_validator('topic', mode='after')
    @classmethod
    def validate_topic(cls, v: str | None):
        """Normalize topic to title case format if provided."""
        if v is None:
            return None
        return normalize_topic(v)

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                # Example 1: Update only difficulty
                {
                    'topic': None,
                    'difficult_level': 'B2',
                    'type': None,
                    'options': None,
                    'question_text': None,
                    'question_language': None,
                    'correct_answer': None,
                    'answer_language': None,
                    'question_translation': None,
                    'question_translation_language': None
                },
                # Example 2: Update question text
                {
                    'topic': 'Present perfect',
                    'difficult_level': None,
                    'type': None,
                    'options': None,
                    'question_text': 'I have been living here for 5 years',
                    'question_language': None,
                    'correct_answer': None,
                    'answer_language': None,
                    'question_translation': None,
                    'question_translation_language': None
                }
            ]
        }
    )


class ExerciseQuestion(ExerciseBase):
    """Schema for exercise question to display to user."""
    id: int
    options: Options | None
    question_text: str

    @computed_field
    @property
    def instruction(self) -> str:
        return self.type.instruction

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                # Example 1: Translation exercise
                {
                    'id': 1,
                    'topic': 'Present perfect',
                    'difficult_level': 'B1',
                    'type': 'sentence_translation',
                    'question_text': 'I have lived here for 5 years',
                    'options': None,
                    'instruction': 'Translate the following text'
                },
                # Example 2: Multiple choice
                {
                    'id': 2,
                    'topic': 'Past simple verbs',
                    'difficult_level': 'A2',
                    'type': 'multiple_choice',
                    'question_text': 'Yesterday I ___ to the store',
                    'options': {
                        'A': 'go',
                        'B': 'went',
                        'C': 'gone',
                        'D': 'going'
                    },
                    'instruction': 'Choose the correct answer from the options below'
                },
                # Example 3: Fill blank
                {
                    'id': 3,
                    'topic': 'Articles',
                    'difficult_level': 'A1',
                    'type': 'fill_blank',
                    'question_text': 'I have ___ apple',
                    'options': None,
                    'instruction': 'Fill in the blank with the correct word'
                },
            ]
        }
    )


class ExerciseUserAnswer(BaseModel):
    """Schema for user answer submission."""
    user_answer: str
    time_spent_seconds: int = Field(gt=0, description="Time spent answering (seconds)")

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                # Example 1: Translation exercise
                {
                    'user_answer': 'Я живу тут 5 років',
                    'time_spent_seconds': 44
                },
                # Example 2: Multiple choice
                {
                    'user_answer': 'went',
                    'time_spent_seconds': 13
                },
                # Example 3: Fill in the blank
                {
                    'user_answer': 'an',
                    'time_spent_seconds': 22
                }
            ]
        }
    )


class ExerciseCorrectAnswer(ExerciseBase):
    """Schema for response after answer submission."""
    id: int
    question_text: str
    options: Options | None
    correct_answer: str = Field(min_length=1)
    user_answer: str
    is_correct: bool
    status: ExerciseStatusEnum
    question_translation: str | None
    explanation: str | None = None

    @computed_field
    @property
    def correct_option_key(self) -> str | None:
        """Option key for correct answer (multiple choice only)."""
        return get_correct_option_key(
            self.type,
            self.options,
            self.correct_answer
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    # Example 1: Translation exercise
                    'id': 1,
                    'topic': 'Present perfect',
                    'difficult_level': 'B1',
                    'type': 'sentence_translation',
                    'question_text': 'I have lived here for 5 years',
                    'options': None,
                    'correct_answer': 'Я живу тут 5 років',
                    'user_answer': 'Я живу тут 5 років',
                    'is_correct': True,
                    'status': 'correct',
                    'question_translation': None,
                    'explanation': None
                },
                {
                    # Example 2: Multiple choice
                    'id': 2,
                    'topic': 'Past simple verbs',
                    'difficult_level': 'A2',
                    'type': 'multiple_choice',
                    'question_text': 'Yesterday I ___ to the store',
                    'options': {
                        'A': 'go',
                        'B': 'went',
                        'C': 'gone',
                        'D': 'going'
                    },
                    'correct_answer': 'went',
                    'user_answer': 'go',
                    'is_correct': False,
                    'status': 'incorrect',
                    'question_translation': 'Вчора я пішов у магазин',
                    'explanation': None,
                    'correct_option_key': 'B'
                },
                # Example 3: Fill in the blank
                {
                    'id': 3,
                    'topic': 'Articles',
                    'difficult_level': 'A1',
                    'type': 'fill_blank',
                    'question_text': 'I have ___ apple',
                    'options': None,
                    'correct_answer': 'an',
                    'user_answer': 'a',
                    'is_correct': False,
                    'status': 'incorrect',
                    'question_translation': 'У мене є яблуко',
                    'explanation': None
                }
            ]
        }
    )


class ExerciseFilter(BaseModel):
    """Schema for filtering exercises based on optional criteria."""
    topic: str | None = Field(None, min_length=1, max_length=100)
    difficult_level: LanguageLevelEnum | None = None
    type: ExerciseTypeEnum | None = None

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'topic': None,
                'difficult_level': 'B1',
                'type': None,
            }
        }
    )


class ExerciseBrief(ExerciseBase):
    """Brief schema for exercise response."""
    id: int
    question_language: LanguageEnum
    answer_language: LanguageEnum

    @computed_field
    @property
    def question_language_full_name(self) -> str:
        return self.question_language.full_name

    @computed_field
    @property
    def answer_language_full_name(self) -> str:
        return self.answer_language.full_name

    @computed_field
    @property
    def type_display_name(self) -> str:
        return self.type.display_name

    @computed_field
    @property
    def correct_option_key(self) -> str | None:
        """Option key for correct answer (multiple choice only)."""
        return get_correct_option_key(
            self.type,
            self.options,
            self.correct_answer
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 1,
                'topic': 'Present perfect',
                'difficult_level': 'B1',
                'type': 'sentence_translation',
                'question_language': 'en',
                'answer_language': 'uk',
                'question_language_full_name': 'English',
                'answer_language_full_name': 'Ukrainian',
                'type_display_name': 'Sentence translation'
            }
        }
    )


class ExerciseRead(ExerciseBrief):
    """Schema for exercise response (for admin)."""
    # Base info
    options: Options | None = None

    # Question
    question_text: str = Field(min_length=1)

    # Answer
    correct_answer: str = Field(min_length=1)

    # Translation (optional)
    question_translation: str | None = Field(None, min_length=1)
    question_translation_language: LanguageEnum | None = None

    # Metadata
    added_at: datetime
    is_active: bool

    @computed_field
    @property
    def question_translation_full_name(self) -> str | None:
        if self.question_translation_language is None:
            return None
        return self.question_translation_language.full_name

    @computed_field
    @property
    def correct_option_key(self) -> str | None:
        """Option key for correct answer (multiple choice only)."""
        return get_correct_option_key(
            self.type,
            self.options,
            self.correct_answer
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                # Example 1: Translation exercise
                {
                    'id': 1,
                    'topic': 'Present perfect',
                    'difficult_level': 'B1',
                    'type': 'sentence_translation',
                    'type_display_name': 'Sentence translation',
                    'question_language': 'en',
                    'question_language_full_name': 'English',
                    'answer_language': 'uk',
                    'answer_language_full_name': 'Ukrainian',
                    'options': None,
                    'question_text': 'I have lived here for 5 years',
                    'correct_answer': 'Я живу тут 5 років',
                    'question_translation': None,
                    'question_translation_language': None,
                    'question_translation_full_name': None,
                    'added_at': '2024-12-20T12:30:00Z',
                    'is_active': True
                },
                # Example 2: Multiple choice
                {
                    'id': 2,
                    'topic': 'Past simple verbs',
                    'difficult_level': 'A2',
                    'type': 'multiple_choice',
                    'type_display_name': 'Multiple choice',
                    'question_language': 'en',
                    'question_language_full_name': 'English',
                    'answer_language': 'en',
                    'answer_language_full_name': 'English',
                    'options': {
                        'A': 'go',
                        'B': 'went',
                        'C': 'gone',
                        'D': 'going'
                    },
                    'question_text': 'Yesterday I ___ to the store',
                    'correct_answer': 'went',
                    'correct_option_key': 'B',
                    'question_translation': 'Вчора я пішов у магазин',
                    'question_translation_language': 'uk',
                    'question_translation_full_name': 'Ukrainian',
                    'added_at': '2024-12-20T12:30:00Z',
                    'is_active': True
                },
                # Example 3: Fill blank
                {
                    'id': 3,
                    'topic': 'Articles',
                    'difficult_level': 'A1',
                    'type': 'fill_blank',
                    'type_display_name': 'Fill in the blank', # В Enum 'Fill in the blank'
                    'question_language': 'en',
                    'question_language_full_name': 'English',
                    'answer_language': 'en',
                    'answer_language_full_name': 'English',
                    'options': None,
                    'question_text': 'I have ___ apple',
                    'correct_answer': 'an',
                    'question_translation': 'У мене є яблуко',
                    'question_translation_language': 'uk',
                    'question_translation_full_name': 'Ukrainian',
                    'added_at': '2024-12-20T12:30:00Z',
                    'is_active': True
                },
            ]
        }
    )