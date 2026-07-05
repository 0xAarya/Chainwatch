from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BlockModel(Base):
    __tablename__ = "blocks"

    block_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(100), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    transaction_count: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
