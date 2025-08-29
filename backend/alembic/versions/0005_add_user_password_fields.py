"""Add user password fields

Revision ID: 0005_add_user_password_fields
Revises: 0004_add_subnet_allocation_fields
Create Date: 2025-08-28 04:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '0005_user_password'
down_revision = '0004_subnet_alloc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('users', 'must_change_password')
    op.drop_column('users', 'password_changed_at')
