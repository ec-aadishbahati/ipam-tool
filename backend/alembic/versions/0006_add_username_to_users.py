"""Add username field to users table

Revision ID: 0006_add_username_to_users
Revises: 0005_add_user_password_fields
Create Date: 2025-08-29 01:54:54.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0006_add_username_to_users'
down_revision = '0005_add_user_password_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))
    
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    op.execute("UPDATE users SET username = 'admin' WHERE is_admin = 1")
    op.execute("UPDATE users SET username = email WHERE is_admin = 0")
    
    op.alter_column('users', 'username', nullable=False)


def downgrade():
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')
