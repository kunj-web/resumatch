"""create upgrade interests

Revision ID: d8f2a1c6b4e7
Revises: c3d9e7f1a6b2
Create Date: 2026-07-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d8f2a1c6b4e7"
down_revision: Union[str, Sequence[str], None] = "c3d9e7f1a6b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "upgrade_interests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "source",
            name="uq_upgrade_interests_user_source",
        ),
    )
    op.create_index(
        op.f("ix_upgrade_interests_email"),
        "upgrade_interests",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_upgrade_interests_user_id"),
        "upgrade_interests",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_upgrade_interests_user_id"), table_name="upgrade_interests")
    op.drop_index(op.f("ix_upgrade_interests_email"), table_name="upgrade_interests")
    op.drop_table("upgrade_interests")
