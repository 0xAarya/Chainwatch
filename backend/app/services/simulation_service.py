import random
import uuid
from datetime import datetime, timezone
from typing import List

from app.database.base import SessionLocal
from app.models.block import BlockModel
from app.models.incident import IncidentModel
from app.models.transaction import TransactionModel
from app.services.monitoring_service import MonitoringService


class SimulationService:
    def __init__(self) -> None:
        self.monitoring_service = MonitoringService()

    def generate_transaction(self) -> TransactionModel:
        status = random.choice(["SUCCESS", "FAILED", "PENDING"])
        amount = random.choice([120.0, 240.0, 1800.0, 15.0, -5.0, 0.0, 45.0])
        transaction = TransactionModel(
            transaction_id=f"tx-{uuid.uuid4().hex[:8]}",
            sender=random.choice(["alice", "bob", "carol", "dave"]),
            receiver=random.choice(["erin", "frank", "grace", "heidi"]),
            amount=amount,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            error_message="Simulated processing issue" if status == "FAILED" else None,
            block_id=None,
        )
        with SessionLocal() as session:
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
        self.monitoring_service.inspect_transaction(transaction)
        self.monitoring_service.log_event("INFO", "Simulation", f"Generated transaction {transaction.transaction_id}")
        return transaction

    def generate_block(self) -> BlockModel:
        with SessionLocal() as session:
            transaction_count = session.query(TransactionModel).count()
            index = session.query(BlockModel).count() + 1
            block = BlockModel(
                block_id=f"block-{uuid.uuid4().hex[:8]}",
                index=index,
                timestamp=datetime.now(timezone.utc).isoformat(),
                previous_hash=f"prev-{index-1}",
                current_hash=f"hash-{uuid.uuid4().hex[:8]}",
                transaction_count=transaction_count,
                summary="Simulated block",
            )
            session.add(block)
            session.commit()
            session.refresh(block)
            return block
