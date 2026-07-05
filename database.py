import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from config import DB_PATH
from incident_manager import Incident, create_incident
from transaction import Transaction


def ensure_data_dir(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    target_path = Path(db_path) if db_path else DB_PATH
    ensure_data_dir(target_path)
    connection = sqlite3.connect(target_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str | Path | None = None) -> None:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS blocks (
            block_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            transaction_count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            incident_type TEXT NOT NULL,
            transaction_id TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            resolution_status TEXT NOT NULL
        );
        """
    )
    connection.commit()
    connection.close()


def insert_transaction(transaction: Transaction, db_path: str | Path | None = None) -> None:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO transactions (
            transaction_id, sender, receiver, amount, timestamp, status, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction.transaction_id,
            transaction.sender,
            transaction.receiver,
            transaction.amount,
            transaction.timestamp,
            transaction.status,
            transaction.error_message,
        ),
    )
    connection.commit()
    connection.close()


def insert_block(block_id: str, transaction_count: int, db_path: str | Path | None = None) -> None:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO blocks (block_id, timestamp, transaction_count) VALUES (?, ?, ?)",
        (block_id, datetime.now(timezone.utc).isoformat(), transaction_count),
    )
    connection.commit()
    connection.close()


def insert_incident(incident: Incident, db_path: str | Path | None = None) -> None:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO incidents (
            incident_id, incident_type, transaction_id, description, severity, timestamp, resolution_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident.incident_id,
            incident.incident_type,
            incident.transaction_id,
            incident.description,
            incident.severity,
            incident.timestamp,
            incident.resolution_status,
        ),
    )
    connection.commit()
    connection.close()


def get_transactions(db_path: str | Path | None = None) -> List[Transaction]:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM transactions ORDER BY timestamp").fetchall()
    connection.close()
    return [Transaction.from_dict(dict(row)) for row in rows]


def get_blocks(db_path: str | Path | None = None) -> List[dict]:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM blocks ORDER BY timestamp").fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_incidents(db_path: str | Path | None = None) -> List[Incident]:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC").fetchall()
    connection.close()
    return [
        Incident(
            incident_id=row["incident_id"],
            incident_type=row["incident_type"],
            transaction_id=row["transaction_id"],
            description=row["description"],
            severity=row["severity"],
            timestamp=row["timestamp"],
            resolution_status=row["resolution_status"],
        )
        for row in rows
    ]


def search_incidents(query: str, db_path: str | Path | None = None) -> List[Incident]:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    rows = cursor.execute(
        "SELECT * FROM incidents WHERE incident_type LIKE ? OR description LIKE ? ORDER BY timestamp DESC",
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    connection.close()
    return [
        Incident(
            incident_id=row["incident_id"],
            incident_type=row["incident_type"],
            transaction_id=row["transaction_id"],
            description=row["description"],
            severity=row["severity"],
            timestamp=row["timestamp"],
            resolution_status=row["resolution_status"],
        )
        for row in rows
    ]


def filter_incidents_by_severity(severity: str, db_path: str | Path | None = None) -> List[Incident]:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    rows = cursor.execute(
        "SELECT * FROM incidents WHERE severity = ? ORDER BY timestamp DESC",
        (severity,),
    ).fetchall()
    connection.close()
    return [
        Incident(
            incident_id=row["incident_id"],
            incident_type=row["incident_type"],
            transaction_id=row["transaction_id"],
            description=row["description"],
            severity=row["severity"],
            timestamp=row["timestamp"],
            resolution_status=row["resolution_status"],
        )
        for row in rows
    ]


def filter_incidents_by_status(status: str, db_path: str | Path | None = None) -> List[Incident]:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    rows = cursor.execute(
        "SELECT * FROM incidents WHERE resolution_status = ? ORDER BY timestamp DESC",
        (status,),
    ).fetchall()
    connection.close()
    return [
        Incident(
            incident_id=row["incident_id"],
            incident_type=row["incident_type"],
            transaction_id=row["transaction_id"],
            description=row["description"],
            severity=row["severity"],
            timestamp=row["timestamp"],
            resolution_status=row["resolution_status"],
        )
        for row in rows
    ]


def update_incident_resolution(incident_id: str, resolution_status: str, db_path: str | Path | None = None) -> None:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE incidents SET resolution_status = ? WHERE incident_id = ?",
        (resolution_status, incident_id),
    )
    connection.commit()
    connection.close()


def get_incident_stats(db_path: str | Path | None = None) -> dict:
    connection = get_connection(db_path)
    cursor = connection.cursor()
    total_incidents = cursor.execute("SELECT COUNT(*) AS count FROM incidents").fetchone()["count"]
    unresolved_incidents = cursor.execute(
        "SELECT COUNT(*) AS count FROM incidents WHERE resolution_status = 'OPEN'"
    ).fetchone()["count"]
    severity_rows = cursor.execute(
        "SELECT severity, COUNT(*) AS count FROM incidents GROUP BY severity"
    ).fetchall()
    connection.close()

    severity_counts = {row["severity"]: row["count"] for row in severity_rows}
    return {
        "total_incidents": total_incidents,
        "unresolved_incidents": unresolved_incidents,
        "severity_counts": severity_counts,
    }
