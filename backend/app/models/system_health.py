from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SystemHealthModel(Base):
    __tablename__ = "system_health"

    component: Mapped[str] = mapped_column(String(100), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    response_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False)
    uptime_percent: Mapped[float] = mapped_column(Float, nullable=False)
    last_updated: Mapped[str] = mapped_column(String(100), nullable=False)
