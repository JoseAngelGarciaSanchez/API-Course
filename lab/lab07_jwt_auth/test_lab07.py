import time

import pytest
from fastapi.testclient import TestClient

from lab._loader import load

ex = load("lab07_jwt_auth")

# The example token from https://jwt.io (secret: "your-256-bit-secret")
JWT_IO_PAYLOAD = {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
JWT_IO_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
    "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
)


@pytest.fixture
def client():
    return TestClient(ex.app)


def login(client, user, pwd):
    return client.post("/token", json={"username": user, "password": pwd})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- Part A -------------------------------------------------------------------
def test_b64url():
    assert ex.b64url_encode(b"\xfb\xff") == "-_8"
    for raw in [b"", b"a", b"ab", b"abc", b"abcd", bytes(range(256))]:
        enc = ex.b64url_encode(raw)
        assert "=" not in enc
        assert ex.b64url_decode(enc) == raw


def test_create_matches_jwt_io():
    assert ex.create_jwt(JWT_IO_PAYLOAD, "your-256-bit-secret") == JWT_IO_TOKEN


def test_verify_ok():
    assert ex.verify_jwt(JWT_IO_TOKEN, "your-256-bit-secret") == JWT_IO_PAYLOAD


def test_verify_wrong_secret():
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(JWT_IO_TOKEN, "guess")


def test_verify_tampered_payload():
    h, _, s = JWT_IO_TOKEN.split(".")
    forged = ex.b64url_encode(b'{"sub":"1234567890","name":"John Doe","admin":true}')
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(f"{h}.{forged}.{s}", "your-256-bit-secret")


def test_verify_alg_none():
    h = ex.b64url_encode(b'{"alg":"none","typ":"JWT"}')
    p = ex.b64url_encode(b'{"sub":"admin"}')
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(f"{h}.{p}.", "your-256-bit-secret")


@pytest.mark.parametrize("garbage", ["", "abc", "a.b", "a.b.c.d", "!!.??.**"])
def test_verify_garbage(garbage):
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(garbage, "s")


@pytest.mark.parametrize("header,payload", [(b"[]", b"{}"), (b'{"alg":"HS256"}', b'["lea"]')])
def test_verify_rejects_non_object_parts(header, payload):
    h, p = ex.b64url_encode(header), ex.b64url_encode(payload)
    signature = ex.create_jwt({}, "s").split(".")[2]
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(f"{h}.{p}.{signature}", "s")


def test_verify_rejects_non_numeric_exp():
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(ex.create_jwt({"sub": "lea", "exp": "soon"}, "s"), "s")


def test_verify_expiry():
    token = ex.create_jwt({"sub": "lea", "exp": 1_000}, "s")
    assert ex.verify_jwt(token, "s", now=999)["sub"] == "lea"
    with pytest.raises(ex.InvalidToken):
        ex.verify_jwt(token, "s", now=1_000)


# --- Part B -------------------------------------------------------------------
def test_passwords():
    stored = ex.hash_password("correct horse")
    assert "correct horse" not in stored
    assert ex.verify_password("correct horse", stored)
    assert not ex.verify_password("wrong horse", stored)
    assert ex.hash_password("x") != ex.hash_password("x"), "salts must differ"


# --- Part C -------------------------------------------------------------------
def test_middleware(client):
    r = client.get("/public")
    assert float(r.headers["X-Process-Time"]) >= 0


def test_login(client):
    r = login(client, "lea", "lea-password")
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    payload = ex.verify_jwt(body["access_token"], ex.SECRET_KEY)
    assert payload["sub"] == "lea" and payload["admin"] is False
    assert 0 < payload["exp"] - time.time() <= ex.ACCESS_TOKEN_MINUTES * 60 + 1


def test_login_failures(client):
    wrong_password, unknown_user = login(client, "lea", "nope"), login(client, "ghost", "nope")
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json(), "do not reveal which usernames exist"


def test_login_hashes_even_for_unknown_users(client, monkeypatch):
    calls = []

    def spy(password, stored):
        calls.append(stored)
        return False

    monkeypatch.setattr(ex, "verify_password", spy)
    login(client, "ghost", "nope")
    assert calls == [ex.DUMMY_HASH], "an unknown user must cost as much time as a wrong password"


def test_me(client):
    token = login(client, "lea", "lea-password").json()["access_token"]
    assert client.get("/me", headers=auth(token)).json() == {"username": "lea", "admin": False}


def test_me_requires_token(client):
    r = client.get("/me")
    assert r.status_code == 401
    assert r.headers.get("WWW-Authenticate") == "Bearer"
    invalid = client.get("/me", headers=auth("not.a.token"))
    assert invalid.status_code == 401
    assert invalid.headers.get("WWW-Authenticate") == "Bearer"


def test_me_rejects_expired_and_forged(client):
    expired = ex.create_jwt({"sub": "lea", "exp": int(time.time()) - 1}, ex.SECRET_KEY)
    assert client.get("/me", headers=auth(expired)).status_code == 401
    forged = ex.create_jwt({"sub": "admin", "admin": True}, "attacker-secret")
    assert client.get("/me", headers=auth(forged)).status_code == 401
    ghost = ex.create_jwt({"sub": "ghost"}, ex.SECRET_KEY)
    assert client.get("/me", headers=auth(ghost)).status_code == 401


def test_admin(client):
    lea = login(client, "lea", "lea-password").json()["access_token"]
    admin = login(client, "admin", "admin-password").json()["access_token"]
    assert client.get("/admin/stats").status_code == 401
    assert client.get("/admin/stats", headers=auth(lea)).status_code == 403
    assert client.get("/admin/stats", headers=auth(admin)).json() == {"users": 2}
