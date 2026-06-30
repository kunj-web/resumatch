"""add tailor credit period

Revision ID: c3d9e7f1a6b2
Revises: b7e2a9d4c6f3
Create Date: 2026-06-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d9e7f1a6b2"
down_revision: Union[str, Sequence[str], None] = "b7e2a9d4c6f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "tailor_resume_credits_period",
            sa.String(length=7),
            nullable=False,
            server_default="",
        ),
    )
    op.alter_column("users", "tailor_resume_credits_period", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "tailor_resume_credits_period")
