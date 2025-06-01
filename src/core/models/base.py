from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr


def get_naming_convention() -> dict[str, str]:
    conventions = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    return conventions


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=get_naming_convention(),
    )

    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"
