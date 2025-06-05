from typing import Any

USER: dict[str, Any] = {
    "id": 1,
    "nickname": "test_user",
    "password": "user_password",
    "first_name": "Test",
    "last_name": "User",
    "email": "user@example.com",
    "is_active": True,
    "is_superuser": False,
}

SUPERUSER: dict[str, Any] = {
    "id": 2,
    "nickname": "super_user",
    "password": "super_password",
    "first_name": "Super",
    "last_name": "User",
    "email": "root@example.com",
    "is_active": True,
    "is_superuser": True,
}

ACCESS_TOKEN: str = "jwt.access.token"
REFRESH_TOKEN: str = "jwt.refresh.token"
