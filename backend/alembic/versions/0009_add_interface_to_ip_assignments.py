"""Add interface field to ip_assignments

Revision ID: 0009_add_interface_to_ip_assignments
Revises: 0008_add_device_metadata
Create Date: 2025-08-31 00:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0009_add_interface_to_ip_assignments'
down_revision = '0008_add_device_metadata'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect
    from alembic import context
    
    conn = context.get_bind()
    inspector = inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('ip_assignments')]
    
    with op.batch_alter_table('ip_assignments') as batch_op:
        if 'interface' not in existing_columns:
            batch_op.add_column(sa.Column('interface', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('ip_assignments') as batch_op:
        batch_op.drop_column('interface')
