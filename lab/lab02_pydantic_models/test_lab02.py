from datetime import date

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from lab._loader import load

ex = load("lab02_pydantic_models")

GOOD = {"id": 1, "last_validate_level": "M1", "last_average_mark": 14.5, "dedicated_hours": 20}


def test_student_ok():
    s = ex.StudentRecord(**GOOD)
    assert s.last_average_mark == 14.5


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", 0),
        ("last_validate_level", "M"),
        ("last_validate_level", "M12"),
        ("last_average_mark", 21),
        ("last_average_mark", -1),
        ("dedicated_hours", -5),
    ],
)
def test_student_constraints(field, value):
    with pytest.raises(ValidationError):
        ex.StudentRecord(**{**GOOD, field: value})


def test_level_validator():
    assert ex.StudentRecord(**{**GOOD, "last_validate_level": "m2"}).last_validate_level == "M2"
    with pytest.raises(ValidationError):
        ex.StudentRecord(**{**GOOD, "last_validate_level": "XX"})


def test_creature():
    c = ex.Creature(name="yeti", country="CN", area="Himalayas", description="Hirsute")
    assert c.aka is None
    assert c.tags == []
    c.tags.append("cold")
    assert ex.Creature(name="nessie", country="GB", area="Loch Ness", description="Wet").tags == []
    assert ex.Creature(name="x" * 2, country="*", area="*", description="?").country == "*"


@pytest.mark.parametrize("kwargs", [{"name": "y"}, {"country": "china"}, {"country": "cn"}])
def test_creature_invalid(kwargs):
    base = {"name": "yeti", "country": "CN", "area": "Himalayas", "description": "Hirsute"}
    with pytest.raises(ValidationError):
        ex.Creature(**{**base, **kwargs})


def test_booking():
    ex.Booking(guest="Lea", start=date(2026, 1, 1), end=date(2026, 1, 3))
    with pytest.raises(ValidationError):
        ex.Booking(guest="Lea", start=date(2026, 1, 3), end=date(2026, 1, 3))


def test_parse_students():
    rows = [GOOD, {**GOOD, "id": -1}, {**GOOD, "id": 2}, {"id": 3}]
    valid, invalid = ex.parse_students(rows)
    assert [s.id for s in valid] == [1, 2]
    assert invalid == [1, 3]


def test_post_students():
    c = TestClient(ex.app)
    r = c.post("/students", json=GOOD)
    assert r.status_code == 201
    assert r.json()["last_validate_level"] == "M1"
    bad = c.post("/students", json={**GOOD, "last_average_mark": 42})
    assert bad.status_code == 422
    assert bad.json()["detail"][0]["loc"] == ["body", "last_average_mark"]


def test_post_users_hides_password():
    c = TestClient(ex.app)
    r = c.post("/users", json={"username": "lea", "password": "s3cret-password"})
    assert r.status_code == 201
    assert r.json() == {"username": "lea"}
    assert c.post("/users", json={"username": "lea", "password": "short"}).status_code == 422


def test_post_users_rejects_unknown_fields():
    c = TestClient(ex.app)
    r = c.post("/users", json={"username": "eve", "password": "s3cret-password", "admin": True})
    assert r.status_code == 422, "unknown fields must be rejected, not silently ignored"
    assert r.json()["detail"][0]["type"] == "extra_forbidden"
