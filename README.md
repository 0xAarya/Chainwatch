# ChainWatch

ChainWatch is a beginner-friendly Python project that simulates a simple blockchain transaction system and automatically detects operational incidents. It is designed for an Application Support Engineer portfolio and focuses on Python programming, logging, SQLite, monitoring, debugging, and incident management.

## Problem Statement

Modern applications and services must detect failures quickly. A simple transaction system can be monitored for suspicious behavior, failed operations, duplicate records, and delayed processing. This project demonstrates how a support engineer might build a lightweight monitoring workflow with logs, incident tracking, and a basic dashboard.

## Project Objectives

- Simulate blockchain-style transactions without using real cryptocurrency or external APIs.
- Detect incidents such as failed transactions, pending delays, duplicate IDs, invalid amounts, and suspiciously high amounts.
- Store data in SQLite for easy troubleshooting and reporting.
- Provide a simple Streamlit dashboard for monitoring.
- Create logs that are useful during incident investigations.

## Features

- Transaction and block data models
- Incident generation with automatic severity assignment
- SQLite storage for transactions, blocks, and incidents
- Logging for application events, errors, and incidents
- Basic incident search and filtering
- Streamlit dashboard for operational visibility
- Sample data generation for local demos
- Pytest-based unit tests

## Architecture

```text
+-------------------+       +-------------------+       +-------------------+
| Transaction Model | ----> | TransactionMonitor| ----> | Incident Manager  |
+-------------------+       +-------------------+       +-------------------+
          |                            |                           |
          v                            v                           v
+-------------------+       +-------------------+       +-------------------+
| SQLite Database  | <---- | Python Logging    | <---- | Streamlit Dashboard|
+-------------------+       +-------------------+       +-------------------+
```

## Technology Stack

- Python 3
- SQLite
- Streamlit
- pytest
- Built-in logging

## Project Structure

```text
chainwatch/
├── app.py
├── blockchain.py
├── transaction.py
├── monitor.py
├── incident_manager.py
├── database.py
├── config.py
├── sample_data.py
├── requirements.txt
├── README.md
├── data/
├── logs/
└── tests/
```

## Installation

1. Clone or open the project folder.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

### Initialize the database and generate sample data

```bash
python sample_data.py
```

### Start the dashboard

```bash
streamlit run app.py
```

## How to Run Tests

```bash
pytest -q
```

## Database Explanation

The project uses SQLite to store three tables:

- transactions: stores all simulated payments
- blocks: stores lightweight block summaries
- incidents: stores detected operational issues

These records can be inspected directly with SQLite tools or through the dashboard.

## Monitoring and Incident Detection

The monitor inspects transactions for:

- failed transactions
- pending transactions that stay unresolved for too long
- duplicate transaction IDs
- unusually large amounts
- invalid zero or negative amounts
- application errors

Each issue is turned into an incident and assigned a severity.

## Sample Troubleshooting Scenario

A support engineer might see a high-severity incident for an invalid or duplicate transaction. They can review the logs in the logs folder, inspect the incident records in SQLite, and verify whether a transaction was malformed or duplicated during processing.

## Limitations

- This is a simplified simulator, not a real blockchain implementation.
- The monitoring logic is intentionally basic and beginner-friendly.
- No real wallet, external network, or production-grade alerting is included.

## Future Improvements

- Add a web API for incident submission
- Add alerting via email or Slack
- Improve dashboard charts and filters
- Add more realistic block validation rules
- Support incident resolution workflows
