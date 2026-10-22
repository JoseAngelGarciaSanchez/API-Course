"""Lab 07 — JSON Web Tokens from scratch, then protecting routes.

Goal
    Issue signed tokens at login and protect routes with a bearer-token dependency.

You will learn
    * the anatomy of a JWT: base64url(header) . base64url(payload) . base64url(HMAC-SHA256)
    * the classic attacks: tampered payload, ``"alg": "none"``, expired tokens, timing attacks
    * storing passwords as salted, slow hashes
    * 401 (who are you?) vs 403 (I know who you are, and the answer is no)
    * dependencies that build on other dependencies, and an HTTP middleware

You build HS256 JWTs with the standard library only (base64, hmac, hashlib, json)
so that nothing is magic. In a real project use vetted libraries, as the FastAPI
docs now do: PyJWT for tokens and pwdlib (Argon2) for passwords. python-jose and
passlib, used in older tutorials, are no longer maintained.

References
    Slides : "JSON Web Token (JWT)" (header . payload . signature, HMACSHA256)
    Books  : [FA] ch. 11 (Authentication and Authorization) ; [ADP] ch. 30 (Request authentication)
    Docs   : https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
             https://datatracker.ietf.org/doc/html/rfc7519 (JWT)

Run it
    uv run uvicorn lab.lab07_jwt_auth.exercise:app --reload
    # in /docs: POST /token, copy the access_token, click "Authorize", paste it

Check your work
    uv run pytest lab/lab07_jwt_auth -v
"""

import base64  # noqa: F401
import hashlib
import hmac  # noqa: F401
import json
import os
import time  # noqa: F401
from typing import Annotated  # noqa: F401

from fastapi import Depends, FastAPI, HTTPException, Request, status  # noqa: F401
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # noqa: F401
from pydantic import BaseModel

SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")
ACCESS_TOKEN_MINUTES = 30


class InvalidToken(Exception):
    pass


# --- Part A: JWT by hand ------------------------------------------------------
def b64url_encode(data: bytes) -> str:
    """TODO A1: URL-safe base64 WITHOUT the trailing "=" padding (RFC 7515)."""
    raise NotImplementedError("TODO A1")


def b64url_decode(text: str) -> bytes:
    """TODO A2: inverse of b64url_encode — put the padding back first
    (the length of a base64 string must be a multiple of 4)."""
    raise NotImplementedError("TODO A2")


def _json(obj: dict) -> bytes:
    """Given: compact JSON, no spaces — the exact bytes matter for the signature."""
    return json.dumps(obj, separators=(",", ":")).encode()


def create_jwt(payload: dict, secret: str) -> str:
    """TODO A3: return  b64(header) + "." + b64(payload) + "." + b64(signature)

    header    = {"alg": "HS256", "typ": "JWT"}   (in that order, serialised with _json)
    signature = HMAC-SHA256(key=secret, msg=b64(header) + "." + b64(payload))
    Hint: hmac.new(key_bytes, msg_bytes, hashlib.sha256).digest()
    """
    raise NotImplementedError("TODO A3")


def verify_jwt(token: str, secret: str, now: float | None = None) -> dict:
    """TODO A4: return the payload if the token is valid, else raise InvalidToken.

    Reject: tokens that don't have 3 parts or don't decode; a header or payload
    that is not a JSON *object* (``[]`` decodes fine!); header alg != "HS256"
    (the famous "alg": "none" attack); a wrong signature — compare with
    hmac.compare_digest, not ==, to avoid timing attacks; an "exp" that is not a
    number, or an expired token (payload "exp" <= now, now defaults to time.time()).
    Anything you forget here becomes a 500 later, in code that trusts the payload.
    """
    raise NotImplementedError("TODO A4")


# --- Part B: passwords --------------------------------------------------------
def hash_password(password: str, salt: bytes | None = None) -> str:
    """Given: salted, slow hash (PBKDF2). Stored as "<salt hex>$<hash hex>"."""
    salt = os.urandom(16) if salt is None else salt
    # shortcut: OWASP recommends 600_000 iterations (or Argon2); kept low so the tests stay fast.
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """TODO B1: re-hash ``password`` with the salt found in ``stored`` and
    compare (hmac.compare_digest)."""
    raise NotImplementedError("TODO B1")


USERS: dict[str, dict] = {
    "lea": {"username": "lea", "hashed_password": hash_password("lea-password"), "admin": False},
    "admin": {"username": "admin", "hashed_password": hash_password("admin-password"), "admin": True},
}


# --- Part C: the API ----------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Hashed once at startup: login checks a password against it when the user does not exist.
DUMMY_HASH = hash_password("dummy-password")

app = FastAPI(title="Secured API")
# Since FastAPI 0.122, a missing or non-Bearer Authorization header is answered by
# HTTPBearer itself: 401 with the header "WWW-Authenticate: Bearer".
bearer = HTTPBearer()


# TODO C1: an HTTP *middleware* (@app.middleware("http")) that adds the header
#   X-Process-Time (seconds, as a string) to EVERY response.
#   async def add_process_time(request: Request, call_next): ...


# TODO C2: POST /token  body LoginRequest
#   wrong user or password -> 401, with the same message for both: why?
#   For an unknown user, still verify the password against DUMMY_HASH: why?
#   (hint: measure how long a failed login takes with and without it)
#   else -> Token whose JWT payload holds sub, admin, iat and exp (now + 30 min)
def login():
    raise NotImplementedError("TODO C2")


def current_user():
    """TODO C3: a dependency that returns the USERS entry of the caller.

    Signature hint:
        def current_user(creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]) -> dict
    ``bearer`` already rejects requests without a token. Invalid/expired token or
    unknown "sub" -> 401 too, with the header  WWW-Authenticate: Bearer  (RFC 6750).
    """
    raise NotImplementedError("TODO C3")


def admin_user():
    """TODO C4: a dependency built on current_user: non-admins -> 403 Forbidden.
    401 = "who are you?"   403 = "I know who you are, and the answer is no"."""
    raise NotImplementedError("TODO C4")


# TODO C5: GET /me  (any logged-in user) -> {"username": ..., "admin": ...}
def me():
    raise NotImplementedError("TODO C5")


# TODO C6: GET /admin/stats  (admins only) -> {"users": <number of users>}
def admin_stats():
    raise NotImplementedError("TODO C6")


@app.get("/public")
def public() -> dict:
    return {"message": "anyone can read this"}
