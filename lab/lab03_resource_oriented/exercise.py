"""Lab 03 — From RPC to a resource-oriented API (the flight-booking example).

Goal
    Replace six ad-hoc RPC methods by ONE resource and the five standard methods.

You will learn
    * naming standard methods and mapping them to HTTP verbs and URLs
    * good resource identifiers: unique, opaque, URL-safe, readable (Crockford Base32)
    * the right status codes: 201 + ``Location``, 204, 404, 409, 422
    * PATCH semantics: change only what is sent, and never accept ``null`` for a required field

References
    Slides : "What are resource-oriented APIs?" (the 3 flight-booking slides),
             "FastAPI uses HTTP request methods", "Status code"
    Books  : [ADP] ch. 1 (resource-oriented APIs), ch. 3 (Naming), ch. 6 (Resource identification),
             ch. 7 (Standard methods) ; [FA] ch. 8 (Web layer)
    Docs   : https://fastapi.tiangolo.com/tutorial/body-updates/

Run it
    uv run uvicorn lab.lab03_resource_oriented.exercise:app --reload

Check your work
    uv run pytest lab/lab03_resource_oriented -v
"""

import datetime as dt
import secrets  # noqa: F401
from typing import Literal

from fastapi import FastAPI, HTTPException, Response, status  # noqa: F401
from pydantic import BaseModel, Field, field_validator  # noqa: F401

# --- Part A: from RPC to resources -----------------------------------------
STANDARD_METHODS = ("create", "get", "list", "update", "delete")


def pluralize(word: str) -> str:
    """Given: naive English plural (Reservation -> Reservations, Category -> Categories)."""
    if word.endswith("y") and word[-2:-1].lower() not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "ch", "sh")):
        return word + "es"
    return word + "s"


def standard_method_name(method: str, resource: str) -> str:
    """TODO A1: build the name of a standard method: <StandardMethod><Resource>.

    standard_method_name("get", "FlightReservation")  -> "GetFlightReservation"
    standard_method_name("list", "FlightReservation") -> "ListFlightReservations"  (plural!)
    Raise ValueError for anything not in STANDARD_METHODS (case-insensitive).
    """
    raise NotImplementedError("TODO A1")


def http_route(method: str, collection: str) -> tuple[str, str]:
    """TODO A2: map a standard method to its HTTP verb and URL (Geewax ch. 7).

    http_route("create", "flightReservations") -> ("POST", "/flightReservations")
    http_route("get", "flightReservations")    -> ("GET", "/flightReservations/{id}")
    list -> GET on the collection, update -> PATCH on an item, delete -> DELETE on an item.
    Raise ValueError for an unknown method.
    """
    raise NotImplementedError("TODO A2")


# TODO A3: the slides list 6 RPC methods. Which standard method replaces each?
#   (two of them become the *same* standard method — which ones, and why?)
RPC_TO_STANDARD = {
    "ScheduleFlight": "TODO",
    "GetFlightDetails": "TODO",
    "ShowAllBookings": "TODO",
    "CancelReservation": "TODO",
    "RescheduleFlight": "TODO",
    "UpgradeTrip": "TODO",
}

# --- Part B: identifiers ----------------------------------------------------
# Geewax ch. 6: ids should be unique, opaque, URL-safe and easy to read aloud.
# Crockford's Base32 drops the confusing letters i, l, o and u.
CROCKFORD = "0123456789abcdefghjkmnpqrstvwxyz"


def new_id(length: int = 12) -> str:
    """TODO B1: random id of ``length`` chars from CROCKFORD.

    Use the ``secrets`` module (cryptographically random), not ``random``.
    """
    raise NotImplementedError("TODO B1")


# --- Part C: the resource-oriented API --------------------------------------
Cabin = Literal["economy", "business", "first"]


class FlightReservationCreate(BaseModel):
    """What the client sends. Note: no id — the *server* chooses it."""

    passenger: str = Field(min_length=1)
    flight_number: str = Field(pattern=r"^[A-Z]{2}\d{1,4}$")
    date: dt.date
    cabin: Cabin = "economy"


class FlightReservation(FlightReservationCreate):
    id: str


class FlightReservationUpdate(BaseModel):
    """Every field optional: PATCH only changes what is sent.

    TODO C0: ``{"date": null}`` is accepted today and stores a reservation without a
    date! In JSON an explicit ``null`` and an omitted field are two different things
    (Pydantic tracks it in ``model_fields_set``; FastAPI >= 0.151 does it for ``Body``
    parameters too): omitted -> keep the current value, null -> "set it to None".
    None is not a valid value for any of these fields, so reject it (-> 422) with a
    ``@field_validator("*")`` that raises ValueError when the value is None.
    It only runs on values the client sent: defaults are never validated.
    """

    passenger: str | None = Field(default=None, min_length=1)
    flight_number: str | None = Field(default=None, pattern=r"^[A-Z]{2}\d{1,4}$")
    date: dt.date | None = None
    cabin: Cabin | None = None


RESERVATIONS: dict[str, FlightReservation] = {}

app = FastAPI(title="Flight reservations")
COLLECTION = "/flightReservations"


# TODO C1: POST /flightReservations  -> 201 + the stored reservation (with a new_id()).
#          Also send the header  Location: /flightReservations/<id>  (the URL of the new
#          resource, RFC 9110): add a ``response: Response`` parameter and set response.headers.
#          If the same passenger already booked the same flight on the same date
#          -> 409 Conflict.
def create_flight_reservation():
    raise NotImplementedError("TODO C1")


# TODO C2: GET /flightReservations/{reservation_id}  -> the reservation, or 404.
def get_flight_reservation():
    raise NotImplementedError("TODO C2")


# TODO C3: GET /flightReservations  -> {"results": [ ...all reservations... ]}
def list_flight_reservations():
    raise NotImplementedError("TODO C3")


# TODO C4: PATCH /flightReservations/{reservation_id}
#          Only the fields present in the body change (hint:
#          body.model_dump(exclude_unset=True) and model_copy(update=...)).
#          "RescheduleFlight" = PATCH {"date": ...}; "UpgradeTrip" = PATCH {"cabin": "first"}.
#          404 if it does not exist.
def update_flight_reservation():
    raise NotImplementedError("TODO C4")


# TODO C5: DELETE /flightReservations/{reservation_id}  -> 204 No Content, or 404.
#          Hint: status_code=204 on the decorator and ``-> None``: FastAPI sends no body.
def delete_flight_reservation():
    raise NotImplementedError("TODO C5")
