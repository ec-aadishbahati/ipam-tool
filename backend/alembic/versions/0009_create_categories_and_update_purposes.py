"""Create categories table and update purposes to use category_id

Revision ID: 0009_create_categories_and_update_purposes
Revises: 0008_add_device_metadata
Create Date: 2025-08-29 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0009_categories'
down_revision = '0008_device_meta'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect
    from alembic import context
    
    conn = context.get_bind()
    inspector = inspect(conn)
    
    if 'categories' not in inspector.get_table_names():
        op.create_table(
            'categories',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False, unique=True),
            sa.Column('description', sa.Text(), nullable=True),
        )
        op.create_index('ix_categories_name', 'categories', ['name'])
    
    existing_columns = [col['name'] for col in inspector.get_columns('purposes')]
    
    with op.batch_alter_table('purposes') as batch_op:
        if 'category_id' not in existing_columns:
            batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_purposes_category_id', 'categories', ['category_id'], ['id'])


def downgrade():
    with op.batch_alter_table('purposes') as batch_op:
        batch_op.drop_constraint('fk_purposes_category_id', type_='foreignkey')
        batch_op.drop_column('category_id')
    
    op.drop_index('ix_categories_name', 'categories')
    op.drop_table('categories')
