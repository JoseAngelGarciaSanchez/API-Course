"""Tests per layer, as in [FA] ch. 12: unit tests for data and service,
then the web layer with a dependency override (fresh DB for each test)."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from lab._loader import load

data = load("lab04_layers_and_dependencies", "data")
service = load("lab04_layers_and_dependencies", "service")
web = load("lab04_layers_and_dependencies", "web")
errors = load("lab04_layers_and_dependencies", "errors")
Creature = load("lab04_layers_and_dependencies", "model").Creature

YETI = {
    "name": "yeti",
    "country": "CN",
    "area": "Himalayas",
    "description": "Hirsute Himalayan",
    "aka": "Abominable Snowman",
}
BIGFOOT = {"name": "sasquatch", "country": "US", "area": "*", "description": "Yeti's Cousin Eddie", "aka": "Bigfoot"}


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:", check_same_thread=False)
    data.init(c)
    yield c
    c.close()


@pytest.fixture
def client(conn):
    web.app.dependency_overrides[web.get_db] = lambda: conn
    yield TestClient(web.app)
    web.app.dependency_overrides.clear()


# --- data layer ---------------------------------------------------------------
def test_data_create_get(conn):
    data.create(conn, Creature(**YETI))
    assert data.get_one(conn, "yeti").aka == "Abominable Snowman"


def test_data_duplicate(conn):
    data.create(conn, Creature(**YETI))
    with pytest.raises(errors.Duplicate):
        data.create(conn, Creature(**YETI))


def test_data_get_all_paging(conn):
    for n in ["c-one", "a-one", "b-one"]:
        data.create(conn, Creature(**{**YETI, "name": n}))
    assert [c.name for c in data.get_all(conn)] == ["a-one", "b-one", "c-one"]
    assert [c.name for c in data.get_all(conn, skip=1, limit=1)] == ["b-one"]


def test_data_modify_delete(conn):
    data.create(conn, Creature(**YETI))
    data.modify(conn, "yeti", Creature(**{**YETI, "area": "Tibet"}))
    assert data.get_one(conn, "yeti").area == "Tibet"
    data.delete(conn, "yeti")
    with pytest.raises(errors.Missing):
        data.get_one(conn, "yeti")
    with pytest.raises(errors.Missing):
        data.delete(conn, "yeti")
    with pytest.raises(errors.Missing):
        data.modify(conn, "yeti", Creature(**YETI))


def test_data_count_by_country(conn):
    for name, country in [("yeti", "CN"), ("bigfoot", "US"), ("mothman", "US")]:
        data.create(conn, Creature(**{**YETI, "name": name, "country": country}))
    assert data.count_by_country(conn) == {"CN": 1, "US": 2}
    assert list(data.count_by_country(conn)) == ["CN", "US"], "ORDER BY country"


def test_data_sql_injection(conn):
    evil = "x'); DROP TABLE creature; --"
    data.create(conn, Creature(**{**YETI, "name": evil}))
    assert data.get_one(conn, evil).name == evil
    assert conn.execute("SELECT count(*) FROM creature").fetchone()[0] == 1


# --- service layer ------------------------------------------------------------
def test_service_normalises(conn):
    created = service.create(conn, Creature(**{**YETI, "name": "  Yeti ", "country": "cn"}))
    assert (created.name, created.country) == ("yeti", "CN")
    assert service.get_one(conn, "YETI").name == "yeti"


def test_service_replace_delete_stats(conn):
    service.create(conn, Creature(**YETI))
    service.create(conn, Creature(**BIGFOOT))
    service.create(conn, Creature(**{**BIGFOOT, "name": "mothman"}))
    assert service.count_by_country(conn) == {"CN": 1, "US": 2}
    service.replace(conn, "Yeti", Creature(**{**YETI, "area": "Nepal"}))
    assert service.get_one(conn, "yeti").area == "Nepal"
    service.delete(conn, "MOTHMAN")
    assert len(service.get_all(conn)) == 2


# --- web layer ----------------------------------------------------------------
def test_web_crud(client):
    assert client.post("/creature", json=YETI).status_code == 201
    dup = client.post("/creature", json=YETI)
    assert dup.status_code == 409
    assert dup.json() == {"detail": "Creature yeti already exists"}
    assert client.get("/creature/Yeti").json()["name"] == "yeti"
    missing = client.get("/creature/nessie")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Creature nessie not found"}
    r = client.put("/creature/yeti", json={**YETI, "area": "Bhutan"})
    assert r.status_code == 200 and r.json()["area"] == "Bhutan"
    assert client.put("/creature/nessie", json=YETI).status_code == 404
    gone = client.delete("/creature/yeti")
    assert gone.status_code == 204
    assert gone.content == b""
    assert client.delete("/creature/yeti").status_code == 404


def test_web_paging(client):
    for i in range(15):
        client.post("/creature", json={**YETI, "name": f"yeti{i:02d}"})
    assert len(client.get("/creature").json()) == 10
    page = client.get("/creature", params={"skip": 10, "limit": 3}).json()
    assert [c["name"] for c in page] == ["yeti10", "yeti11", "yeti12"]
    assert client.get("/creature", params={"limit": 1000}).status_code == 422
    assert client.get("/creature", params={"skip": -1}).status_code == 422


def test_web_stats(client):
    client.post("/creature", json=YETI)
    client.post("/creature", json=BIGFOOT)
    assert client.get("/creature/stats/by-country").json() == {"CN": 1, "US": 1}


def test_dependency_override_isolates_db(client):
    # the module-level connection must not have been touched by the other tests
    assert web._conn.execute("SELECT count(*) FROM creature").fetchone()[0] == 0
