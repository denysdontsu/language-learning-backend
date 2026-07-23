from app.schemas import (
    LanguageLevelEnum,
    ExerciseTypeEnum,
    LanguageEnum,
    UserRoleEnum,
    ExerciseStatusEnum
)


class TestExerciseStatusEnum:
    def test_correct_status_exclude_hours(self):
        assert ExerciseStatusEnum.CORRECT.exclude_at_hours == 336

    def test_skip_status_exclude_hours(self):
        assert ExerciseStatusEnum.SKIP.exclude_at_hours == 72

    def test_incorrect_status_exclude_hours(self):
        assert ExerciseStatusEnum.INCORRECT.exclude_at_hours == 0


class TestExerciseTypeEnum:
    def test_display_names(self):
        assert ExerciseTypeEnum.SENTENCE_TRANSLATION.display_name == 'Sentence translation'
        assert ExerciseTypeEnum.MULTIPLE_CHOICE.display_name == 'Multiple choice'
        assert ExerciseTypeEnum.FILL_BLANK.display_name == 'Fill in the blank'

    def test_instructions(self):
        assert ExerciseTypeEnum.SENTENCE_TRANSLATION.instruction == 'Translate the following text'
        assert ExerciseTypeEnum.MULTIPLE_CHOICE.instruction == 'Choose the correct answer from the options below'
        assert ExerciseTypeEnum.FILL_BLANK.instruction == 'Fill in the blank with the correct word'

    def test_get_all_types_returns_all_values(self):
        result = ExerciseTypeEnum.get_all_types()
        assert set(result.keys()) == {'sentence_translation', 'multiple_choice', 'fill_blank'}


class TestLanguageLevelEnum:
    def test_all_descriptions(self):
        assert LanguageLevelEnum.A1.description == 'Beginner'
        assert LanguageLevelEnum.A2.description == 'Elementary'
        assert LanguageLevelEnum.B1.description == 'Intermediate'
        assert LanguageLevelEnum.B2.description == 'Upper Intermediate'
        assert LanguageLevelEnum.C1.description == 'Advanced'
        assert LanguageLevelEnum.C2.description == 'Proficient'

    def test_get_all_language_levels_count(self):
        result = LanguageLevelEnum.get_all_language_levels()
        assert len(result) == 6


class TestLanguageEnum:
    def test_all_full_names(self):
        assert LanguageEnum.UK.full_name == 'Ukrainian'
        assert LanguageEnum.EN.full_name == 'English'
        assert LanguageEnum.DE.full_name == 'German'


class TestUserRoleEnum:
    def test_is_admin(self):
        assert UserRoleEnum.ADMIN.is_admin() is True
        assert UserRoleEnum.USER.is_admin() is False