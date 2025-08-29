from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_table(
        "purposes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
    )
    op.create_table(
        "vlans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site", sa.String(length=50), nullable=False),
        sa.Column("environment", sa.String(length=50), nullable=False),
        sa.Column("vlan_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("purpose_id", sa.Integer(), nullable=True),
        sa.UniqueConstraint("site", "environment", "vlan_id", name="uq_vlan_site_env_id"),
    )
    op.create_table(
        "supernets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cidr", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("site", sa.String(length=50), nullable=True),
        sa.Column("environment", sa.String(length=50), nullable=True),
    )
    op.create_table(
        "subnets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("supernet_id", sa.Integer(), nullable=True),
        sa.Column("cidr", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("purpose_id", sa.Integer(), nullable=True),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("gateway_ip", sa.String(length=64), nullable=True),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
        sa.Column("site", sa.String(length=50), nullable=True),
        sa.Column("environment", sa.String(length=50), nullable=True),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
    )
    op.create_table(
        "ip_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subnet_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.UniqueConstraint("subnet_id", "ip_address", name="uq_subnet_ip"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("before", sa.Text(), nullable=True),
        sa.Column("after", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("ip_assignments")
    op.drop_table("devices")
    op.drop_table("subnets")
    op.drop_table("supernets")
    op.drop_table("vlans")
    op.drop_table("purposes")
    op.drop_table("users")
