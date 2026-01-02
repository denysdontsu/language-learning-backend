from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import async_session_maker

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide async database session for dependency injection.

    Yields:
        AsyncSession: Database session that will be automatically closed
    """
    async with async_session_maker() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]


