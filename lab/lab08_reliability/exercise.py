"""Lab 08 — Reliability: deduplication, validation-only requests, retries.

Goal
    Make a payment API safe to retry, and write the client that retries it.

The scenario: a client sends POST /payments, the network drops the *response*,
the client retries... and Lea gets paid twice. We fix it on both sides:
  * server: a client-chosen ``request_id`` + a fingerprint of the body
  * client: retry only what is safe, with exponential backoff, honouring Retry-After

You will learn
    * request deduplication (idempotency) for non-idempotent methods such as POST
    * ``validate_only``: check a request without executing it
    * which failures are worth retrying, exponential backoff with full jitter, Retry-After

Here the id travels in the body, as in [ADP]. Many public APIs (Stripe, Adyen...) send
it in a header instead: ``Idempotency-Key`` (IETF draft "The Idempotency-Key HTTP
Header Field"). The server-side logic is the same.

References
    Books : [ADP] ch. 26 (Request deduplication), ch. 27 (Request validation), ch. 29 (Request retrial)
    Docs  : https://www.rfc-editor.org/rfc/rfc9110#name-retry-after
            https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/

Run it
    uv run uvicorn lab.lab08_reliability.exercise:app --reload

Check your work
    uv run pytest lab/lab08_reliability -v
"""

import hashlib  # noqa: F401
import json  # noqa: F401
import random
import time
from collections.abc import Callable
from datetime import UTC, datetime  # noqa: F401
from email.utils import parsedate_to_datetime  # noqa: F401
from typing import Literal

import httpx2
from fastapi import FastAPI, HTTPException, Response, status  # noqa: F401
from pydantic import BaseModel, Field

# --- Part A: request deduplication + validation-only requests -----------------
BALANCE = 1_000.0


class PaymentRequest(BaseModel):
    request_id: str | None = None
    amount: float = Field(gt=0)
    currency: Literal["EUR", "USD"]
    to: str = Field(min_length=1)


class Payment(BaseModel):
    id: str | None
    amount: float
    currency: str
    to: str


PAYMENTS: dict[str, Payment] = {}
REQUEST_CACHE: dict[str, tuple[str, Payment]] = {}  # request_id -> (fingerprint, response)


def fingerprint(body: dict) -> str:
    """TODO A1: SHA-256 hex digest of the body serialised as JSON with
    sorted keys, so {"a":1,"b":2} and {"b":2,"a":1} give the same value."""
    raise NotImplementedError("TODO A1")


def check_business_rules(req: PaymentRequest) -> None:
    """Given: you cannot spend more than BALANCE minus what was already paid."""
    spent = sum(p.amount for p in PAYMENTS.values())
    if req.amount > BALANCE - spent:
        raise ValueError("insufficient funds")


app = FastAPI(title="Payments")


# TODO A2: POST /payments?validate_only=false   body PaymentRequest
#   1. fingerprint the body WITHOUT request_id
#   2. request_id already in REQUEST_CACHE:
#        same fingerprint      -> return the cached Payment (nothing new created)
#        different fingerprint -> 409 Conflict
#   3. check_business_rules; ValueError -> 400
#   4. validate_only=true -> 200 with Payment(id=None, ...), store NOTHING
#      (hint: add a `response: Response` parameter and set response.status_code)
#   5. otherwise store Payment(id=f"pay_{n:04d}") in PAYMENTS, cache it under
#      request_id if there is one, answer 201.
#   Question: two retries of the same request arrive at the SAME time, on two
#   workers. Both miss the cache... What would a real database need here?
def create_payment():
    raise NotImplementedError("TODO A2")


@app.get("/payments")
def list_payments() -> dict:
    return {"results": list(PAYMENTS.values())}


# --- Part B: retrying on the client side ---------------------------------------
RETRYABLE_STATUS = {429, 502, 503, 504}


def backoff_delays(
    max_attempts: int, base: float = 0.1, cap: float = 5.0, rng: random.Random | None = None
) -> list[float]:
    """TODO B1: the waits *between* attempts (so max_attempts - 1 values).

    delay_i = min(cap, base * 2**i)                 -> 0.1, 0.2, 0.4, 0.8 ...
    If ``rng`` is given, use "full jitter": rng.uniform(0, delay_i), so that
    thousands of clients don't all retry at the same instant.
    """
    raise NotImplementedError("TODO B1")


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """TODO B2: the Retry-After header is either seconds ("120") or an HTTP
    date ("Wed, 21 Oct 2026 12:00:30 GMT"). Return seconds to wait (>= 0),
    or None if absent/unparseable. Hint: email.utils.parsedate_to_datetime,
    and ``now`` defaults to datetime.now(UTC).
    """
    raise NotImplementedError("TODO B2")


def call_with_retry(
    send: Callable[[], httpx2.Response],
    max_attempts: int = 4,
    base: float = 0.1,
    cap: float = 5.0,
    sleep: Callable[[float], None] = time.sleep,
) -> httpx2.Response:
    """TODO B3: call ``send()`` until it works or attempts run out.

    * response status in RETRYABLE_STATUS -> wait and retry
      (wait = Retry-After if present (capped), else backoff_delays(...)[attempt])
    * httpx2.TransportError (network down...) -> wait and retry
    * any other response (2xx, 400, 404...) -> return it immediately
    * last attempt: return the response / re-raise the exception
    Always wait with the injected ``sleep`` (tests pass a fake one).
    """
    raise NotImplementedError("TODO B3")
