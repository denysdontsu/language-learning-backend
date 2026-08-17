# Standard library
import subprocess

# Third-party
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

load_dotenv('.test.env', override=True)

# App
from app.core.config import settings


def pytest_configure(config):
    """Run once before any tests - apply migrations."""
    assert settings.is_testing, "Tests must run with ENVIRONMENT=testing"
    subprocess.run(['alembic', 'upgrade', 'head'], check=True)


test_engine = create_async_engine(
    settings.database_url,
    echo=False,
)

test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    join_transaction_mode="create_savepoint",
)


@pytest.fixture
async def db():
    """
    Provide test database session with automatic rollback after each test.

    Uses join_transaction_mode='create_savepoint' so that session.commit()
    calls inside service functions commit only to a savepoint, not to the
    real database. The outer transaction is rolled back after the test,
    keeping the database clean.
    """
    async with test_engine.connect() as connection:
        await connection.begin()
        async with test_session_maker(bind=connection) as session:
            yield session
        await connection.rollback()