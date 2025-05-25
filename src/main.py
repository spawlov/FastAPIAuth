from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn

from api import router as api_router
from fastapi import FastAPI

from core.models import Base
from core.models.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(
    api_router,
)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        reload=True,
    )
