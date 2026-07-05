from sqlalchemy import Column, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    incident_type: Mapped[str] = mapped_column(String(100), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(100), nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    probable_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_component: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
