# Third-party
import pytest
from httpx import ASGITransport, AsyncClient

# APP
from app.api.dependencies import get_db

from app.core.security import create_access_token, hash_password
from app.db.connection import async_session_maker

from app.main import app

# Models
from app.models import User

# Schemas
from app.schemas import LanguageEnum, UserRoleEnum


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
async def test_user(db, user_data) -> User:
    """
    Create regular user directly in database without commit.

    Uses flush instead of commit to keep changes within the test
    transaction, allowing automatic rollback after the test.
    """
    user_fields = {k: v for k, v in user_data.items() if k != 'password'}
    user = User(
        **user_fields,
        hashed_password=hash_password(user_data['password']),
        role=UserRoleEnum.USER,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.fixture
async def auth_headers(test_user) -> dict:
    """Provide JWT authorization headers for a regular user."""
    token = create_access_token({'sub': str(test_user.id)})
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
async def admin_user(db, user_data) -> User:
    """
    Create admin user directly in database without commit.

    Uses flush instead of commit to keep changes within the test
    transaction, allowing automatic rollback after the test.
    """
    user_fields = {k: v for k, v in user_data.items() if k != 'password'}
    user = User(
        **user_fields,
        hashed_password=hash_password(user_data['password']),
        role=UserRoleEnum.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest.fixture
async def admin_headers(admin_user) -> dict:
    """Provide JWT authorization headers for an admin user."""
    token = create_access_token({'sub': str(admin_user.id)})
    return {'Authorization': f'Bearer {token}'}