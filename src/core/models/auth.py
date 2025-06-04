from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base
from core.models.mixins.id_int_pk import IdIntPKMixin
from core.schemas.auth import TokenType


class TokenBlacklist(IdIntPKMixin, Base):
    jti: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_type: Mapped[TokenType] = mapped_column(
        String(10),
        nullable=False,
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc),
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_token_blacklist_user_id",
            "user_id",
        ),
        Index(
            "ix_token_blacklist_jti",
            "jti",
            unique=True,
        ),
        Index(
            "ix_token_blacklist_created_at",
            "created_at",
        ),
    )
