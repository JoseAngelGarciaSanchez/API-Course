import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab03_resource_oriented")

BOOKING = {"passenger": "Lea", "flight_number": "AF1234", "date": "2026-12-24"}


@pytest.fixture
def client():
    ex.RESERVATIONS.clear()
    return TestClient(ex.app)


# --- Part A -----------------------------------------------------------------
@pytest.mark.parametrize(
    "method,expected",
    [
        ("create", "CreateFlightReservation"),
        ("get", "GetFlightReservation"),
        ("LIST", "ListFlightReservations"),
        ("update", "UpdateFlightReservation"),
        ("delete", "DeleteFlightReservation"),
    ],
)
def test_standard_method_name(method, expected):
    assert ex.standard_method_name(method, "FlightReservation") == expected


def test_standard_method_name_plural_y():
    assert ex.standard_method_name("list", "Category") == "ListCategories"


def test_standard_method_name_unknown():
    with pytest.raises(ValueError):
        ex.standard_method_name("ShowAll", "FlightReservation")


def test_http_route():
    c = "flightReservations"
    assert ex.http_route("create", c) == ("POST", "/flightReservations")
    assert ex.http_route("get", c) == ("GET", "/flightReservations/{id}")
    assert ex.http_route("list", c) == ("GET", "/flightReservations")
    assert ex.http_route("update", c) == ("PATCH", "/flightReservations/{id}")
    assert ex.http_route("delete", c) == ("DELETE", "/flightReservations/{id}")
    with pytest.raises(ValueError):
        ex.http_route("upgrade", c)


def test_rpc_mapping():
    assert ex.RPC_TO_STANDARD == {
        "ScheduleFlight": "CreateFlightReservation",
        "GetFlightDetails": "GetFlightReservation",
        "ShowAllBookings": "ListFlightReservations",
        "CancelReservation": "DeleteFlightReservation",
        "RescheduleFlight": "UpdateFlightReservation",
        "UpgradeTrip": "UpdateFlightReservation",
    }


# --- Part B -----------------------------------------------------------------
def test_new_id():
    ids = {ex.new_id() for _ in range(1000)}
    assert len(ids) == 1000
    for i in ids:
        assert len(i) == 12
        assert set(i) <= set(ex.CROCKFORD)
    assert len(ex.new_id(20)) == 20


# --- Part C -----------------------------------------------------------------
def test_create_and_get(client):
    r = client.post("/flightReservations", json=BOOKING)
    assert r.status_code == 201
    body = r.json()
    assert body["cabin"] == "economy"
    assert len(body["id"]) == 12
    assert r.headers["Location"] == f"/flightReservations/{body['id']}"
    got = client.get(f"/flightReservations/{body['id']}")
    assert got.status_code == 200
    assert got.json() == body


def test_create_rejects_bad_flight_number(client):
    assert client.post("/flightReservations", json={**BOOKING, "flight_number": "af12"}).status_code == 422


def test_duplicate_is_conflict(client):
    client.post("/flightReservations", json=BOOKING)
    assert client.post("/flightReservations", json=BOOKING).status_code == 409


def test_get_missing(client):
    assert client.get("/flightReservations/doesnotexist").status_code == 404


def test_list(client):
    client.post("/flightReservations", json=BOOKING)
    client.post("/flightReservations", json={**BOOKING, "passenger": "Axel"})
    results = client.get("/flightReservations").json()["results"]
    assert sorted(r["passenger"] for r in results) == ["Axel", "Lea"]


def test_patch_reschedule_and_upgrade(client):
    rid = client.post("/flightReservations", json=BOOKING).json()["id"]
    r = client.patch(f"/flightReservations/{rid}", json={"date": "2026-12-26"})
    assert r.status_code == 200
    assert r.json()["date"] == "2026-12-26"
    r = client.patch(f"/flightReservations/{rid}", json={"cabin": "first"})
    assert r.json()["cabin"] == "first"
    assert r.json()["date"] == "2026-12-26", "PATCH must not reset fields that were not sent"
    assert client.patch("/flightReservations/nope", json={"cabin": "first"}).status_code == 404


@pytest.mark.parametrize("patch", [{"date": None}, {"cabin": None}, {"passenger": None}, {"passenger": ""}])
def test_patch_rejects_null_and_invalid(client, patch):
    rid = client.post("/flightReservations", json=BOOKING).json()["id"]
    assert client.patch(f"/flightReservations/{rid}", json=patch).status_code == 422
    assert client.get(f"/flightReservations/{rid}").json()["date"] == BOOKING["date"], "nothing must change"


def test_delete(client):
    rid = client.post("/flightReservations", json=BOOKING).json()["id"]
    r = client.delete(f"/flightReservations/{rid}")
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(f"/flightReservations/{rid}").status_code == 404
    assert client.delete(f"/flightReservations/{rid}").status_code == 404
