"""add user plan and tailor credits

Revision ID: 2f3a6b9c1d4e
Revises: 8c1b4f7a2d9e
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f3a6b9c1d4e"
down_revision: Union[str, Sequence[str], None] = "8c1b4f7a2d9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_plan_enum = sa.Enum("FREE", "PRO", name="userplan")


def upgrade() -> None:
    user_plan_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column("plan", user_plan_enum, nullable=False, server_default="FREE"),
    )
    op.add_column(
        "users",
        sa.Column(
            "tailor_resume_credits_used",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column("users", "plan", server_default=None)
    op.alter_column("users", "tailor_resume_credits_used", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "tailor_resume_credits_used")
    op.drop_column("users", "plan")
    user_plan_enum.drop(op.get_bind(), checkfirst=True)
