"""Add subnet allocation fields

Revision ID: 0004_add_subnet_allocation_fields
Revises: 0003_add_cascade_delete_constraints
Create Date: 2025-08-27 15:33:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0004_subnet_alloc'
down_revision = '0003_cascade_delete'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subnets', sa.Column('allocation_mode', sa.String(20), nullable=False, server_default='manual'))
    op.add_column('subnets', sa.Column('gateway_mode', sa.String(20), nullable=False, server_default='manual'))
    op.add_column('subnets', sa.Column('subnet_mask', sa.Integer(), nullable=True))
    op.add_column('subnets', sa.Column('host_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('subnets', 'host_count')
    op.drop_column('subnets', 'subnet_mask')
    op.drop_column('subnets', 'gateway_mode')
    op.drop_column('subnets', 'allocation_mode')
