from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: str
    status: str = "PENDING"
    block_id: str | None = None
    error_message: str | None = None


class TransactionRead(TransactionCreate):
    pass
