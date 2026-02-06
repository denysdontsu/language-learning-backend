from fastapi import APIRouter, Depends

from .users import router as users_router
from .languages import router as languages_router
from .exercises import router as exercises_router
from ...dependencies import require_admin

router = APIRouter(prefix='/admin',
                   dependencies=[Depends(require_admin)])

router.include_router(users_router)
router.include_router(languages_router)
router.include_router(exercises_router)

__all__ = ['router']