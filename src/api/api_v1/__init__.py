from core.settings import settings
from fastapi import APIRouter

from .hello import router as hello_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(
    hello_router,
    prefix="/hello",
    tags=["Hello"],
)
