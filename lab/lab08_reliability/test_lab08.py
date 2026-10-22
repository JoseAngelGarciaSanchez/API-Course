import random
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import httpx2
import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab08_reliability")

PAY = {"amount": 100, "currency": "EUR", "to": "Lea"}


@pytest.fixture
def client():
    ex.PAYMENTS.clear()
    ex.REQUEST_CACHE.clear()
    return TestClient(ex.app)


# --- Part A -------------------------------------------------------------------
def test_fingerprint_ignores_key_order():
    assert ex.fingerprint({"a": 1, "b": 2}) == ex.fingerprint({"b": 2, "a": 1})
    assert ex.fingerprint({"a": 1}) != ex.fingerprint({"a": 2})
    assert len(ex.fingerprint({})) == 64


def test_create_without_request_id(client):
    r1 = client.post("/payments", json=PAY)
    r2 = client.post("/payments", json=PAY)
    assert r1.status_code == r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"], "no request_id -> no deduplication"


def test_retry_with_same_request_id_is_deduplicated(client):
    body = {**PAY, "request_id": "a1b2c3"}
    r1 = client.post("/payments", json=body)
    r2 = client.post("/payments", json=body)
    assert r1.status_code == 201
    assert r2.json() == r1.json()
    assert len(client.get("/payments").json()["results"]) == 1, "the money must leave only once!"


def test_request_id_reused_with_other_body(client):
    client.post("/payments", json={**PAY, "request_id": "a1b2c3"})
    r = client.post("/payments", json={**PAY, "amount": 999, "request_id": "a1b2c3"})
    assert r.status_code == 409


def test_validate_only(client):
    r = client.post("/payments", params={"validate_only": True}, json=PAY)
    assert r.status_code == 200
    assert r.json()["id"] is None
    assert client.get("/payments").json()["results"] == []
    bad = client.post("/payments", params={"validate_only": True}, json={**PAY, "amount": 5000})
    assert bad.status_code == 400


def test_business_rule(client):
    assert client.post("/payments", json={**PAY, "amount": 900}).status_code == 201
    assert client.post("/payments", json={**PAY, "amount": 200}).status_code == 400
    assert client.post("/payments", json={**PAY, "currency": "BTC"}).status_code == 422


# --- Part B -------------------------------------------------------------------
def test_backoff_delays():
    assert ex.backoff_delays(5, base=0.1, cap=10) == pytest.approx([0.1, 0.2, 0.4, 0.8])
    assert ex.backoff_delays(6, base=1, cap=5) == [1, 2, 4, 5, 5]
    assert ex.backoff_delays(1) == []
    jittered = ex.backoff_delays(5, base=1, cap=100, rng=random.Random(42))
    assert all(0 <= d <= m for d, m in zip(jittered, [1, 2, 4, 8], strict=True))
    assert jittered != [1, 2, 4, 8]


def test_parse_retry_after():
    assert ex.parse_retry_after(None) is None
    assert ex.parse_retry_after("120") == 120
    now = datetime(2026, 10, 21, 12, 0, tzinfo=UTC)
    assert ex.parse_retry_after(format_datetime(now + timedelta(seconds=30), usegmt=True), now=now) == 30
    assert ex.parse_retry_after("soon") is None


def scripted(*outcomes):
    """A fake `send` that returns/raises the outcomes in order."""
    calls = []

    def send():
        outcome = outcomes[len(calls)]
        calls.append(outcome)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    return send, calls


def test_retry_until_success():
    send, calls = scripted(httpx2.Response(503), httpx2.Response(503), httpx2.Response(200))
    slept = []
    r = ex.call_with_retry(send, max_attempts=4, base=0.1, sleep=slept.append)
    assert r.status_code == 200
    assert len(calls) == 3
    assert slept == pytest.approx([0.1, 0.2])


def test_no_retry_on_client_error():
    send, calls = scripted(httpx2.Response(400), httpx2.Response(200))
    r = ex.call_with_retry(send, sleep=lambda s: None)
    assert r.status_code == 400 and len(calls) == 1


def test_gives_up_after_max_attempts():
    send, calls = scripted(*[httpx2.Response(503)] * 3)
    r = ex.call_with_retry(send, max_attempts=3, sleep=lambda s: None)
    assert r.status_code == 503 and len(calls) == 3


def test_honours_retry_after():
    send, _ = scripted(httpx2.Response(429, headers={"Retry-After": "2"}), httpx2.Response(200))
    slept = []
    ex.call_with_retry(send, base=0.1, cap=5, sleep=slept.append)
    assert slept == [2]


def test_retries_network_errors():
    req = httpx2.Request("GET", "https://example.org")
    send, calls = scripted(httpx2.ConnectError("down", request=req), httpx2.Response(200))
    assert ex.call_with_retry(send, sleep=lambda s: None).status_code == 200
    assert len(calls) == 2
    send, _ = scripted(*[httpx2.ConnectError("down", request=req)] * 2)
    with pytest.raises(httpx2.ConnectError):
        ex.call_with_retry(send, max_attempts=2, sleep=lambda s: None)
