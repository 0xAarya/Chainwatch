from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from transaction import Transaction


@dataclass
class Block:
    block_id: str
    transactions: List[Transaction] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "transaction_count": len(self.transactions),
            "timestamp": self.timestamp,
        }
