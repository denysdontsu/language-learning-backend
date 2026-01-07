"""add fill_blank to exercise_type enum

Revision ID: e9d426e6d045
Revises: 808ed363444b
Create Date: 2026-01-07 22:05:26.310822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9d426e6d045'
down_revision = '808ed363444b'
branch_labels = None
depends_on = None


def upgrade():
    """Add 'fill_blank' value to exercise_type enum."""
    op.execute(
        "ALTER TYPE exercise_type ADD VALUE IF NOT EXISTS 'fill_blank'"
    )


def downgrade():
    """
        Cannot remove enum value in PostgreSQL directly.

        Workaround would require:
        1. Create new enum type without the value
        2. Convert all columns to new type
        3. Drop old type
        4. Rename new type

        This is complex and risky, so downgrade is not implemented.
        If needed, recreate database from scratch.
        """
    pass