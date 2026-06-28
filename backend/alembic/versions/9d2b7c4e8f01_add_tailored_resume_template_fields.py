"""add tailored resume template fields

Revision ID: 9d2b7c4e8f01
Revises: 7a9c2e4f6b1d
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d2b7c4e8f01"
down_revision: Union[str, Sequence[str], None] = "7a9c2e4f6b1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tailored_resumes",
        sa.Column(
            "template_key",
            sa.String(length=50),
            nullable=False,
            server_default="ats_classic",
        ),
    )
    op.add_column(
        "tailored_resumes",
        sa.Column(
            "output_format",
            sa.String(length=10),
            nullable=False,
            server_default="docx",
        ),
    )
    op.add_column(
        "tailored_resumes",
        sa.Column("final_file_name", sa.String(), nullable=True),
    )
    op.add_column(
        "tailored_resumes",
        sa.Column("final_file_path", sa.String(), nullable=True),
    )

    op.alter_column("tailored_resumes", "template_key", server_default=None)
    op.alter_column("tailored_resumes", "output_format", server_default=None)


def downgrade() -> None:
    op.drop_column("tailored_resumes", "final_file_path")
    op.drop_column("tailored_resumes", "final_file_name")
    op.drop_column("tailored_resumes", "output_format")
    op.drop_column("tailored_resumes", "template_key")
