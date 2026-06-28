"""create tailored resumes

Revision ID: 7a9c2e4f6b1d
Revises: 2f3a6b9c1d4e
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7a9c2e4f6b1d"
down_revision: Union[str, Sequence[str], None] = "2f3a6b9c1d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tailored_resume_status_enum = postgresql.ENUM(
    "DRAFT",
    "FINALIZED",
    "FAILED",
    name="tailoredresumestatus",
    create_type=False,
)


def upgrade() -> None:
    postgresql.ENUM(
        "DRAFT",
        "FINALIZED",
        "FAILED",
        name="tailoredresumestatus",
    ).create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tailored_resumes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("source_resume_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            tailored_resume_status_enum,
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column(
            "draft_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "edited_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "unsupported_gaps",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("finalized_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tailored_resumes_job_id"),
        "tailored_resumes",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tailored_resumes_source_resume_id"),
        "tailored_resumes",
        ["source_resume_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tailored_resumes_user_id"),
        "tailored_resumes",
        ["user_id"],
        unique=False,
    )

    op.alter_column("tailored_resumes", "status", server_default=None)
    op.alter_column("tailored_resumes", "draft_content", server_default=None)
    op.alter_column("tailored_resumes", "unsupported_gaps", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_tailored_resumes_user_id"), table_name="tailored_resumes")
    op.drop_index(
        op.f("ix_tailored_resumes_source_resume_id"), table_name="tailored_resumes"
    )
    op.drop_index(op.f("ix_tailored_resumes_job_id"), table_name="tailored_resumes")
    op.drop_table("tailored_resumes")
    tailored_resume_status_enum.drop(op.get_bind(), checkfirst=True)
