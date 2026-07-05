from sqlalchemy import Column, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    sender: Mapped[str] = mapped_column(String(100), nullable=False)
    receiver: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    block_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
