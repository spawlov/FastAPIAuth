from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def root():
    return {
        "detail": "success",
        "message": "Hello, World",
    }


@router.get("/{name}")
async def say_hello(name: str):
    return {
        "detail": "success",
        "message": f"Hello, {name}",
    }
