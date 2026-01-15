"""Add status column with check constraint

Replace column boolean is_active with enum-based status in table 'user_exercise_history'.
Make user_answer nullable to support skip status.
Add 'check_status' constraint in 'user_exercise_history' table

Revision ID: 102ceb88b4ed
Revises: 860522b56861
Create Date: 2026-01-15 16:50:05.963613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '756af3813bf4'
down_revision = '860522b56861'
branch_labels = None
depends_on = None


def upgrade():
    # Create Enum type 'exercise_status'
    exercise_status = sa.Enum('correct', 'incorrect', 'skip', name='exercise_status')
    exercise_status.create(op.get_bind())

    # Add new column 'status'
    op.add_column('user_exercise_history',
                  sa.Column('status', exercise_status, nullable=False))

    # Make 'user_answer' nullable
    op.alter_column('user_exercise_history',
                    'user_answer',
                    existing_type=sa.Text(),
                    nullable=True)

    # Add check constraint 'check_status'
    op.create_check_constraint(
        'check_status',
        'user_exercise_history',
        """
        ((status = 'skip') AND user_answer IS NULL)
        OR
        ((status IN ('incorrect', 'correct')) AND user_answer IS NOT NULL)
        """
    )

    # Delete old column
    op.drop_column('user_exercise_history', 'is_active')


def downgrade():
    # Add back old column
    op.add_column('user_exercise_history',
                  sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))

    # Delete check constrain 'check_status'
    op.drop_constraint(
        'check_status',
        'user_exercise_history',
        type_='check'
    )

    # Make 'user_answer' NOT NULL again
    op.execute("UPDATE user_exercise_history SET user_answer = '' WHERE user_answer IS NULL")
    op.alter_column('user_exercise_history',
                    'user_answer',
                    existing_type=sa.Text(),
                    nullable=False)

    # Drop new column 'status'
    op.drop_column('user_exercise_history', 'status')

    # Drop Enum type 'exercise_status'
    exercise_status = sa.Enum('correct', 'incorrect', 'skip', name='exercise_status')
    exercise_status.drop(op.get_bind())

