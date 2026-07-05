import random
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import SessionLocal
from app.database.init_db import init_db
from app.models.block import BlockModel
from app.models.incident import IncidentModel
from app.models.log_entry import ApplicationLogModel
from app.models.system_health import SystemHealthModel
from app.models.transaction import TransactionModel
from app.schemas.incident import IncidentRead
from app.schemas.log_entry import LogEntryRead
from app.schemas.system_health import SystemHealthRead
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.monitoring_service import MonitoringService
from app.services.simulation_service import SimulationService
from app.services.tronscan_service import fetch_live_transactions

app = FastAPI(title="ChainWatch API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
monitoring_service = MonitoringService()
monitoring_service.seed_health()
simulation_service = SimulationService()


def seed_demo_data() -> None:
    with SessionLocal() as session:
        if session.query(TransactionModel).first() is None:
            sample_transactions = [
                TransactionModel(
                    transaction_id="tx-trx-1001",
                    sender="alice",
                    receiver="bob",
                    amount=125.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="SUCCESS",
                    block_id="block-001",
                ),
                TransactionModel(
                    transaction_id="tx-trx-1002",
                    sender="carol",
                    receiver="dave",
                    amount=1800.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="SUCCESS",
                    block_id="block-001",
                ),
                TransactionModel(
                    transaction_id="tx-trx-1003",
                    sender="erin",
                    receiver="frank",
                    amount=54.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="FAILED",
                    block_id="block-001",
                    error_message="Simulated execution issue",
                ),
                TransactionModel(
                    transaction_id="tx-trx-1004",
                    sender="grace",
                    receiver="heidi",
                    amount=0.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="PENDING",
                    block_id="block-001",
                ),
            ]
            session.add_all(sample_transactions)
            session.add(BlockModel(
                block_id="block-001",
                index=1,
                timestamp=datetime.now(timezone.utc).isoformat(),
                previous_hash="0" * 64,
                current_hash="a1b2c3",
                transaction_count=4,
                summary="Genesis block",
            ))
            session.add(IncidentModel(
                incident_id="incident-demo-001",
                incident_type="FAILED_TRANSACTION",
                transaction_id="tx-trx-1003",
                description="A transaction failed during processing",
                severity="HIGH",
                timestamp=datetime.now(timezone.utc).isoformat(),
                resolution_status="OPEN",
                probable_cause="Simulated downstream processing error",
                affected_component="Transaction Processor",
                recommended_action="Inspect processor logs and retry",
            ))
            session.add(ApplicationLogModel(
                level="INFO",
                component="Monitoring Engine",
                message="TRON simulation seeded successfully",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ))
            session.commit()


seed_demo_data()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "chain": "TRON"}


@app.get("/transactions", response_model=list[TransactionRead])
def list_transactions() -> list[TransactionModel]:
    live_transactions = fetch_live_transactions(limit=8)
    if live_transactions:
        with SessionLocal() as session:
            session.query(TransactionModel).delete()
            for tx in live_transactions:
                session.add(TransactionModel(**tx))
            session.commit()
        return [TransactionModel(**tx) for tx in live_transactions]

    with SessionLocal() as session:
        return session.query(TransactionModel).order_by(TransactionModel.timestamp.desc()).all()


@app.post("/transactions", response_model=TransactionRead, status_code=201)
def create_transaction(payload: TransactionCreate) -> TransactionModel:
    with SessionLocal() as session:
        transaction = TransactionModel(**payload.model_dump())
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        monitoring_service.inspect_transaction(transaction)
        monitoring_service.log_event("INFO", "API", f"Created transaction {transaction.transaction_id}")
        return transaction


@app.get("/blocks", response_model=list[dict])
def list_blocks() -> list[dict]:
    with SessionLocal() as session:
        blocks = session.query(BlockModel).order_by(BlockModel.index.desc()).all()
        return [
            {
                "block_id": block.block_id,
                "index": block.index,
                "timestamp": block.timestamp,
                "transaction_count": block.transaction_count,
                "previous_hash": block.previous_hash,
                "current_hash": block.current_hash,
                "summary": block.summary,
            }
            for block in blocks
        ]


@app.get("/incidents", response_model=list[IncidentRead])
def list_incidents() -> list[IncidentModel]:
    with SessionLocal() as session:
        return session.query(IncidentModel).order_by(IncidentModel.timestamp.desc()).all()


@app.post("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str) -> dict:
    with SessionLocal() as session:
        incident = session.get(IncidentModel, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        incident.resolution_status = "RESOLVED"
        session.commit()
        return {"status": "resolved", "incident_id": incident_id}


@app.get("/logs", response_model=list[LogEntryRead])
def list_logs() -> list[ApplicationLogModel]:
    with SessionLocal() as session:
        return session.query(ApplicationLogModel).order_by(ApplicationLogModel.id.desc()).all()


@app.get("/system-health", response_model=list[SystemHealthRead])
def list_system_health() -> list[SystemHealthModel]:
    with SessionLocal() as session:
        return session.query(SystemHealthModel).all()


@app.get("/analytics")
def analytics() -> dict:
    live_transactions = fetch_live_transactions(limit=10)
    transactions = live_transactions if live_transactions else []
    with SessionLocal() as session:
        incidents = session.query(IncidentModel).all()
        if not live_transactions:
            transactions = [
                {
                    "status": tx.status,
                }
                for tx in session.query(TransactionModel).all()
            ]
        return {
            "total_transactions": len(transactions),
            "success_rate": round(sum(1 for tx in transactions if tx.get("status") == "SUCCESS") / len(transactions) * 100 if transactions else 0, 2),
            "failure_rate": round(sum(1 for tx in transactions if tx.get("status") == "FAILED") / len(transactions) * 100 if transactions else 0, 2),
            "total_incidents": len(incidents),
            "critical_incidents": sum(1 for incident in incidents if incident.severity == "CRITICAL"),
            "severity_breakdown": {
                severity: sum(1 for incident in incidents if incident.severity == severity)
                for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            },
        }


@app.post("/simulation/start")
def start_simulation() -> dict:
    simulation_service.generate_transaction()
    simulation_service.generate_block()
    return {"status": "started", "chain": "TRON"}


@app.post("/simulation/incident")
def trigger_incident() -> dict:
    with SessionLocal() as session:
        tx = session.query(TransactionModel).order_by(TransactionModel.timestamp.desc()).first()
        if tx is None:
            return {"status": "no_transactions"}
        incident = IncidentModel(
            incident_id=f"incident-random-{random.randint(1000, 9999)}",
            incident_type="APPLICATION_ERROR",
            transaction_id=tx.transaction_id,
            description="Simulated latency spike on the TRON validator node",
            severity="HIGH",
            timestamp=datetime.now(timezone.utc).isoformat(),
            resolution_status="OPEN",
            probable_cause="Transient service congestion",
            affected_component="API Server",
            recommended_action="Inspect request queue and retry policy",
        )
        session.add(incident)
        session.commit()
        monitoring_service.log_event("ERROR", "Incident Service", "Injected a random TRON incident")
        return {"status": "incident_created", "incident_id": incident.incident_id}


@app.post("/simulation/reset")
def reset_simulation() -> dict:
    with SessionLocal() as session:
        session.query(TransactionModel).delete()
        session.query(BlockModel).delete()
        session.query(IncidentModel).delete()
        session.query(ApplicationLogModel).delete()
        session.query(SystemHealthModel).delete()
        session.commit()
    monitoring_service.seed_health()
    seed_demo_data()
    return {"status": "reset", "chain": "TRON"}
