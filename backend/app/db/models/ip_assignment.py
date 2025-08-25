from sqlalchemy import String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class IpAssignment(Base):
    __tablename__ = "ip_assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subnet_id: Mapped[int] = mapped_column(Integer, index=True)
    device_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(64))
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (UniqueConstraint("subnet_id", "ip_address", name="uq_subnet_ip"),)
