"""Add cascade delete constraints to foreign key relationships

Revision ID: 0003_add_cascade_delete_constraints
Revises: 0002_add_foreign_keys
Create Date: 2025-08-26 10:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0003_cascade_delete'
down_revision = '0002_add_foreign_keys'
branch_labels = None
depends_on = None


def upgrade() -> None:
    
    with op.batch_alter_table('vlans') as batch_op:
        batch_op.drop_constraint('fk_vlans_purpose_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_vlans_purpose_id', 'purposes', ['purpose_id'], ['id'], ondelete='CASCADE')
    
    with op.batch_alter_table('subnets') as batch_op:
        batch_op.drop_constraint('fk_subnets_supernet_id', type_='foreignkey')
        batch_op.drop_constraint('fk_subnets_purpose_id', type_='foreignkey')
        batch_op.drop_constraint('fk_subnets_vlan_id', type_='foreignkey')
        
        batch_op.create_foreign_key('fk_subnets_supernet_id', 'supernets', ['supernet_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_subnets_purpose_id', 'purposes', ['purpose_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_subnets_vlan_id', 'vlans', ['vlan_id'], ['id'], ondelete='CASCADE')
    
    with op.batch_alter_table('devices') as batch_op:
        batch_op.drop_constraint('fk_devices_vlan_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_devices_vlan_id', 'vlans', ['vlan_id'], ['id'], ondelete='CASCADE')
    
    with op.batch_alter_table('ip_assignments') as batch_op:
        batch_op.drop_constraint('fk_ip_assignments_subnet_id', type_='foreignkey')
        batch_op.drop_constraint('fk_ip_assignments_device_id', type_='foreignkey')
        
        batch_op.create_foreign_key('fk_ip_assignments_subnet_id', 'subnets', ['subnet_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_ip_assignments_device_id', 'devices', ['device_id'], ['id'], ondelete='CASCADE')
    
    with op.batch_alter_table('audit_logs') as batch_op:
        batch_op.drop_constraint('fk_audit_logs_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_audit_logs_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    
    with op.batch_alter_table('audit_logs') as batch_op:
        batch_op.drop_constraint('fk_audit_logs_user_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_audit_logs_user_id', 'users', ['user_id'], ['id'])
    
    with op.batch_alter_table('ip_assignments') as batch_op:
        batch_op.drop_constraint('fk_ip_assignments_device_id', type_='foreignkey')
        batch_op.drop_constraint('fk_ip_assignments_subnet_id', type_='foreignkey')
        
        batch_op.create_foreign_key('fk_ip_assignments_device_id', 'devices', ['device_id'], ['id'])
        batch_op.create_foreign_key('fk_ip_assignments_subnet_id', 'subnets', ['subnet_id'], ['id'])
    
    with op.batch_alter_table('devices') as batch_op:
        batch_op.drop_constraint('fk_devices_vlan_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_devices_vlan_id', 'vlans', ['vlan_id'], ['id'])
    
    with op.batch_alter_table('subnets') as batch_op:
        batch_op.drop_constraint('fk_subnets_vlan_id', type_='foreignkey')
        batch_op.drop_constraint('fk_subnets_purpose_id', type_='foreignkey')
        batch_op.drop_constraint('fk_subnets_supernet_id', type_='foreignkey')
        
        batch_op.create_foreign_key('fk_subnets_vlan_id', 'vlans', ['vlan_id'], ['id'])
        batch_op.create_foreign_key('fk_subnets_purpose_id', 'purposes', ['purpose_id'], ['id'])
        batch_op.create_foreign_key('fk_subnets_supernet_id', 'supernets', ['supernet_id'], ['id'])
    
    with op.batch_alter_table('vlans') as batch_op:
        batch_op.drop_constraint('fk_vlans_purpose_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_vlans_purpose_id', 'purposes', ['purpose_id'], ['id'])
