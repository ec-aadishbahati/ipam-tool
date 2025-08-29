from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Purpose(Base):
    __tablename__ = "purposes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    category_rel: Mapped[Optional["Category"]] = relationship("Category", back_populates="purposes")
    subnets: Mapped[list["Subnet"]] = relationship("Subnet", back_populates="purpose", cascade="all, delete-orphan")
    vlans: Mapped[list["Vlan"]] = relationship("Vlan", back_populates="purpose", cascade="all, delete-orphan")
    supernets: Mapped[list["Supernet"]] = relationship("Supernet", back_populates="purpose")
