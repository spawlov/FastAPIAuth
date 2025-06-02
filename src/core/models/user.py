from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base
from core.models.mixins.id_int_pk import IdIntPKMixin


class User(IdIntPKMixin, Base):
    nickname: Mapped[str] = mapped_column(
        unique=True,
    )
    password: Mapped[str]
    first_name: Mapped[str] = mapped_column(
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        unique=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
    )
