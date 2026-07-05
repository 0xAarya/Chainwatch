from pathlib import Path

from blockchain import Block
from config import DB_PATH
from database import init_db, insert_block, insert_incident, insert_transaction
from incident_manager import create_incident
from monitor import TransactionMonitor
from transaction import Transaction


def generate_sample_data(db_path: str | Path | None = None) -> None:
    init_db(db_path)

    sample_transactions = [
        Transaction("tx-1001", "alice", "bob", 120.0, "2026-07-05T09:00:00", "SUCCESS"),
        Transaction("tx-1002", "carol", "dave", 2000.0, "2026-07-05T09:05:00", "SUCCESS"),
        Transaction("tx-1003", "erin", "frank", 75.0, "2026-07-05T09:10:00", "FAILED"),
        Transaction("tx-1004", "grace", "heidi", -10.0, "2026-07-05T09:15:00", "FAILED"),
        Transaction("tx-1005", "ivan", "judy", 50.0, "2026-07-05T09:20:00", "PENDING"),
        Transaction("tx-1005", "ivan", "judy", 50.0, "2026-07-05T09:25:00", "PENDING"),
    ]

    monitor = TransactionMonitor()
    incidents = monitor.inspect_transactions(sample_transactions)

    for transaction in sample_transactions:
        insert_transaction(transaction, db_path)

    for incident in incidents:
        insert_incident(incident, db_path)

    insert_block("block-001", len(sample_transactions), db_path)

    error_incident = create_incident("tx-1003", "APPLICATION_ERROR", "Simulated application error while processing transaction")
    insert_incident(error_incident, db_path)


if __name__ == "__main__":
    generate_sample_data(DB_PATH)
    print("Sample data generated")
