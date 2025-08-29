"""Add rack management tables and device rack relationship

Revision ID: 0007_add_rack_management
Revises: 0006_add_username_to_users
Create Date: 2025-08-29 02:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0007_add_rack_management'
down_revision = '0006_add_username_to_users'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect
    from alembic import context
    
    conn = context.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'racks' not in existing_tables:
        op.create_table(
            "racks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("aisle", sa.String(length=50), nullable=False),
            sa.Column("rack_number", sa.String(length=50), nullable=False),
            sa.Column("position_count", sa.Integer(), nullable=False, server_default="42"),
            sa.Column("power_type", sa.String(length=50), nullable=True),
            sa.Column("power_capacity", sa.String(length=100), nullable=True),
            sa.Column("cooling_type", sa.String(length=50), nullable=True),
            sa.Column("location", sa.String(length=255), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.UniqueConstraint("aisle", "rack_number", name="uq_rack_aisle_number"),
        )
    
    existing_columns = [col['name'] for col in inspector.get_columns('devices')]
    
    with op.batch_alter_table('devices') as batch_op:
        if 'rack_id' not in existing_columns:
            batch_op.add_column(sa.Column('rack_id', sa.Integer(), nullable=True))
        if 'rack_position' not in existing_columns:
            batch_op.add_column(sa.Column('rack_position', sa.Integer(), nullable=True))
        
        existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('devices')]
        if 'fk_device_rack' not in existing_fks:
            batch_op.create_foreign_key('fk_device_rack', 'racks', ['rack_id'], ['id'])


def downgrade():
    with op.batch_alter_table('devices') as batch_op:
        batch_op.drop_constraint('fk_device_rack', type_='foreignkey')
        batch_op.drop_column('rack_position')
        batch_op.drop_column('rack_id')
    op.drop_table("racks")
