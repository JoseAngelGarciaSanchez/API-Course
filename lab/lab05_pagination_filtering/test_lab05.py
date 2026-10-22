import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab05_pagination_filtering")


@pytest.fixture
def client():
    return TestClient(ex.app)


def test_parse_filter():
    assert ex.parse_filter("") == {}
    assert ex.parse_filter("country=FR") == {"country": "FR"}
    assert ex.parse_filter('country = "US" AND area = "Alps"') == {"country": "US", "area": "Alps"}


@pytest.mark.parametrize("bad", ["country", "age = 3", 'country = "US" AND legs = 4'])
def test_parse_filter_errors(bad):
    with pytest.raises(ex.FilterError):
        ex.parse_filter(bad)


def test_apply_filter():
    found = ex.apply_filter(ex.CREATURES, {"country": "FR", "area": "Alps"})
    assert [c["name"] for c in found] == ["dahu"]


def test_token_roundtrip_and_opaque():
    token = ex.encode_page_token(20, "country=US")
    assert token not in ("20", "o=20") and not token.isdigit(), "the token must be opaque, not a raw offset"
    assert ex.decode_page_token(token, "country=US") == 20


def test_token_bound_to_filter():
    token = ex.encode_page_token(10, "country=US")
    with pytest.raises(ex.InvalidPageToken):
        ex.decode_page_token(token, "country=FR")


def test_token_garbage():
    with pytest.raises(ex.InvalidPageToken):
        ex.decode_page_token("not-a-token!!", "")


def test_effective_page_size():
    assert ex.effective_page_size(0) == ex.DEFAULT_PAGE_SIZE
    assert ex.effective_page_size(5) == 5
    assert ex.effective_page_size(10_000) == ex.MAX_PAGE_SIZE
    with pytest.raises(ValueError):
        ex.effective_page_size(-1)


def test_list_page_walks_everything():
    seen, token = [], ""
    for _ in range(10):
        page, token = ex.list_page(ex.CREATURES, max_page_size=5, page_token=token)
        seen += page
        if not token:
            break
    assert seen == ex.CREATURES


def test_endpoint_pages(client):
    first = client.get("/creatures", params={"max_page_size": 10}).json()
    assert len(first["results"]) == 10 and first["next_page_token"]
    second = client.get("/creatures", params={"max_page_size": 10, "page_token": first["next_page_token"]}).json()
    third = client.get("/creatures", params={"max_page_size": 10, "page_token": second["next_page_token"]}).json()
    assert len(third["results"]) == 3
    assert third["next_page_token"] == ""


def test_endpoint_filter(client):
    r = client.get("/creatures", params={"filter": "country = US", "max_page_size": 4}).json()
    assert all(c["country"] == "US" for c in r["results"])
    r2 = client.get(
        "/creatures", params={"filter": "country = US", "max_page_size": 4, "page_token": r["next_page_token"]}
    ).json()
    assert [c["name"] for c in r2["results"]] == ["thunderbird", "champ"]
    assert r2["next_page_token"] == ""


def test_endpoint_errors(client):
    assert client.get("/creatures", params={"filter": "legs = 4"}).status_code == 400
    assert client.get("/creatures", params={"page_token": "garbage"}).status_code == 400
    assert client.get("/creatures", params={"max_page_size": -3}).status_code == 400
    token = client.get("/creatures", params={"filter": "country = US", "max_page_size": 2}).json()["next_page_token"]
    changed = client.get("/creatures", params={"filter": "country = FR", "page_token": token})
    assert changed.status_code == 400, "reusing a token with another filter must fail"


def test_endpoint_rejects_unknown_parameters(client):
    r = client.get("/creatures", params={"page_size": 5})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "page_size"]


def test_openapi_documents_query_parameters(client):
    op = client.get("/openapi.json").json()["paths"]["/creatures"]["get"]
    assert sorted(p["name"] for p in op["parameters"]) == ["filter", "max_page_size", "page_token"]
