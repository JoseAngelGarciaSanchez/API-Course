"""No real network call here: httpx2.MockTransport fakes JSONPlaceholder."""

import json

import httpx2
import pytest

from lab._loader import load

ex = load("lab00_query_open_apis")

POSTS = [
    {"userId": 1, "id": 1, "title": "Sunt aut facere", "body": "a"},
    {"userId": 1, "id": 2, "title": "qui est esse", "body": "b"},
    {"userId": 2, "id": 3, "title": "ea molestias quasi", "body": "c"},
]


def fake_api(request: httpx2.Request) -> httpx2.Response:
    path = request.url.path
    if request.method == "POST" and path == "/posts":
        assert request.headers["content-type"].startswith("application/json"), "send JSON: json=..."
        return httpx2.Response(201, json={**json.loads(request.content), "id": 101})
    assert request.method == "GET"
    if path == "/posts":
        user = request.url.params.get("userId")
        return httpx2.Response(200, json=[p for p in POSTS if user in (None, str(p["userId"]))])
    post_id = path.removeprefix("/posts/")
    if post_id == "500":
        return httpx2.Response(500, text="boom")
    return next(
        (httpx2.Response(200, json=p) for p in POSTS if str(p["id"]) == post_id),
        httpx2.Response(404, json={}),
    )


@pytest.fixture
def client():
    with httpx2.Client(transport=httpx2.MockTransport(fake_api), base_url=ex.BASE_URL) as c:
        yield c


def test_get_posts(client):
    assert ex.get_posts(client) == POSTS


def test_get_post(client):
    assert ex.get_post(client, 2) == POSTS[1]


def test_get_post_missing_is_none(client):
    assert ex.get_post(client, 999) is None


def test_get_post_server_error_raises(client):
    with pytest.raises(httpx2.HTTPStatusError):
        ex.get_post(client, 500)


def test_posts_by_user(client):
    assert ex.posts_by_user(client, 1) == POSTS[:2]
    assert ex.posts_by_user(client, 42) == []


def test_titles_with_word(client):
    assert ex.titles_with_word(client, "SUNT") == ["Sunt aut facere"]
    assert ex.titles_with_word(client, "zzz") == []


def test_create_post(client):
    created = ex.create_post(client, 7, "Hi", "Body")
    assert created == {"userId": 7, "title": "Hi", "body": "Body", "id": 101}


def test_my_api_is_filled_in():
    assert all(v != "TODO" for v in ex.MY_API.values()), "fill in MY_API (part D1)"
