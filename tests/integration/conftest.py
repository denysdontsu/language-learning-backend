# Third-party
from typing import Callable
import pytest
from httpx import ASGITransport, AsyncClient

# APP
from app.api.dependencies import get_db

from app.core.security import create_access_token, hash_password
from app.db.connection import async_session_maker

from app.main import app

# Models
from app.models import User, UserLevelLanguage, Exercise

# Schemas
from app.schemas import LanguageEnum, UserRoleEnum, LanguageLevelEnum, ExerciseTypeEnum


@pytest.fixture
async def db():
    """
    Provide test database session with automatic rollback after each test.
    """
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def client(db):
    """
    Provide async HTTP test client with overridden database dependency.

    Replaces get_db with test session to ensure all requests
    use the same transaction that will be rolled back after the test.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def user_data():
    """Base user data for registration and user creation fixtures."""
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'name' : 'Test User',
        'native_language': LanguageEnum.UK,
        'password': 'testpass1',
    }


@pytest.fixture
def create_user_in_db(db, user_data):
    """
    Factory fixture to create test users with optional field overrides.

    Enables flexible user creation with default values that can be customized
    per test. Uses flush() to keep changes in test transaction for auto-rollback.

    Usage:
        async def test_example(create_user_in_db):
            user = await create_user_in_db(email='custom@example.com')
            user_admin = await create_user_in_db(role=UserRoleEnum.ADMIN)

    Args:
        db: Test database session
        user_data: Fixture with base user data

    Returns:
        Async function that creates and returns User instance
    """
    async def _create_user(**overrides) -> User:
        default = {
            'is_active': True,
            'role': UserRoleEnum.USER
        }
        data = {**default, **user_data, **overrides}

        user_fields = {k: v for k, v in data.items() if k != 'password'}
        user = User(
            **user_fields,
            hashed_password=hash_password(data['password']),
        )
        db.add(user)
        await db.flush()
        return user

    return _create_user


@pytest.fixture
async def test_user(create_user_in_db):
    """
    Create regular user directly in database without commit.

    Uses flush instead of commit to keep changes within the test
    transaction, allowing automatic rollback after the test.
    """
    return await create_user_in_db()


@pytest.fixture
async def test_deactivate_user(create_user_in_db):
    """
    Create inactive user for testing access denial scenarios.

    User with is_active=False for testing authentication/authorization
    that rejects inactive accounts.

    Returns:
        User: Inactive user in database
    """
    return await create_user_in_db(
        is_active=False
    )


@pytest.fixture
async def test_admin(create_user_in_db):
    """
    Create admin directly in database without commit.

    Uses flush instead of commit to keep changes within the test
    transaction, allowing automatic rollback after the test.
    """
    return await create_user_in_db(
        email='admin@example.com',
        username='adminuser',
        role=UserRoleEnum.ADMIN
    )


@pytest.fixture
def get_auth_headers() -> Callable:
    """
    Factory fixture to generate JWT authorization headers for any user.

    Creates Bearer token headers for provided user instance.
    Includes user role in token payload for admin/user distinction.

    Usage:
        async def test_example(test_user, test_admin, get_auth_headers):
            user_headers = get_auth_headers(test_user)
            admin_headers = get_auth_headers(test_admin)

    Returns:
        Callable: Function that takes User instance, returns auth header dict
    """
    def _create_headers(user) -> dict:
        token = create_access_token(data={'user_id': user.id, 'role': user.role})
        return {'Authorization': f'Bearer {token}'}

    return _create_headers


@pytest.fixture
async def admin_headers(admin_user) -> dict:
    """Provide JWT authorization headers for an admin user."""
    token = create_access_token(data={'user_id': admin_user.id, 'role': admin_user.role})
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
async def test_user_learning_language(db, test_user):
    """
    Create active learning language for test user.

    Sets up UserLevelLanguage relationship and assigns it as user's
    active_learning_language. Useful for testing language-dependent
    functionality and response serialization (UserBriefWithLang).

    Returns:
        UserLevelLanguage: Active language relationship with B1 level English

    Side effects:
        - Sets test_user.active_learning_language_id
        - Refreshes test_user ORM state
    """
    user_language = UserLevelLanguage(
        user_id=test_user.id,
        language=LanguageEnum.EN,
        level=LanguageLevelEnum.B1
    )

    db.add(user_language)
    await db.flush()

    test_user.active_learning_language_id = user_language.id
    await db.flush()
    await db.refresh(test_user)

    return user_language


@pytest.fixture
async def test_other_user(create_user_in_db):
    """
    Create second test user for multi-user test scenarios.

    Useful for testing:
    - Duplicate constraint validation (same email/username)
    - User isolation (cannot see other user's data)
    - Comparison scenarios

    Returns:
        User: Second user with different email/username from test_user
    """
    return await create_user_in_db(
        email='test2@example.com',
        username='testuser2',
        name='Test User 2',
        native_language=LanguageEnum.UK,
        password='testpass1',
    )


@pytest.fixture
async def exercise_en_uk(db) -> Exercise:
    """
    Create a single EN→UK sentence translation exercise.

    Language pair matches test_user (native=UK, active=EN).
    Use this fixture when you need one known exercise with predictable
    id, topic, and correct_answer for submit and next endpoint tests.
    """
    exercise = Exercise(
        topic='Grammar',
        difficult_level=LanguageLevelEnum.B1,
        type=ExerciseTypeEnum.SENTENCE_TRANSLATION,
        question_text='She has been studying English for three years.',
        question_language=LanguageEnum.EN,
        correct_answer='Вона вивчає англійську вже три роки.',
        answer_language=LanguageEnum.UK,
        is_active=True,
    )
    db.add(exercise)
    await db.flush()
    return exercise


@pytest.fixture
async def exercises_batch(db) -> list[Exercise]:
    """
    Create a batch of exercises across different topics and levels.

    Language pair matches test_user (native=UK, active=EN).
    Use this fixture for topics endpoint tests where multiple
    distinct topics are needed.
    """
    exercises = [
        Exercise(
            topic='Grammar',
            difficult_level=LanguageLevelEnum.B1,
            type=ExerciseTypeEnum.SENTENCE_TRANSLATION,
            question_text='She has been studying English for three years.',
            question_language=LanguageEnum.EN,
            correct_answer='Вона вивчає англійську вже три роки.',
            answer_language=LanguageEnum.UK,
            is_active=True,
        ),
        Exercise(
            topic='Vocabulary',
            difficult_level=LanguageLevelEnum.A1,
            type=ExerciseTypeEnum.SENTENCE_TRANSLATION,
            question_text='The cat is on the table.',
            question_language=LanguageEnum.EN,
            correct_answer='Кіт на столі.',
            answer_language=LanguageEnum.UK,
            is_active=True,
        ),
        Exercise(
            topic='Prepositions',
            difficult_level=LanguageLevelEnum.A2,
            type=ExerciseTypeEnum.FILL_BLANK,
            question_text='She is sitting ___ the chair.',
            question_language=LanguageEnum.EN,
            correct_answer='on',
            answer_language=LanguageEnum.EN,
            question_translation='Вона сидить ___ стільці.',
            question_translation_language=LanguageEnum.UK,
            is_active=True,
        ),
        Exercise(
            topic='Tenses',
            difficult_level=LanguageLevelEnum.B1,
            type=ExerciseTypeEnum.MULTIPLE_CHOICE,
            question_text='I ___ here for three years.',
            question_language=LanguageEnum.EN,
            correct_answer='have been living',
            answer_language=LanguageEnum.EN,
            question_translation='Я ___ тут вже три роки.',
            question_translation_language=LanguageEnum.UK,
            options={'A': 'live', 'B': 'have been living', 'C': 'lived', 'D': 'am living'},
            is_active=True,
        ),
        Exercise(
            topic='Articles',
            difficult_level=LanguageLevelEnum.A1,
            type=ExerciseTypeEnum.FILL_BLANK,
            question_text='I have ___ apple.',
            question_language=LanguageEnum.EN,
            correct_answer='an',
            answer_language=LanguageEnum.EN,
            question_translation='У мене є ___ яблуко.',
            question_translation_language=LanguageEnum.UK,
            is_active=True,
        ),
    ]

    for exercise in exercises:
        db.add(exercise)

    await db.flush()
    return exercises