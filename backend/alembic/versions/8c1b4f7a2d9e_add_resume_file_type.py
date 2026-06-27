"""add resume file type

Revision ID: 8c1b4f7a2d9e
Revises: ebd804c57704
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c1b4f7a2d9e"
down_revision: Union[str, Sequence[str], None] = "ebd804c57704"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "resumes",
        sa.Column("file_type", sa.String(length=10), nullable=False, server_default="pdf"),
    )
    op.alter_column("resumes", "file_type", server_default=None)


def downgrade() -> None:
    op.drop_column("resumes", "file_type")
