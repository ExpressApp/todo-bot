"""add_tasks_table

Revision ID: 0f49c52ce1d8
Revises: c630e92c23e1
Create Date: 2021-04-15 16:15:23.472743

Doc: https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

revision = "0f49c52ce1d8"
down_revision = "18c27de1bcc0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("assignee", UUID, nullable=True),
        sa.Column(
            "attachment_id",
            UUID,
            ForeignKey("tasks_attachments_meta.id"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_table("tasks")
