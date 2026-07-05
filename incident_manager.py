from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from config import DEFAULT_SEVERITY, SEVERITY_BY_TYPE


@dataclass
class Incident:
    incident_id: str
    incident_type: str
    transaction_id: str
    description: str
    severity: str
    timestamp: str
    resolution_status: str = "OPEN"

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "incident_type": self.incident_type,
            "transaction_id": self.transaction_id,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "resolution_status": self.resolution_status,
        }


def create_incident(transaction_id: str, incident_type: str, description: str) -> Incident:
    timestamp = datetime.now(timezone.utc).isoformat()
    severity = SEVERITY_BY_TYPE.get(incident_type, DEFAULT_SEVERITY)
    incident_id = f"incident-{timestamp.replace(':', '').replace('-', '').replace('.', '')}"
    return Incident(
        incident_id=incident_id,
        incident_type=incident_type,
        transaction_id=transaction_id,
        description=description,
        severity=severity,
        timestamp=timestamp,
    )
