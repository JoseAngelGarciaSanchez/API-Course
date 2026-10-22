"""No real network call here: httpx2.MockTransport fakes the World Bank API and
the app's get_http_client dependency is overridden ([FA] ch. 12)."""

import asyncio
import json

import httpx2
import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab08_external_api_and_model")

STUDENT = {"id": 7, "last_validate_level": "M1", "last_average_mark": 12, "dedicated_hours": 40}
# Real answers of https://api.worldbank.org/v2/country/fr?format=json and .../country/zz?format=json
FRANCE = [
    {"page": 1, "pages": 1, "per_page": "50", "total": 1},
    [
        {
            "id": "FRA",
            "iso2Code": "FR",
            "name": "France",
            "region": {"id": "ECS", "iso2code": "Z7", "value": "Europe & Central Asia"},
            "incomeLevel": {"id": "HIC", "iso2code": "XD", "value": "High income"},
            "capitalCity": "Paris",
            "longitude": "2.35097",
            "latitude": "48.8566",
        }
    ],
]
UNKNOWN = [{"message": [{"id": "120", "key": "Invalid value", "value": "The provided parameter value is not valid"}]}]


def fake_world_bank(request: httpx2.Request) -> httpx2.Response:
    assert request.url.params.get("format") == "json", "ask the World Bank for JSON: ?format=json"
    code = request.url.path.rsplit("/", 1)[-1].upper()
    if code == "FR":
        return httpx2.Response(200, json=FRANCE)
    if code == "ZZ":
        return httpx2.Response(200, json=UNKNOWN)
    if code == "XX":
        return httpx2.Response(503, text="maintenance")
    if code == "HTM":
        return httpx2.Response(200, text="<html>Moved</html>")
    if code == "TO":
        raise httpx2.ReadTimeout("too slow", request=request)
    return httpx2.Response(500)


def mock_client() -> httpx2.AsyncClient:
    return httpx2.AsyncClient(transport=httpx2.MockTransport(fake_world_bank), base_url=ex.WORLD_BANK_API)


@pytest.fixture
def client():
    async def override():
        async with mock_client() as c:
            yield c

    ex.app.dependency_overrides[ex.get_http_client] = override
    yield TestClient(ex.app)
    ex.app.dependency_overrides.clear()


# --- Part A -------------------------------------------------------------------
def test_predict_mark_formula():
    # 2 + 0.7*12 + 0.05*40 + 0.5 = 12.9
    assert ex.predict_mark(ex.StudentRecord(**STUDENT)) == 12.9


def test_predict_mark_is_clipped():
    top = ex.StudentRecord(**{**STUDENT, "last_average_mark": 20, "dedicated_hours": 500, "last_validate_level": "M2"})
    assert ex.predict_mark(top) == 20.0


def test_predict():
    record = {**STUDENT, "last_average_mark": 8, "dedicated_hours": 0, "last_validate_level": "L3"}
    p = ex.predict(ex.StudentRecord(**record))
    assert p.predicted_mark == 7.6
    assert p.passes is False
    assert p.model_version == ex.MODEL_VERSION


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "model_version": "linear-v1"}


def test_predict_endpoint(client):
    r = client.post("/predict", json=STUDENT)
    assert r.status_code == 200
    assert r.json() == {"id": 7, "predicted_mark": 12.9, "passes": True, "model_version": "linear-v1"}
    assert client.post("/predict", json={**STUDENT, "last_validate_level": "PhD"}).status_code == 422


def test_batch_endpoint(client):
    batch = [STUDENT, {**STUDENT, "id": 8, "last_average_mark": 5, "dedicated_hours": 0}]
    r = client.post("/predict:batch", json=batch)
    assert r.status_code == 200
    preds = r.json()["predictions"]
    assert [p["id"] for p in preds] == [7, 8]
    assert [p["passes"] for p in preds] == [True, False]
    assert client.post("/predict:batch", json=[]).status_code == 422
    assert client.post("/predict:batch", json=[STUDENT] * 101).status_code == 422


def test_stream_endpoint(client):
    batch = [STUDENT, {**STUDENT, "id": 8, "last_average_mark": 5, "dedicated_hours": 0}]
    r = client.post("/predict:stream", json=batch)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/jsonl")
    lines = [json.loads(line) for line in r.text.splitlines()]
    assert [(p["id"], p["passes"]) for p in lines] == [(7, True), (8, False)]
    assert client.post("/predict:stream", json=[{**STUDENT, "id": 0}]).status_code == 422


# --- Part B -------------------------------------------------------------------
def fetch(code: str) -> dict:
    async def go():
        async with mock_client() as c:
            return await ex.fetch_country(code, c)

    return asyncio.run(go())


def test_fetch_country():
    expected = {
        "code": "FR",
        "name": "France",
        "capital": "Paris",
        "region": "Europe & Central Asia",
        "income_level": "High income",
    }
    assert fetch("fr") == expected


@pytest.mark.parametrize(
    "code,exc",
    [("ZZ", "CountryNotFound"), ("XX", "UpstreamError"), ("HTM", "UpstreamError"), ("TO", "UpstreamTimeout")],
)
def test_fetch_country_errors(code, exc):
    with pytest.raises(getattr(ex, exc)):
        fetch(code)


def test_lifespan_shares_one_client():
    with TestClient(ex.app):
        http = ex.app.state.http_client
        assert isinstance(http, httpx2.AsyncClient) and not http.is_closed
        assert str(http.base_url).rstrip("/") == ex.WORLD_BANK_API
    assert http.is_closed, "close the client at shutdown"


def test_country_endpoint(client):
    assert client.get("/countries/FR").json()["capital"] == "Paris"
    assert client.get("/countries/ZZ").status_code == 404
    assert client.get("/countries/XX").status_code == 502
    assert client.get("/countries/HTM").status_code == 502
    assert client.get("/countries/TO").status_code == 504


@pytest.mark.parametrize("code", ["f", "fran", "f%3Fr", "12"])
def test_country_code_is_validated(client, code):
    assert client.get(f"/countries/{code}").status_code == 422
