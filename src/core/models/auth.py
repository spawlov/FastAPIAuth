from datetime import datetime, timezone
from typing import Literal, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base
from core.models.mixins.id_int_pk import IdIntPKMixin


if TYPE_CHECKING:
    from core.models.user import User


TokenType = Literal["access", "refresh"]


class TokenBlacklist(IdIntPKMixin, Base):
    jti: Mapped[UUID] = mapped_column(
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
    user: Mapped["User"] = relationship(
        back_populates="revoked_tokens",
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
