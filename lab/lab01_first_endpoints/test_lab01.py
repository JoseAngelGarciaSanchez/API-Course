import json

import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab01_first_endpoints")


@pytest.fixture
def client():
    snapshot = list(ex.ANNUAIRE)
    yield TestClient(ex.app)
    ex.ANNUAIRE[:] = snapshot


def test_title(client):
    assert client.get("/openapi.json").json()["info"]["title"] == "Student Directory"


def test_hi(client):
    r = client.get("/hi")
    assert r.status_code == 200
    assert r.json() == "hi"


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_all(client):
    assert len(client.get("/annuaire").json()["annuaire"]) == 4


def test_query_param(client):
    names = [s["name"] for s in client.get("/annuaire", params={"domain": "health"}).json()["annuaire"]]
    assert names == ["Lea", "Ines"]


def test_path_param(client):
    names = [s["name"] for s in client.get("/annuaire/2025").json()["annuaire"]]
    assert names == ["Ines", "Hugo"]


def test_path_param_not_found(client):
    assert client.get("/annuaire/1999").status_code == 404


def test_path_param_wrong_type(client):
    assert client.get("/annuaire/abc").status_code == 422


def test_header(client):
    assert client.get("/whoami", headers={"X-Client-Name": "pytest"}).json() == {"client": "pytest"}
    assert client.get("/whoami").json() == {"client": "anonymous"}


def test_body_created(client):
    new = {"name": "Zoe", "year": 2026, "domain": "climate"}
    r = client.post("/annuaire", json=new)
    assert r.status_code == 201
    assert r.json() == new
    assert client.get("/annuaire/2026").json()["annuaire"] == [new]


def test_body_invalid(client):
    r = client.post("/annuaire", json={"name": "Zoe"})
    assert r.status_code == 422
    assert {e["loc"][-1] for e in r.json()["detail"]} == {"year", "domain"}


def test_body_requires_json_content_type(client):
    body = json.dumps({"name": "Zoe", "year": 2026, "domain": "climate"})
    assert client.post("/annuaire", content=body).status_code == 422
    assert client.post("/annuaire", content=body, headers={"Content-Type": "application/json"}).status_code == 201


def test_openapi_lists_paths(client):
    paths = client.get("/openapi.json").json()["paths"]
    for p in ["/hi", "/health", "/annuaire", "/annuaire/{year}", "/whoami"]:
        assert p in paths
