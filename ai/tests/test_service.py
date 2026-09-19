from fastapi.testclient import TestClient

import sys
from unittest.mock import MagicMock
sys.modules['torch'] = MagicMock()
sys.modules['peft'] = MagicMock()
sys.modules['transformers'] = MagicMock()

from ai import service


def test_health(monkeypatch):
    monkeypatch.setattr(service, "load_model", lambda: (None, None, "cpu"))

    with TestClient(service.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_loaded": True,
        "device": "cpu",
    }


def test_extract(monkeypatch):
    expected = {
        "contact": {"name": "Rahul", "organization": None},
        "event": {
            "type": "quotation",
            "description": "website",
            "amount": 50000,
            "currency": "INR",
            "status": "completed",
        },
        "followup": {
            "required": True,
            "action": "call",
            "date_expression": "Friday",
        },
    }
    monkeypatch.setattr(service, "load_model", lambda: (None, None, "cpu"))
    monkeypatch.setattr(service, "extract_followup", lambda text: expected)

    with TestClient(service.app) as client:
        response = client.post(
            "/extract",
            json={"text": "Rahul ko quotation bhej diya, Friday ko call karna hai."},
        )

    assert response.status_code == 200
    assert response.json() == expected


def test_extract_rejects_empty_text(monkeypatch):
    monkeypatch.setattr(service, "load_model", lambda: (None, None, "cpu"))

    with TestClient(service.app) as client:
        response = client.post("/extract", json={"text": ""})

    assert response.status_code == 422


def test_extract_rejects_missing_text(monkeypatch):
    monkeypatch.setattr(service, "load_model", lambda: (None, None, "cpu"))

    with TestClient(service.app) as client:
        response = client.post("/extract", json={})

    assert response.status_code == 422
