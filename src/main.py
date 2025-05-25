from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn

from api import router as api_router
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


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
