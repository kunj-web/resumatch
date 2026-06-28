"""add tailored resume rendered content

Revision ID: b7e2a9d4c6f3
Revises: a4f1c8d2e9b0
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b7e2a9d4c6f3"
down_revision: Union[str, Sequence[str], None] = "a4f1c8d2e9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tailored_resumes",
        sa.Column(
            "rendered_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("tailored_resumes", "rendered_content")
