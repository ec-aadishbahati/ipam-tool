from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Subnet(Base):
    __tablename__ = "subnets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supernet_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cidr: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purpose_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gateway_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vlan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    site: Mapped[str | None] = mapped_column(String(50), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(50), nullable=True)
