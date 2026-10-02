"""create job search tables

Revision ID: 20260913_01
Revises:
Create Date: 2026-09-13
"""
from alembic import op
import sqlalchemy as sa


revision = "20260913_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("company", sa.String(length=300)),
        sa.Column("location", sa.String(length=300)),
        sa.Column("description_snippet", sa.Text()),
        sa.Column("salary", sa.String(length=200)),
        sa.Column("employment_type", sa.String(length=100)),
        sa.Column("source", sa.String(length=200)),
        sa.Column("external_url", sa.Text(), nullable=False),
        sa.Column("provider_updated_at", sa.DateTime(timezone=True)),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "external_id", name="uq_job_offer_provider_external_id"),
    )
    op.create_table(
        "favorite_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_offer_id", sa.Integer(), sa.ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "job_offer_id", name="uq_favorite_user_offer"),
    )
    op.create_index("ix_favorite_jobs_user_id", "favorite_jobs", ["user_id"])
    op.create_index("ix_favorite_jobs_job_offer_id", "favorite_jobs", ["job_offer_id"])


def downgrade() -> None:
    op.drop_table("favorite_jobs")
    op.drop_table("job_offers")
