"""Lab 01 — Your first endpoints: path, query, header and body parameters.

Goal
    Build a small "annuaire" (student directory) API and explore it in Swagger UI.

You will learn
    * declaring GET/POST path operations and choosing their status codes
    * the four places a parameter can come from: path, query, header, body
    * the ``Annotated[type, Query()/Path()/Header()]`` style recommended by FastAPI
    * how FastAPI turns type hints into validation (422) and into the OpenAPI schema

References
    Slides : "API Endpoints", "API Parameters: Path / Query / Header / Body",
             "Status code", "OpenAPI", "Swagger UI"
    Book   : [FA] ch. 3 (FastAPI Tour)
    Docs   : https://fastapi.tiangolo.com/tutorial/query-params-str-validations/

Run it
    uv run uvicorn lab.lab01_first_endpoints.exercise:app --reload
    # open http://127.0.0.1:8000/docs

Check your work
    uv run pytest lab/lab01_first_endpoints -v
"""

from typing import Annotated  # noqa: F401

from fastapi import FastAPI, Header, HTTPException, Path, Query, status  # noqa: F401
from pydantic import BaseModel

# TODO 0: give the API the title "Student Directory" (it shows up in /docs and
#         in /openapi.json -> info.title).
app = FastAPI()


class Student(BaseModel):
    name: str
    year: int
    domain: str


ANNUAIRE: list[dict] = [
    {"name": "Lea", "year": 2024, "domain": "health"},
    {"name": "Axel", "year": 2024, "domain": "finance"},
    {"name": "Ines", "year": 2025, "domain": "health"},
    {"name": "Hugo", "year": 2025, "domain": "energy"},
]


# TODO 1: GET /hi  -> returns the JSON string "hi"
def say_hi():
    raise NotImplementedError("TODO 1")


# TODO 2: GET /health  -> {"status": "ok"}
#         (a "health check" endpoint is what monitoring tools and load balancers ping)
def health_check():
    raise NotImplementedError("TODO 2")


# TODO 3: GET /annuaire  -> {"annuaire": [...all students...]}
#         Optional *query* parameter ``domain``:
#         GET /annuaire?domain=health -> only the health students
#         Declare the return type (-> dict[str, list[Student]]): FastAPI uses it to
#         validate, document and serialise the response.
def list_students():
    raise NotImplementedError("TODO 3")


# TODO 4: GET /annuaire/{year}  (*path* parameter, an int)
#         -> {"annuaire": [students of that year]}
#         -> 404 Not Found if nobody matches (raise HTTPException)
#         What happens if you call /annuaire/abc ? Which status code, why?
def students_by_year():
    raise NotImplementedError("TODO 4")


# TODO 5: GET /whoami  reads the *header* ``X-Client-Name``
#         -> {"client": "<value>"} or {"client": "anonymous"} if missing.
#         Hint: x_client_name: Annotated[str, Header()] = "anonymous"
#         maps to the header X-Client-Name (underscores become dashes).
def whoami():
    raise NotImplementedError("TODO 5")


# TODO 6: POST /annuaire  with a JSON *body* matching ``Student``
#         -> append it to ANNUAIRE, return it with status 201 Created.
#         Sending {"name": "Zoe"} only must give 422. Why?
#         Sending a valid JSON body WITHOUT the header Content-Type: application/json
#         also gives 422 (FastAPI >= 0.132 checks it). Why is that safer?
def add_student():
    raise NotImplementedError("TODO 6")
