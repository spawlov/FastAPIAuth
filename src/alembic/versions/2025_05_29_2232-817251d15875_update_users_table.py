"""Update Users table

Revision ID: 817251d15875
Revises: 03fcdc940e7e
Create Date: 2025-05-29 22:32:19.029175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "817251d15875"
down_revision: Union[str, None] = "03fcdc940e7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("password", sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password")
