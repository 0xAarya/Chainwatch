from app.database.base import Base, engine
from app.models.block import BlockModel
from app.models.incident import IncidentModel
from app.models.log_entry import ApplicationLogModel
from app.models.system_health import SystemHealthModel
from app.models.transaction import TransactionModel


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
