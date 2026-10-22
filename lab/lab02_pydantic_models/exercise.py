"""Lab 02 — Pydantic models: validation, defaults, input vs output models.

Goal
    Let Pydantic reject bad data at the door, so the rest of the code can trust its inputs.

You will learn
    * ``Field`` constraints (bounds, lengths, regex patterns) and ``default_factory``
    * field validators (normalise one value) and model validators (check several fields)
    * cleaning a batch of rows without letting one bad row crash everything
    * separate input and output models, so secrets never leave the API
    * forbidding unknown fields to block "mass assignment" attacks

References
    Slides : "API Parameters: Body", "Pydantics"
    Books  : [FA] ch. 5 (Pydantic, Type Hints, and Models) ; [ADP] ch. 5 (Data types and defaults)
    Docs   : https://docs.pydantic.dev/latest/concepts/validators/
    Repo   : data_models/model.py and data_models/data_error.py

Check your work
    uv run pytest lab/lab02_pydantic_models -v
"""

from datetime import date

from fastapi import FastAPI, status  # noqa: F401
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator  # noqa: F401

LEVELS = {"L3", "M1", "M2"}


# TODO 1: add constraints with Field(...) so that
#   - id is strictly positive
#   - last_validate_level has exactly 2 characters
#   - last_average_mark is between 0 and 20 (a mark out of 20)
#   - dedicated_hours is >= 0
# TODO 2: add a @field_validator on last_validate_level that upper-cases it
#   ("m1" -> "M1") and raises ValueError if it is not in LEVELS.
class StudentRecord(BaseModel):
    id: int
    last_validate_level: str
    last_average_mark: float
    dedicated_hours: int


# TODO 3: improve the Creature from the repo:
#   - name: at least 2 characters
#   - country: two upper-case letters ("CN") or "*"   (hint: Field(pattern=...))
#   - aka: optional, default None  (Geewax ch. 5: "missing" vs "null")
#   - tags: a list of strings defaulting to an empty list.
#     Careful: never write `tags: list[str] = []` in plain Python classes;
#     use Field(default_factory=list) to make the intent explicit.
class Creature(BaseModel):
    name: str
    country: str
    area: str
    description: str
    aka: str


# TODO 4: cross-field validation. A Booking whose ``end`` is not strictly
#   after ``start`` must fail. Hint: @model_validator(mode="after").
class Booking(BaseModel):
    guest: str
    start: date
    end: date


# TODO 5: the password must have at least 8 characters, and any field that is not
#   declared must be REJECTED (422) instead of silently ignored:
#   model_config = ConfigDict(extra="forbid")
#   Why? Imagine a client sending {"username": "eve", "password": "...", "admin": true}
#   to an API that one day adds an ``admin`` field to UserIn ("mass assignment").
class UserIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    username: str


def parse_students(rows: list[dict]) -> tuple[list[StudentRecord], list[int]]:
    """TODO 6: data-science style cleaning.

    Return (valid_records, indices_of_invalid_rows). Catch ValidationError,
    don't let one bad row crash the whole batch.
    """
    raise NotImplementedError("TODO 6")


app = FastAPI()


# TODO 7: POST /students  -> validate the body as StudentRecord, return it, 201.
def create_student():
    raise NotImplementedError("TODO 7")


# TODO 8: POST /users  takes a UserIn but must *never* send the password back.
#   Use response_model=UserOut ([FA] ch. 5 and 8): FastAPI filters the returned
#   object through UserOut, whatever your function returns. Status 201.
def create_user():
    raise NotImplementedError("TODO 8")
