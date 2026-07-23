# Standard library
import subprocess

# Third-party
import pytest
from dotenv import load_dotenv

load_dotenv('.test.env', override=True)

# App
from app.core.config import settings
from app.db.connection import async_session_maker


def pytest_configure(config):
    """Run once before any tests - apply migrations."""
    assert settings.is_testing, "Tests must run with ENVIRONMENT=testing"
    subprocess.run(['alembic', 'upgrade', 'head'], check=True)


@pytest.fixture
async def db():
    """Provide test database session with automatic rollback."""
    async with async_session_maker() as session:
        async with session.begin():
            yield session
            await session.rollback()

