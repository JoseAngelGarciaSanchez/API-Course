"""Lab 10 — Serve a (tiny) ML model and call an external API.

Goal
    Two building blocks of the final project: a prediction endpoint, and an endpoint
    that calls someone else's API and survives its failures.

You will learn
    * serving a deterministic model, one record at a time, in batch, and as a stream
    * streaming JSON Lines with ``yield`` (FastAPI >= 0.134)
    * calling an external API asynchronously with httpx2, sharing ONE client created
      in the app's ``lifespan``
    * never trusting an upstream: validate what you forward, translate its errors
      (404, 502 Bad Gateway, 504 Gateway Timeout)
    * testing without the network: ``httpx2.MockTransport`` + dependency overrides

References
    Slides : "API Parameters: Body" (predict_passing_year), "Why build a web API?"
             (hide the heavy lifting), "Coding time" (external API + little model)
    Books  : [FA] ch. 4 (async), ch. 12 (testing with mocks), ch. 14 (Data science and a little AI)
             [ADP] ch. 18 (Batch operations)
    Docs   : https://fastapi.tiangolo.com/advanced/events/ (lifespan)
             https://fastapi.tiangolo.com/tutorial/stream-json-lines/
             https://datahelpdesk.worldbank.org/knowledgebase/articles/898590 (World Bank country API)

Run it against the real World Bank API (no key needed)
    uv run uvicorn lab.lab10_external_api_and_model.exercise:app --reload
    # http://127.0.0.1:8000/countries/fr

Check your work (the tests never touch the network)
    uv run pytest lab/lab10_external_api_and_model -v
"""

from collections.abc import AsyncIterator, Iterable  # noqa: F401
from contextlib import asynccontextmanager
from typing import Annotated

import httpx2
from fastapi import Depends, FastAPI, HTTPException, Path, Request  # noqa: F401
from pydantic import BaseModel, Field

# --- Part A: a (very) small deterministic model ------------------------------
MODEL_VERSION = "linear-v1"
INTERCEPT = 2.0
COEFFICIENTS = {"last_average_mark": 0.7, "dedicated_hours": 0.05}
LEVEL_BONUS = {"L3": 0.0, "M1": 0.5, "M2": 1.0}
PASS_MARK = 10.0


class StudentRecord(BaseModel):
    id: int = Field(gt=0)
    last_validate_level: str = Field(pattern=r"^(L3|M1|M2)$")
    last_average_mark: float = Field(ge=0, le=20)
    dedicated_hours: int = Field(ge=0)


class Prediction(BaseModel):
    id: int
    predicted_mark: float
    passes: bool
    model_version: str = MODEL_VERSION


def predict_mark(record: StudentRecord) -> float:
    """TODO A1: linear regression with FIXED coefficients.

    mark = INTERCEPT + sum(coef * feature) + LEVEL_BONUS[level]
    Clip to [0, 20] and round to 2 decimals.
    """
    raise NotImplementedError("TODO A1")


def predict(record: StudentRecord) -> Prediction:
    """TODO A2: wrap predict_mark into a Prediction (passes = mark >= PASS_MARK)."""
    raise NotImplementedError("TODO A2")


# --- Part B: calling an external API ------------------------------------------
WORLD_BANK_API = "https://api.worldbank.org/v2"


class CountryNotFound(Exception):
    pass


class UpstreamError(Exception):
    pass


class UpstreamTimeout(UpstreamError):
    pass


async def fetch_country(code: str, client: httpx2.AsyncClient) -> dict:
    """TODO B1: GET /country/<code>?format=json with ``client`` (it already has the base_url).

    The World Bank answers a JSON list ``[metadata, [country, ...]]``::

        [{"page": 1, ...}, [{"iso2Code": "FR", "name": "France", "capitalCity": "Paris",
                             "region": {"value": "Europe & Central Asia"},
                             "incomeLevel": {"value": "High income"}, ...}]]

    Return {"code": "FR", "name": "France", "capital": "Paris",
            "region": "Europe & Central Asia", "income_level": "High income"}

    Careful: for an unknown code it answers **200** with ``[{"message": [...]}]``.
    Never trust an upstream status code alone. Translate everything into OUR
    exceptions (never leak httpx2 outside this function):
      200 but no country list                -> CountryNotFound
      any other status, or a body that is not JSON -> UpstreamError
      httpx2.TimeoutException                -> UpstreamTimeout
      any other httpx2.HTTPError             -> UpstreamError
    """
    raise NotImplementedError("TODO B1")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """TODO B2: runs once at startup (before ``yield``) and once at shutdown (after).

    Create ONE ``httpx2.AsyncClient(base_url=WORLD_BANK_API, timeout=5.0)``, store it in
    ``app.state.http_client`` and make sure it is closed at shutdown
    (``async with ... as client:`` around the ``yield``).
    Why share one client instead of opening one per request?
    (In a real project you would also load the trained model here, once.)
    """
    yield


def get_http_client(request: Request) -> httpx2.AsyncClient:
    """Given: the dependency that hands the shared client to the endpoints.
    The tests replace it with a client whose transport is fake."""
    return request.app.state.http_client


# --- Part C: the API ----------------------------------------------------------
app = FastAPI(title="Predictions", lifespan=lifespan)
HTTP = Annotated[httpx2.AsyncClient, Depends(get_http_client)]


# TODO C1: GET /health -> {"status": "ok", "model_version": MODEL_VERSION}
def health():
    raise NotImplementedError("TODO C1")


# TODO C2: POST /predict  (body StudentRecord) -> Prediction
def predict_one():
    raise NotImplementedError("TODO C2")


# TODO C3: POST /predict:batch  body = a JSON list of 1 to 100 StudentRecord
#   -> {"predictions": [...]} in the same order. Outside 1..100 -> 422.
#   Hint: Annotated[list[StudentRecord], Field(min_length=1, max_length=100)]
#   Question ([ADP] ch. 18): if record #57 is invalid, should the whole batch fail?
def predict_batch():
    raise NotImplementedError("TODO C3")


# TODO C4: POST /predict:stream  body = a JSON list of StudentRecord
#   -> one Prediction per line (JSON Lines, content type application/jsonl).
#   Use ``yield`` instead of ``return`` and declare  -> Iterable[Prediction]:
#   the client starts receiving predictions before the last one is computed.
def predict_stream():
    raise NotImplementedError("TODO C4")


# TODO C5: GET /countries/{code}  -> the dict from fetch_country (async def!)
#   ``code`` comes from the client and ends up in the World Bank URL: accept only
#   2 or 3 letters (Path(pattern=...)), anything else -> 422 before any call.
#   CountryNotFound -> 404, UpstreamTimeout -> 504 Gateway Timeout,
#   UpstreamError -> 502 Bad Gateway. Why not 500?
def country():
    raise NotImplementedError("TODO C5")
