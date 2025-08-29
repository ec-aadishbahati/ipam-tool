"""Add vendor and serial_number fields to devices

Revision ID: 0008_add_device_metadata
Revises: 0007_add_rack_management
Create Date: 2025-08-29 11:11:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0008_device_meta'
down_revision = '0007_rack_mgmt'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect
    from alembic import context
    
    conn = context.get_bind()
    inspector = inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('devices')]
    
    with op.batch_alter_table('devices') as batch_op:
        if 'vendor' not in existing_columns:
            batch_op.add_column(sa.Column('vendor', sa.String(length=100), nullable=True))
        if 'serial_number' not in existing_columns:
            batch_op.add_column(sa.Column('serial_number', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('devices') as batch_op:
        batch_op.drop_column('serial_number')
        batch_op.drop_column('vendor')
