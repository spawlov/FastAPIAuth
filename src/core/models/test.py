from sqlalchemy.orm import Mapped

from . import Base
from .mixins.id_int_pk import IdIntPKMixin


class Test(IdIntPKMixin, Base):
    field_one: Mapped[str]
    field_two: Mapped[int]
    field_three: Mapped[float]
    field_four: Mapped[bool]
