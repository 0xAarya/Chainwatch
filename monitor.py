import logging
from datetime import datetime, timedelta
from typing import List, Optional

from config import HIGH_AMOUNT_THRESHOLD, TRANSACTION_TIMEOUT_SECONDS
from incident_manager import Incident, create_incident
from transaction import Transaction


class TransactionMonitor:
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger("chainwatch.monitor")

    def inspect_transactions(self, transactions: List[Transaction]) -> List[Incident]:
        incidents: List[Incident] = []
        seen_ids = set()

        for transaction in transactions:
            if transaction.transaction_id in seen_ids:
                incident = create_incident(
                    transaction.transaction_id,
                    "DUPLICATE_TRANSACTION_ID",
                    f"Duplicate transaction detected for {transaction.transaction_id}",
                )
                incidents.append(incident)
                self.logger.warning("Duplicate transaction detected: %s", transaction.transaction_id)
            else:
                seen_ids.add(transaction.transaction_id)

            if transaction.status == "FAILED":
                incident = create_incident(
                    transaction.transaction_id,
                    "FAILED_TRANSACTION",
                    f"Transaction {transaction.transaction_id} failed",
                )
                incidents.append(incident)
                self.logger.error("Failed transaction detected: %s", transaction.transaction_id)

            if transaction.amount <= 0:
                incident = create_incident(
                    transaction.transaction_id,
                    "INVALID_AMOUNT",
                    f"Transaction {transaction.transaction_id} has an invalid amount",
                )
                incidents.append(incident)
                self.logger.error("Invalid amount detected: %s", transaction.transaction_id)

            if transaction.amount > HIGH_AMOUNT_THRESHOLD:
                incident = create_incident(
                    transaction.transaction_id,
                    "UNUSUALLY_HIGH_AMOUNT",
                    f"Transaction {transaction.transaction_id} exceeds the high amount threshold",
                )
                incidents.append(incident)
                self.logger.warning("High amount detected: %s", transaction.transaction_id)

            if transaction.status == "PENDING":
                try:
                    timestamp = datetime.fromisoformat(transaction.timestamp)
                except ValueError:
                    timestamp = datetime.utcnow()

                if datetime.utcnow() - timestamp > timedelta(seconds=TRANSACTION_TIMEOUT_SECONDS):
                    incident = create_incident(
                        transaction.transaction_id,
                        "PENDING_TRANSACTION",
                        f"Transaction {transaction.transaction_id} stayed pending too long",
                    )
                    incidents.append(incident)
                    self.logger.warning("Pending transaction timed out: %s", transaction.transaction_id)

        return incidents
