"""default tailored resume output to pdf

Revision ID: a4f1c8d2e9b0
Revises: 9d2b7c4e8f01
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4f1c8d2e9b0"
down_revision: Union[str, Sequence[str], None] = "9d2b7c4e8f01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE tailored_resumes
        SET output_format = 'pdf'
        WHERE output_format = 'docx'
          AND final_file_path IS NULL
        """
    )
    op.alter_column(
        "tailored_resumes",
        "output_format",
        existing_type=sa.String(length=10),
        server_default="pdf",
    )
    op.alter_column("tailored_resumes", "output_format", server_default=None)


def downgrade() -> None:
    op.alter_column(
        "tailored_resumes",
        "output_format",
        existing_type=sa.String(length=10),
        server_default="docx",
    )
    op.alter_column("tailored_resumes", "output_format", server_default=None)
