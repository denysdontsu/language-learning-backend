"""
Add user role enum

Revision ID: 9d7c65ea9a7c
Revises: bf1b5c6bd1d9
Create Date: 2026-01-31 15:54:07.982571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d7c65ea9a7c'
down_revision = 'bf1b5c6bd1d9'
branch_labels = None
depends_on = None


def upgrade():
    # Create Enum type 'user_role'
    user_role_enum = sa.Enum('user', 'admin', name='user_role')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Change the column type from VARCHAR to ENUM
    op.alter_column('users', 'role',
                    existing_type=sa.VARCHAR(length=20),
                    type_=user_role_enum,
                    existing_nullable=False,
                    postgresql_using='role::user_role'
                    )


def downgrade():
    # Return VARCHAR
    op.alter_column('users', 'role',
                    existing_type=sa.Enum('user', 'admin', name='user_role'),
                    type_=sa.VARCHAR(length=20),
                    existing_nullable=False
                    )

    # Delete Enum type 'user_role'
    user_role_enum = sa.Enum('user', 'admin', name='user_role')
    user_role_enum.drop(op.get_bind(), checkfirst=True)

