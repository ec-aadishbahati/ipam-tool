from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

if TYPE_CHECKING:
    from .device import Device


class Rack(Base):
    __tablename__ = "racks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aisle: Mapped[str] = mapped_column(String(50), index=True)
    rack_number: Mapped[str] = mapped_column(String(50), index=True)
    position_count: Mapped[int] = mapped_column(Integer, server_default="42")
    power_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    power_capacity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cooling_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("aisle", "rack_number", name="uq_rack_aisle_number"),)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="rack")
