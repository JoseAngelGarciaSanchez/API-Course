"""Lab 05 — Pagination and filtering for List methods.

Goal
    Make GET /creatures scale: return the collection page by page, with a filter.

You will learn
    * why opaque page tokens beat ?skip=&limit= ([ADP] ch. 21: offsets leak the
      storage layout and break when data changes)
    * binding a token to the request that produced it
    * a tiny filter language, parsed and validated on the server ([ADP] ch. 22)
    * grouping query parameters in a Pydantic *query-parameter model* that forbids
      unknown parameters

The response shape (the List standard method of [ADP])::

    {"results": [...], "next_page_token": "..."}   # "" means "last page"

References
    Books  : [ADP] ch. 21 (Pagination), ch. 22 (Filtering) ; [FA] ch. 8 (query parameters)
    Docs   : https://fastapi.tiangolo.com/tutorial/query-param-models/
    Lab 09 : chunks() there is the plain-Python version of this (do it first if you like).

Run it
    uv run uvicorn lab.lab05_pagination_filtering.exercise:app --reload

Check your work
    uv run pytest lab/lab05_pagination_filtering -v
"""

import base64  # noqa: F401
import hashlib
import json  # noqa: F401
from typing import Annotated  # noqa: F401

from fastapi import FastAPI, HTTPException, Query  # noqa: F401
from pydantic import BaseModel, ConfigDict  # noqa: F401

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
FILTERABLE_FIELDS = {"name", "country", "area"}

# fmt: off
CREATURES: list[dict] = [
    {"name": n, "country": c, "area": a}
    for n, c, a in [
        ("bigfoot", "US", "Pacific Northwest"), ("bunyip", "AU", "Swamps"), ("chupacabra", "MX", "Puerto Rico"),
        ("dover demon", "US", "Massachusetts"), ("jersey devil", "US", "Pine Barrens"), ("kraken", "NO", "Sea"),
        ("loch ness monster", "GB", "Loch Ness"), ("mapinguari", "BR", "Amazon"), ("mokele-mbembe", "CG", "Congo"),
        ("mothman", "US", "West Virginia"), ("ogopogo", "CA", "Okanagan Lake"), ("orang pendek", "ID", "Sumatra"),
        ("thunderbird", "US", "Great Plains"), ("tatzelwurm", "AT", "Alps"), ("wendigo", "CA", "Forests"),
        ("yeti", "CN", "Himalayas"), ("yowie", "AU", "Bush"), ("zana", "GE", "Caucasus"),
        ("almas", "MN", "Altai"), ("beast of bodmin", "GB", "Cornwall"), ("champ", "US", "Lake Champlain"),
        ("dahu", "FR", "Alps"), ("drac", "FR", "Rhone"),
    ]
]
# fmt: on


class FilterError(ValueError):
    pass


class InvalidPageToken(ValueError):
    pass


def parse_filter(text: str) -> dict[str, str]:
    """TODO F1: parse a tiny filter language.

    'country = "US" AND area = "Alps"'  -> {"country": "US", "area": "Alps"}
    'country=FR'                         -> {"country": "FR"}
    ''                                   -> {}
    Clauses are separated by " AND "; spaces around "=" and double quotes
    around values are optional. Raise FilterError for a clause without "="
    or a field not in FILTERABLE_FIELDS.
    """
    raise NotImplementedError("TODO F1")


def apply_filter(items: list[dict], criteria: dict[str, str]) -> list[dict]:
    """TODO F2: keep the items matching *all* criteria (exact match)."""
    raise NotImplementedError("TODO F2")


def _fingerprint(filter_text: str) -> str:
    """Given: short hash of the filter, stored inside the token."""
    return hashlib.sha256(filter_text.encode()).hexdigest()[:16]


def encode_page_token(offset: int, filter_text: str) -> str:
    """TODO P1: build an opaque token holding the offset AND the filter fingerprint.

    Suggestion: json.dumps({"o": offset, "f": _fingerprint(filter_text)}),
    then base64.urlsafe_b64encode. (Real APIs also encrypt or sign it.)
    """
    raise NotImplementedError("TODO P1")


def decode_page_token(token: str, filter_text: str) -> int:
    """TODO P2: return the offset stored in ``token``.

    Raise InvalidPageToken if the token is garbage, OR if it was issued for a
    different filter (Geewax: a token is only valid for the same request).
    """
    raise NotImplementedError("TODO P2")


def effective_page_size(max_page_size: int) -> int:
    """TODO P3: 0 -> DEFAULT_PAGE_SIZE ; > MAX_PAGE_SIZE -> MAX_PAGE_SIZE ;
    negative -> ValueError. ("max" because the server may return fewer.)"""
    raise NotImplementedError("TODO P3")


def list_page(
    items: list[dict], max_page_size: int = 0, page_token: str = "", filter_text: str = ""
) -> tuple[list[dict], str]:
    """TODO P4: return (page_of_results, next_page_token).

    Filter first, then slice. next_page_token is "" on the last page.
    """
    raise NotImplementedError("TODO P4")


class Creature(BaseModel):
    name: str
    country: str
    area: str


class ListCreaturesResponse(BaseModel):
    results: list[Creature]
    next_page_token: str


class ListCreaturesRequest(BaseModel):
    """TODO E0: the three query parameters of the List method, in one model:

        max_page_size: int = 0,  page_token: str = "",  filter: str = ""

    and ``model_config = ConfigDict(extra="forbid")`` so that an unknown parameter
    (a typo such as ?page_size=5) is a 422 instead of being silently ignored.
    """


app = FastAPI(title="Cryptids")


# TODO E1: GET /creatures?max_page_size=&page_token=&filter=  -> ListCreaturesResponse
#   Declare the parameter as  params: Annotated[ListCreaturesRequest, Query()]
#   (open /docs: FastAPI still shows three separate query parameters).
#   Any ValueError (bad filter, bad token, negative size) -> 400 Bad Request.
def list_creatures():
    raise NotImplementedError("TODO E1")
