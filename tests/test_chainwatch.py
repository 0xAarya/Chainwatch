from pathlib import Path

from blockchain import Block
from database import get_incident_stats, get_transactions, init_db, insert_incident, insert_transaction
from incident_manager import Incident, create_incident
from monitor import TransactionMonitor
from transaction import Transaction


def test_transaction_creation():
    transaction = Transaction(
        transaction_id="tx-001",
        sender="alice",
        receiver="bob",
        amount=100.0,
        timestamp="2026-07-05T10:00:00",
        status="SUCCESS",
    )

    assert transaction.transaction_id == "tx-001"
    assert transaction.status == "SUCCESS"
    assert transaction.amount == 100.0


def test_block_creation():
    transaction = Transaction(
        transaction_id="tx-002",
        sender="carol",
        receiver="dave",
        amount=250.0,
        timestamp="2026-07-05T10:05:00",
        status="PENDING",
    )
    block = Block(block_id="block-001", transactions=[transaction])

    assert block.block_id == "block-001"
    assert len(block.transactions) == 1
    assert block.transactions[0].transaction_id == "tx-002"


def test_duplicate_transaction_detection():
    monitor = TransactionMonitor()
    transactions = [
        Transaction("dup-1", "alice", "bob", 50.0, "2026-07-05T11:00:00", "SUCCESS"),
        Transaction("dup-1", "alice", "bob", 50.0, "2026-07-05T11:01:00", "FAILED"),
    ]

    incidents = monitor.inspect_transactions(transactions)
    assert any(incident.incident_type == "DUPLICATE_TRANSACTION_ID" for incident in incidents)


def test_failed_transaction_detection():
    monitor = TransactionMonitor()
    transactions = [
        Transaction("tx-fail", "alice", "bob", 75.0, "2026-07-05T12:00:00", "FAILED"),
    ]

    incidents = monitor.inspect_transactions(transactions)
    assert any(incident.incident_type == "FAILED_TRANSACTION" for incident in incidents)


def test_invalid_amount_detection():
    monitor = TransactionMonitor()
    transactions = [
        Transaction("tx-invalid", "alice", "bob", -10.0, "2026-07-05T12:05:00", "FAILED"),
    ]

    incidents = monitor.inspect_transactions(transactions)
    assert any(incident.incident_type == "INVALID_AMOUNT" for incident in incidents)


def test_incident_creation_and_severity_assignment():
    incident = create_incident(
        transaction_id="tx-003",
        incident_type="UNUSUALLY_HIGH_AMOUNT",
        description="Amount over threshold",
    )

    assert isinstance(incident, Incident)
    assert incident.severity == "HIGH"


def test_database_operations(tmp_path):
    db_path = tmp_path / "chainwatch-test.db"
    init_db(str(db_path))

    transaction = Transaction("db-tx", "user-a", "user-b", 30.0, "2026-07-05T09:00:00", "SUCCESS")
    insert_transaction(transaction, str(db_path))

    incident = create_incident("db-tx", "FAILED_TRANSACTION", "Simulated failure")
    insert_incident(incident, str(db_path))

    stored_transactions = get_transactions(str(db_path))
    stats = get_incident_stats(str(db_path))

    assert len(stored_transactions) == 1
    assert stats["total_incidents"] == 1
    assert stats["unresolved_incidents"] == 1
