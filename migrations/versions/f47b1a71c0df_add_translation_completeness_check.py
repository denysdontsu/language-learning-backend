"""Add translation completeness check

Revision ID: f47b1a71c0df
Revises: 99a19fb9275f
Create Date: 2025-12-17 19:45:01.540652

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f47b1a71c0df'
down_revision: Union[str, Sequence[str], None] = '99a19fb9275f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CHECK constraint for translation completeness"""
    op.create_check_constraint(
        'check_translation_completed',
        'exercises',
        """
        (correct_answer_translation IS NULL AND answer_translation_language IS NULL) 
        OR 
        (correct_answer_translation IS NOT NULL AND answer_translation_language IS NOT NULL)
        """
    )


def downgrade() -> None:
    """Remove CHECK constraint"""
    op.drop_constraint(
        'check_translation_completed',
        'exercises',
        type_='check'
    )

