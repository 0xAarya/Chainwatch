from pydantic import BaseModel


class IncidentCreate(BaseModel):
    incident_type: str
    transaction_id: str
    description: str
    severity: str
    timestamp: str
    resolution_status: str = "OPEN"
    probable_cause: str | None = None
    affected_component: str | None = None
    recommended_action: str | None = None


class IncidentRead(IncidentCreate):
    incident_id: str
