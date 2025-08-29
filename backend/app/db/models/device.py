from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

if TYPE_CHECKING:
    from .vlan import Vlan
    from .rack import Rack
    from .ip_assignment import IpAssignment


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("vlans.id"), nullable=True)
    rack_id: Mapped[int | None] = mapped_column(ForeignKey("racks.id"), nullable=True)
    rack_position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    vlan: Mapped[Optional["Vlan"]] = relationship("Vlan", back_populates="devices")
    rack: Mapped[Optional["Rack"]] = relationship("Rack", back_populates="devices")
    ip_assignments: Mapped[list["IpAssignment"]] = relationship(
        "IpAssignment", back_populates="device", cascade="all, delete-orphan"
    )
