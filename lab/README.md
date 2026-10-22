# Lab — Building APIs with FastAPI

Hands-on, auto-graded exercises for the *Introduction to API* course (Master 2 MoSEF Data Science,
Université Paris 1 Panthéon-Sorbonne). They follow the slides and two books:

- **[FA]** Bill Lubanovic, *FastAPI: Modern Python Web Development*, O'Reilly, 2023
- **[ADP]** JJ Geewax, *API Design Patterns*, Manning, 2021

Each lab is a folder with an `exercise.py` full of `TODO`s and a `test_*.py` file that grades it.
A lab is done when all its tests pass.

**Stack:** Python ≥ 3.12 · FastAPI ≥ 0.159 · Pydantic 2.14 · Starlette 1.x · httpx2 · pytest 9 · ruff.

## Setup

Install [uv](https://docs.astral.sh/uv/), then from the repository root:

```bash
uv sync                                              # creates .venv with FastAPI, Pydantic, httpx2, pytest, ruff
uv run pytest lab/lab00_python_warmup -v             # run one lab
uv run pytest lab -x                                 # run every lab, stop at the first failure
uv run pytest lab/lab03_resource_oriented -k patch   # only the tests whose name contains "patch"
```

Labs that build an API can also be run and explored in Swagger UI:

```bash
uv run uvicorn lab.lab01_first_endpoints.exercise:app --reload
# then open http://127.0.0.1:8000/docs  and  http://127.0.0.1:8000/openapi.json
```

Before you hand in your work, lint and format it the way the reference code is:

```bash
uv run ruff check lab && uv run ruff format lab
```

## The labs

| # | Lab | What you build | Slides | Books |
|---|-----|----------------|--------|-------|
| 00 | `lab00_python_warmup` | type hints and generic functions, generators, `async`/`await`, `TaskGroup`, choosing processes vs threads vs async | Types of concurrency | FA ch. 2, 4 |
| 01 | `lab01_first_endpoints` | GET/POST endpoints, **path / query / header / body** parameters with `Annotated`, status codes, typed responses, OpenAPI | API Endpoints, API Parameters, Status code, OpenAPI | FA ch. 3 |
| 02 | `lab02_pydantic_models` | `Field` constraints, field and model validators, `default_factory`, input vs output models, **forbidding unknown fields** | Body, Pydantics | FA ch. 5 · ADP ch. 5 |
| 03 | `lab03_resource_oriented` | the RPC flight-booking API turned into **one resource × five standard methods**, Crockford Base32 ids, `201` + `Location`, PATCH that rejects `null` | What are resource-oriented APIs? | ADP ch. 1, 3, 6, 7 · FA ch. 8 |
| 04 | `lab04_layers_and_dependencies` | web → service → data layers on SQLite, `Depends`, **exception handlers**, aggregation in SQL, dependency overrides in tests, SQL injection | — | FA ch. 6, 8, 9, 10, 12 |
| 05 | `lab05_pagination_filtering` | opaque **page tokens**, `max_page_size`, a small filter language, a **query-parameter model** | — | ADP ch. 21, 22 |
| 06 | `lab06_updates_custom_methods` | PATCH with **field masks**, partial GET, custom methods `POST /x/{id}:verb`, **soft delete** | HTTP methods | ADP ch. 8, 9, 25 |
| 07 | `lab07_jwt_auth` | **JWT HS256 built by hand**, password hashing, timing-safe login, bearer-token dependency, 401 vs 403, middleware | JSON Web Token | FA ch. 11 · ADP ch. 30 |
| 08 | `lab08_external_api_and_model` | a deterministic **ML model** served one by one, in batch and **streamed as JSON Lines**; an **async call to the World Bank API** through a client shared by the `lifespan` (mocked in tests), 502/504 | Body (predict), Why build a web API? | FA ch. 4, 12, 14 · ADP ch. 18 |
| 09 | `lab09_reliability` | **request deduplication** (`request_id` + fingerprint), `validate_only`, client retries with exponential backoff, jitter and `Retry-After` | Status code | ADP ch. 26, 27, 29 |

Labs 00–03 cover the core of the course and labs 04–09 go further. Labs 07 and 08 are the building blocks
of the final project.

## Recent FastAPI features used in the labs

FastAPI moved from 0.117 to 0.159 during 2025–2026. These changes matter for the code you write here:

| Version | Change | Where |
|---------|--------|-------|
| 0.115 / 0.157 | Query parameters can be grouped in a Pydantic model, combined with other parameters, and `extra="forbid"` rejects unknown ones | lab 05 |
| 0.121 | Dependencies with `yield` accept `scope="request"` to clean up before the response is sent | (read the docs) |
| 0.122 | `HTTPBearer` and the other security classes answer **401** (not 403) when credentials are missing | lab 07 |
| 0.128 | `pydantic.v1` is no longer supported: Pydantic 2 only | all |
| 0.130 | Responses are serialised by Pydantic in Rust **when the return type is declared**: annotate your endpoints | all |
| 0.132 | JSON bodies must come with a JSON `Content-Type` header (CSRF protection), otherwise 422 | lab 01 |
| 0.134 / 0.135 | `yield` in an endpoint streams **JSON Lines**; Server-Sent Events are supported too | lab 08 |
| 0.137 | Routers are no longer copied by `include_router`: routes added afterwards still work | lab 04 |
| 0.151 | In a JSON body, an explicit `null` and an omitted value are now different things | lab 03 |
| Starlette 1.x | The `TestClient` runs on **httpx2**, the maintained successor of httpx (httpx is deprecated there) | labs 08, 09 |

Full list: <https://fastapi.tiangolo.com/release-notes/>.

## Tips

- Read the module docstring and every `TODO` before coding. The tests also document the expected behaviour.
- `raise NotImplementedError("TODO …")` marks code you have to write. An endpoint is only exposed once
  you add its decorator, e.g. `@app.get("/hi")`.
- Declare parameters with `Annotated` (`limit: Annotated[int, Query(le=100)] = 10`) and declare the return
  type of every endpoint: FastAPI uses it to validate, filter, document and serialise the response.
- A `422` means FastAPI/Pydantic rejected the input before your code ran. A `500` means your code raised an
  exception you didn't handle.
- Some `TODO`s end with a question ("why 502 and not 500?"). Answer it in a comment, because it may come up
  in the oral exam.

## Final project (from the "Coding time" slide)

Create **your own repository** with a FastAPI API that has a modular, maintainable structure (layers as in lab 04):

1. **POST & GET** endpoints to submit and retrieve data (labs 01–03).
2. A **`/health`** endpoint for monitoring (lab 01).
3. A **call to an external API** with `httpx2` (or `requests`), with errors handled (lab 08).
4. A **JWT generator endpoint** and token checking on the secured routes (lab 07).
5. A **small, even deterministic, ML model** served by an endpoint (lab 08).

Bonus points: tests with `pytest` + `TestClient`, pagination (lab 05), field masks or soft delete (lab 06),
deduplication of POST requests (lab 09), a streaming endpoint (lab 08), a clean OpenAPI page (titles,
descriptions, response models), code that passes `ruff check`.

## For teachers

The reference solutions live in `lab/_solutions/` and answer the questions asked in the `TODO`s in comments.
To check that they pass every test:

```bash
LAB_SOLUTION=1 uv run pytest lab
```

To publish the exercises without the answers, delete `lab/_solutions/` from the students' branch, or
add it to `.gitignore`.
