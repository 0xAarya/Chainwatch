from unittest.mock import patch

from app.services.tronscan_service import fetch_live_transactions


def test_fetch_live_transactions_normalizes_payload():
    sample_payload = {
        "data": [
            {
                "hash": "tx-123",
                "timestamp": 1783228053000,
                "ownerAddress": "TBFqXotFN53bT41UUqaiBBfrAF2NanuARL",
                "toAddress": "TAFkxX8Lvt8bjBbk9Xx5aUCH4ppmxJ1tih",
                "contractRet": "SUCCESS",
                "result": "SUCCESS",
                "amount": "2",
                "contractData": {"amount": 2, "owner_address": "TBFqXotFN53bT41UUqaiBBfrAF2NanuARL", "to_address": "TAFkxX8Lvt8bjBbk9Xx5aUCH4ppmxJ1tih"},
                "revert": False,
            }
        ]
    }

    with patch("app.services.tronscan_service.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'{"data": [{"hash": "tx-123", "timestamp": 1783228053000, "ownerAddress": "TBFqXotFN53bT41UUqaiBBfrAF2NanuARL", "toAddress": "TAFkxX8Lvt8bjBbk9Xx5aUCH4ppmxJ1tih", "contractRet": "SUCCESS", "result": "SUCCESS", "amount": "2", "contractData": {"amount": 2, "owner_address": "TBFqXotFN53bT41UUqaiBBfrAF2NanuARL", "to_address": "TAFkxX8Lvt8bjBbk9Xx5aUCH4ppmxJ1tih"}, "revert": false}]}'

        transactions = fetch_live_transactions(limit=1)

    assert len(transactions) == 1
    assert transactions[0]["transaction_id"] == "tx-123"
    assert transactions[0]["status"] == "SUCCESS"
    assert transactions[0]["amount"] == 2.0
