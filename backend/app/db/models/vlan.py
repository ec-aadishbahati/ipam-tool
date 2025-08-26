from typing import Optional
from sqlalchemy import String, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Vlan(Base):
    __tablename__ = "vlans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site: Mapped[str] = mapped_column(String(50), index=True)
    environment: Mapped[str] = mapped_column(String(50), index=True)
    vlan_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    purpose_id: Mapped[int | None] = mapped_column(ForeignKey("purposes.id"), nullable=True)

    __table_args__ = (UniqueConstraint("site", "environment", "vlan_id", name="uq_vlan_site_env_id"),)

    purpose: Mapped[Optional["Purpose"]] = relationship("Purpose", back_populates="vlans")
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="vlan", cascade="all, delete-orphan")
    subnets: Mapped[list["Subnet"]] = relationship("Subnet", back_populates="vlan", cascade="all, delete-orphan")
