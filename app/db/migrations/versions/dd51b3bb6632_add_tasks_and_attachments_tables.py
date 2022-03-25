"""Add tasks and attachments tables

Revision ID: dd51b3bb6632
Revises: d6e3a38b1fbd
Create Date: 2022-03-25 15:05:44.250611

Doc: https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'dd51b3bb6632'
down_revision = 'd6e3a38b1fbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_huid', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('mentioned_colleague', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('attachment_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('attachment_id')
    )
    op.create_table('attachments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file_storage_uuid', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('filename', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['tasks.attachment_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('attachments')
    op.drop_table('tasks')
    # ### end Alembic commands ###