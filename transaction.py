from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Transaction:
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: str
    status: str = "PENDING"
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "status": self.status,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Transaction":
        return cls(
            transaction_id=payload["transaction_id"],
            sender=payload["sender"],
            receiver=payload["receiver"],
            amount=float(payload["amount"]),
            timestamp=payload.get("timestamp", datetime.now(timezone.utc).isoformat()),
            status=payload.get("status", "PENDING"),
            error_message=payload.get("error_message"),
        )
