from core.settings import settings
from fastapi import APIRouter

from .api_v1 import router as api_v1_router

router = APIRouter(
    prefix=settings.api.prefix,
)
router.include_router(
    api_v1_router,
)
