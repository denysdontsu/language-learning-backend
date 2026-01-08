from fastapi import APIRouter, status

from app.api.dependencies import db_dependency
from app.services.auth import register_user_simple
from app.schemas.user import UserCreate, UserBrief

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register',
             status_code=status.HTTP_201_CREATED,
             response_model=UserBrief)
async def register(
        user_data: UserCreate,
        db: db_dependency
):
    """Simple registration"""
    return await register_user_simple(db, user_data)