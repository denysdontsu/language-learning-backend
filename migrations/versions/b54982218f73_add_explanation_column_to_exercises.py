"""Add explanation column to exercises

Revision ID: b54982218f73
Revises: 9d7c65ea9a7c
Create Date: 2026-02-02 16:21:35.481196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b54982218f73'
down_revision = '9d7c65ea9a7c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('exercises', sa.Column('explanation', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('exercises', 'explanation')