"""Lab 04 — Layers and dependencies. Web layer: HTTP in, HTTP out.

Goal
    Split the cryptid API into web -> service -> data layers on top of SQLite,
    and wire them together with FastAPI dependencies.

You will learn
    * what belongs in each layer (start with data.py, then service.py, then this file)
    * reusable dependencies with ``Depends`` and ``Annotated`` aliases
    * mapping domain exceptions to HTTP status codes ONCE, with exception handlers
    * testing each layer, and swapping the database with ``app.dependency_overrides``
    * why SQL placeholders defeat SQL injection

References
    Books : [FA] ch. 6 (Dependencies), 8 (Web), 9 (Service), 10 (Data), 12 (Testing)
    Docs  : https://fastapi.tiangolo.com/tutorial/dependencies/
            https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers

Run it
    uv run uvicorn lab.lab04_layers_and_dependencies.exercise.web:app --reload

Check your work
    uv run pytest lab/lab04_layers_and_dependencies -v
"""

import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Query, Request, status  # noqa: F401
from fastapi.responses import JSONResponse  # noqa: F401

from . import data, service
from .errors import Duplicate, Missing  # noqa: F401
from .model import Creature

_conn = sqlite3.connect(":memory:", check_same_thread=False)
data.init(_conn)


def get_db() -> Iterator[sqlite3.Connection]:
    """Given: a *dependency*. Tests replace it with
    ``app.dependency_overrides[get_db] = ...`` to use a fresh database."""
    yield _conn


@dataclass
class Paging:
    skip: int
    limit: int


def paging(skip: int = 0, limit: int = 10) -> Paging:
    """TODO W1: a reusable dependency for query parameters.

    skip must be >= 0 and limit between 1 and 100, otherwise FastAPI answers
    422 by itself. Hint: ``skip: Annotated[int, Query(ge=0)] = 0``.
    """
    return Paging(skip=skip, limit=limit)


DB = Annotated[sqlite3.Connection, Depends(get_db)]

app = FastAPI(title="Cryptid API")
router = APIRouter(prefix="/creature", tags=["creature"])


# TODO W0: the service raises Missing / Duplicate. Instead of a try/except in every
#   endpoint, register two exception handlers on the app:
#       @app.exception_handler(Missing)
#       async def missing_handler(request: Request, exc: Missing) -> JSONResponse: ...
#   Missing -> 404, Duplicate -> 409, body {"detail": str(exc)} like HTTPException.


# TODO W2: GET /creature?skip=&limit=  -> list[Creature]   (use Depends(paging))
def get_all():
    raise NotImplementedError("TODO W2")


# TODO W3: GET /creature/stats/by-country -> {"CN": 1, ...}
#   Question: why must this route be declared BEFORE GET /creature/{name}?
def stats():
    raise NotImplementedError("TODO W3")


@router.get("/{name}")
def get_one(name: str, conn: DB) -> Creature:
    """Given: no try/except here. Once TODO W0 is done, a Missing raised deep in the
    data layer becomes a 404 on its way out."""
    return service.get_one(conn, name)


# TODO W4: POST /creature -> 201 (Duplicate -> 409 is handled by W0)
def create():
    raise NotImplementedError("TODO W4")


# TODO W5: PUT /creature/{name} -> 200 (Missing -> 404 is handled by W0)
def replace():
    raise NotImplementedError("TODO W5")


# TODO W6: DELETE /creature/{name} -> 204 with no body (status_code=204 and -> None)
def delete():
    raise NotImplementedError("TODO W6")


# Since FastAPI 0.137 this line could also come first: routers are no longer copied.
app.include_router(router)
