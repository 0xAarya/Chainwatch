from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_transactions_endpoint():
    response = client.get('/transactions')
    assert response.status_code == 200


def test_incidents_endpoint():
    response = client.get('/incidents')
    assert response.status_code == 200


def test_analytics_endpoint():
    response = client.get('/analytics')
    assert response.status_code == 200
