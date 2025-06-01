from core.settings import settings
from fastapi import APIRouter

from .auth.auth import router as auth_router
from .users.users import router as users_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)
router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)
