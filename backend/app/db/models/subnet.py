from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Subnet(Base):
    __tablename__ = "subnets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supernet_id: Mapped[int | None] = mapped_column(ForeignKey("supernets.id"), nullable=True)
    cidr: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purpose_id: Mapped[int | None] = mapped_column(ForeignKey("purposes.id"), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gateway_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlans.id"), nullable=True)
    site: Mapped[str | None] = mapped_column(String(50), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(50), nullable=True)

    supernet: Mapped[Optional["Supernet"]] = relationship("Supernet", back_populates="subnets")
    purpose: Mapped[Optional["Purpose"]] = relationship("Purpose", back_populates="subnets")
    vlan: Mapped[Optional["Vlan"]] = relationship("Vlan", back_populates="subnets")
    ip_assignments: Mapped[list["IpAssignment"]] = relationship(
        "IpAssignment", back_populates="subnet", cascade="all, delete-orphan"
    )
