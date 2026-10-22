import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab06_updates_custom_methods")


@pytest.fixture
def client():
    ex.DB.clear()
    ex.DB.update(ex.seed())
    return TestClient(ex.app)


def yeti():
    return ex.seed()["yeti"]


# --- Part A -------------------------------------------------------------------
def test_leaf_paths():
    assert sorted(ex.leaf_paths({"name": "x", "location": {"area": "y", "country": "z"}})) == [
        "location.area",
        "location.country",
        "name",
    ]


def test_implicit_mask_keeps_sibling_fields():
    out = ex.apply_field_mask(yeti(), {"location": {"area": "Tibet"}})
    assert out["location"] == {"country": "CN", "area": "Tibet"}, "a nested patch must not wipe siblings"
    assert out["name"] == "Yeti"


def test_does_not_mutate_input():
    original = yeti()
    ex.apply_field_mask(original, {"location": {"area": "Tibet"}})
    assert original == yeti()


def test_explicit_mask_only_touches_masked_fields():
    out = ex.apply_field_mask(yeti(), {"name": "Migoi", "aka": "ignored"}, ["name"])
    assert out["name"] == "Migoi"
    assert out["aka"] == "Abominable Snowman"


def test_explicit_mask_resets_missing_fields():
    out = ex.apply_field_mask(yeti(), {}, ["aka"])
    assert out["aka"] is None


@pytest.mark.parametrize("mask", [["id"], ["deleted"], ["sightings"], ["legs"], ["location.planet"]])
def test_invalid_masks(mask):
    with pytest.raises(ValueError):
        ex.apply_field_mask(yeti(), {}, mask)


def test_project():
    assert ex.project(yeti(), ["name", "location.country"]) == {"name": "Yeti", "location": {"country": "CN"}}
    with pytest.raises(ValueError):
        ex.project(yeti(), ["nope"])


# --- Part B -------------------------------------------------------------------
def test_patch_endpoint(client):
    r = client.patch("/creatures/yeti", json={"location": {"area": "Bhutan"}})
    assert r.status_code == 200
    assert r.json()["location"] == {"country": "CN", "area": "Bhutan"}
    r = client.patch("/creatures/yeti", params={"update_mask": "aka"}, json={})
    assert r.json()["aka"] is None
    assert client.patch("/creatures/yeti", params={"update_mask": "id"}, json={"id": "x"}).status_code == 400
    assert client.patch("/creatures/bigfoot", json={}).status_code == 404


def test_partial_get(client):
    r = client.get("/creatures/nessie", params={"fields": "name,location.area"})
    assert r.json() == {"name": "Loch Ness Monster", "location": {"area": "Loch Ness"}}
    assert client.get("/creatures/nessie", params={"fields": "wings"}).status_code == 400


def test_custom_method(client):
    r = client.post("/creatures/yeti:reportSighting")
    assert r.status_code == 200
    r = client.post("/creatures/yeti:reportSighting")
    assert r.json()["sightings"] == 2
    assert r.json()["last_seen"] is not None
    assert client.post("/creatures/bigfoot:reportSighting").status_code == 404


def test_soft_delete_lifecycle(client):
    r = client.delete("/creatures/yeti")
    assert r.status_code == 200 and r.json()["deleted"] is True, "soft delete returns the resource"
    assert client.get("/creatures/yeti").status_code == 200, "GET still works on a soft-deleted resource"
    assert [c["id"] for c in client.get("/creatures").json()["results"]] == ["nessie"]
    assert len(client.get("/creatures", params={"include_deleted": True}).json()["results"]) == 2
    assert client.delete("/creatures/yeti").status_code == 412
    assert client.post("/creatures/yeti:reportSighting").status_code == 412
    assert client.post("/creatures/yeti:undelete").json()["deleted"] is False
    assert client.post("/creatures/yeti:undelete").status_code == 412
    expunged = client.post("/creatures/yeti:expunge")
    assert expunged.status_code == 204 and expunged.content == b""
    assert client.get("/creatures/yeti").status_code == 404
