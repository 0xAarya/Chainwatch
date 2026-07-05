from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import List

from app.database.base import SessionLocal
from app.models.incident import IncidentModel
from app.models.transaction import TransactionModel
from app.models.system_health import SystemHealthModel
from app.models.log_entry import ApplicationLogModel

logger = logging.getLogger("chainwatch.monitoring")


class MonitoringService:
    def __init__(self) -> None:
        self.logger = logger

    def create_incident(self, transaction_id: str, incident_type: str, description: str, severity: str, probable_cause: str, affected_component: str, recommended_action: str) -> IncidentModel:
        incident = IncidentModel(
            incident_id=f"incident-{uuid.uuid4().hex[:8]}",
            incident_type=incident_type,
            transaction_id=transaction_id,
            description=description,
            severity=severity,
            timestamp=datetime.now(timezone.utc).isoformat(),
            resolution_status="OPEN",
            probable_cause=probable_cause,
            affected_component=affected_component,
            recommended_action=recommended_action,
        )
        with SessionLocal() as session:
            session.add(incident)
            session.commit()
            session.refresh(incident)
        return incident

    def inspect_transaction(self, transaction: TransactionModel) -> list[IncidentModel]:
        incidents: list[IncidentModel] = []
        if transaction.status == "FAILED":
            incidents.append(self.create_incident(
                transaction.transaction_id,
                "FAILED_TRANSACTION",
                "Transaction failed during processing",
                "HIGH",
                "Simulated downstream processing failure",
                "Transaction Processor",
                "Inspect processor logs and retry the transaction",
            ))
        if transaction.amount <= 0:
            incidents.append(self.create_incident(
                transaction.transaction_id,
                "INVALID_AMOUNT",
                "Transaction amount is zero or negative",
                "CRITICAL",
                "Invalid input validation",
                "API Server",
                "Validate transaction payloads before ingestion",
            ))
        if transaction.amount > 1500:
            incidents.append(self.create_incident(
                transaction.transaction_id,
                "UNUSUALLY_HIGH_AMOUNT",
                "Transaction amount is unusually high",
                "HIGH",
                "Suspicious payment volume",
                "Monitoring Engine",
                "Review the transaction context and threshold policy",
            ))
        if transaction.status == "PENDING":
            incidents.append(self.create_incident(
                transaction.transaction_id,
                "PENDING_TRANSACTION",
                "Transaction remained pending too long",
                "MEDIUM",
                "Processing delay or queue congestion",
                "Transaction Processor",
                "Inspect queue health and retry policy",
            ))
        return incidents

    def seed_health(self) -> None:
        components = [
            ("Blockchain Node", "OPERATIONAL", 18.0, 0.01, 99.9),
            ("Transaction Processor", "DEGRADED", 120.0, 0.04, 98.5),
            ("Database", "OPERATIONAL", 15.0, 0.02, 99.8),
            ("Monitoring Engine", "OPERATIONAL", 22.0, 0.01, 99.7),
            ("Incident Service", "OPERATIONAL", 24.0, 0.01, 99.6),
            ("API Server", "DEGRADED", 90.0, 0.05, 97.8),
        ]
        with SessionLocal() as session:
            for name, status, latency, error_rate, uptime in components:
                health = session.get(SystemHealthModel, name)
                if health is None:
                    session.add(SystemHealthModel(
                        component=name,
                        status=status,
                        response_latency_ms=latency,
                        error_rate=error_rate,
                        uptime_percent=uptime,
                        last_updated=datetime.now(timezone.utc).isoformat(),
                    ))
            session.commit()

    def log_event(self, level: str, component: str, message: str) -> None:
        entry = ApplicationLogModel(
            level=level,
            component=component,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        with SessionLocal() as session:
            session.add(entry)
            session.commit()
