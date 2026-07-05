from pydantic import BaseModel


class SystemHealthRead(BaseModel):
    component: str
    status: str
    response_latency_ms: float
    error_rate: float
    uptime_percent: float
    last_updated: str
