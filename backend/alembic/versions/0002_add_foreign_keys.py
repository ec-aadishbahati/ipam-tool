from alembic import op
import sqlalchemy as sa

revision = "0002_add_foreign_keys"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "fk_subnets_supernet_id",
        "subnets",
        "supernets",
        ["supernet_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subnets_purpose_id",
        "subnets",
        "purposes",
        ["purpose_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subnets_vlan_id",
        "subnets",
        "vlans",
        ["vlan_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_devices_vlan_id",
        "devices",
        "vlans",
        ["vlan_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_ip_assignments_subnet_id",
        "ip_assignments",
        "subnets",
        ["subnet_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_ip_assignments_device_id",
        "ip_assignments",
        "devices",
        ["device_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_vlans_purpose_id",
        "vlans",
        "purposes",
        ["purpose_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_audit_logs_user_id",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_audit_logs_user_id", "audit_logs", type_="foreignkey")
    op.drop_constraint("fk_vlans_purpose_id", "vlans", type_="foreignkey")
    op.drop_constraint("fk_ip_assignments_device_id", "ip_assignments", type_="foreignkey")
    op.drop_constraint("fk_ip_assignments_subnet_id", "ip_assignments", type_="foreignkey")
    op.drop_constraint("fk_devices_vlan_id", "devices", type_="foreignkey")
    op.drop_constraint("fk_subnets_vlan_id", "subnets", type_="foreignkey")
    op.drop_constraint("fk_subnets_purpose_id", "subnets", type_="foreignkey")
    op.drop_constraint("fk_subnets_supernet_id", "subnets", type_="foreignkey")
