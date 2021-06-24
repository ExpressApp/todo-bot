"""create table tasks_attachments_meta

Revision ID: 18c27de1bcc0
Revises: 0f49c52ce1d8
Create Date: 2021-04-16 16:18:55.898776

Doc: https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "18c27de1bcc0"
down_revision = "c630e92c23e1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks_attachments_meta",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("filename", sa.String, nullable=False),
    )


def downgrade():
    op.drop_table("tasks_attachments_meta")
