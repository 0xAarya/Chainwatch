from pydantic import BaseModel


class LogEntryRead(BaseModel):
    id: int
    level: str
    component: str
    message: str
    timestamp: str
