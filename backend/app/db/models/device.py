from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vlan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
