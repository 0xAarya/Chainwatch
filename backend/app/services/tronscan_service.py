import json
from datetime import datetime, timezone
from typing import Any
from urllib.request import urlopen

TRONSCAN_API_URL = "https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&limit=10"


def fetch_live_transactions(limit: int = 10) -> list[dict[str, Any]]:
    try:
        with urlopen(TRONSCAN_API_URL, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    data = payload.get("data") or []
    normalized: list[dict[str, Any]] = []
    for item in data[:limit]:
        amount = item.get("amount")
        if isinstance(amount, str):
            try:
                amount_value = float(amount)
            except ValueError:
                amount_value = 0.0
        elif isinstance(amount, (int, float)):
            amount_value = float(amount)
        else:
            amount_value = 0.0

        contract_data = item.get("contractData") or {}
        if not isinstance(contract_data, dict):
            contract_data = {}

        owner_address = item.get("ownerAddress") or contract_data.get("owner_address") or "unknown"
        to_address = item.get("toAddress") or contract_data.get("to_address") or "unknown"
        timestamp_ms = item.get("timestamp")
        if isinstance(timestamp_ms, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat()
        else:
            timestamp = datetime.now(timezone.utc).isoformat()

        normalized.append(
            {
                "transaction_id": item.get("hash") or item.get("id") or "unknown",
                "sender": owner_address,
                "receiver": to_address,
                "amount": amount_value,
                "timestamp": timestamp,
                "status": (item.get("contractRet") or item.get("result") or "PENDING").upper(),
                "block_id": str(item.get("block") or ""),
            }
        )

    return normalized
