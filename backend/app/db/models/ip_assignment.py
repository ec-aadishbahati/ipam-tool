from typing import Optional
from sqlalchemy import String, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class IpAssignment(Base):
    __tablename__ = "ip_assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subnet_id: Mapped[int] = mapped_column(ForeignKey("subnets.id"), index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(64))
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (UniqueConstraint("subnet_id", "ip_address", name="uq_subnet_ip"),)

    subnet: Mapped["Subnet"] = relationship("Subnet", back_populates="ip_assignments")
    device: Mapped[Optional["Device"]] = relationship("Device", back_populates="ip_assignments")
