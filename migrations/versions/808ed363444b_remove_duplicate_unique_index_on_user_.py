"""Remove duplicate unique index on user_level_languages

Revision ID: 808ed363444b
Revises: f363429e20bf
Create Date: 2026-01-07 00:46:58.721175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '808ed363444b'
down_revision = 'f363429e20bf'
branch_labels = None
depends_on = None



def upgrade():
    op.drop_index(
        'ix_user_language',
        table_name='user_level_languages'
    )

def downgrade():
    op.create_index(
        'ix_user_language',
        'user_level_languages',
        ['user_id', 'language'],
        unique=True
    )