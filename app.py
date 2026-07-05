import logging
from pathlib import Path

import streamlit as st

from config import DB_PATH, LOG_DIR
from database import (
    filter_incidents_by_severity,
    filter_incidents_by_status,
    get_blocks,
    get_incident_stats,
    get_incidents,
    get_transactions,
    init_db,
    search_incidents,
)
from sample_data import generate_sample_data


LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "chainwatch.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("chainwatch.app")


def initialize_app() -> None:
    init_db(DB_PATH)
    if not get_transactions(DB_PATH):
        generate_sample_data(DB_PATH)


def render_dashboard() -> None:
    st.set_page_config(page_title="ChainWatch Dashboard", page_icon="🔗", layout="wide")
    st.title("ChainWatch: Blockchain Transaction Monitoring")
    st.caption("A beginner-friendly incident detection system for application support engineering")

    initialize_app()

    stats = get_incident_stats(DB_PATH)
    transactions = get_transactions(DB_PATH)
    incidents = get_incidents(DB_PATH)
    blocks = get_blocks(DB_PATH)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total transactions", len(transactions))
    col2.metric("Successful", sum(1 for tx in transactions if tx.status == "SUCCESS"))
    col3.metric("Failed", sum(1 for tx in transactions if tx.status == "FAILED"))
    col4.metric("Pending", sum(1 for tx in transactions if tx.status == "PENDING"))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total incidents", stats["total_incidents"])
    col6.metric("Unresolved", stats["unresolved_incidents"])
    col7.metric("Critical", stats["severity_counts"].get("CRITICAL", 0))
    col8.metric("High", stats["severity_counts"].get("HIGH", 0))

    st.subheader("Incident Filters")
    search_query = st.text_input("Search incidents")
    severity_filter = st.selectbox("Filter by severity", ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    status_filter = st.selectbox("Filter by status", ["ALL", "OPEN", "RESOLVED"])

    if search_query:
        incidents = search_incidents(search_query, DB_PATH)
    elif severity_filter != "ALL":
        incidents = filter_incidents_by_severity(severity_filter, DB_PATH)
    elif status_filter != "ALL":
        incidents = filter_incidents_by_status(status_filter, DB_PATH)

    st.subheader("Recent Incidents")
    st.dataframe(
        [
            {
                "Incident ID": incident.incident_id,
                "Type": incident.incident_type,
                "Transaction": incident.transaction_id,
                "Severity": incident.severity,
                "Status": incident.resolution_status,
                "Description": incident.description,
                "Timestamp": incident.timestamp,
            }
            for incident in incidents[:10]
        ]
    )

    st.subheader("Blockchain Blocks")
    st.dataframe([block for block in blocks])

    st.subheader("Transaction Summary")
    st.dataframe(
        [
            {
                "ID": transaction.transaction_id,
                "Sender": transaction.sender,
                "Receiver": transaction.receiver,
                "Amount": transaction.amount,
                "Status": transaction.status,
                "Timestamp": transaction.timestamp,
            }
            for transaction in transactions
        ]
    )


if __name__ == "__main__":
    render_dashboard()
