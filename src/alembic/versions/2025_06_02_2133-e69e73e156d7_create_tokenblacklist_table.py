"""Create TokenBlacklist table

Revision ID: e69e73e156d7
Revises: 817251d15875
Create Date: 2025-06-02 21:33:24.132780

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e69e73e156d7"
down_revision: Union[str, None] = "817251d15875"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tokenblacklists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_type", sa.String(length=10), nullable=False),
        sa.Column("reason", sa.String(length=50), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_tokenblacklists_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tokenblacklists")),
        sa.UniqueConstraint("jti", name=op.f("uq_tokenblacklists_jti")),
    )
    op.create_index(
        "ix_token_blacklist_created_at",
        "tokenblacklists",
        ["created_at"],
        unique=False,
    )
    op.create_index("ix_token_blacklist_jti", "tokenblacklists", ["jti"], unique=True)
    op.create_index(
        "ix_token_blacklist_user_id",
        "tokenblacklists",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_token_blacklist_user_id", table_name="tokenblacklists")
    op.drop_index("ix_token_blacklist_jti", table_name="tokenblacklists")
    op.drop_index("ix_token_blacklist_created_at", table_name="tokenblacklists")
    op.drop_table("tokenblacklists")
