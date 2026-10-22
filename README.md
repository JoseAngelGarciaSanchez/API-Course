# API-Course

Course material for **Introduction to APIs with FastAPI**, Master 2 MoSEF Data Science
(Université Paris 1 Panthéon-Sorbonne): slides, live-coding examples and auto-graded labs.

## What's inside

| Path | Content |
|------|---------|
| [`slides/api_slides.pdf`](slides/api_slides.pdf) | Course slides |
| [`api/`](api/) | Live-coding examples from class: a first FastAPI app, generators, `async`/`await` |
| [`data_models/`](data_models/) | Pydantic models and fake data used by `api/main.py` |
| [`lab/`](lab/README.md) | 10 hands-on labs, each graded by its own pytest tests |

## Setup

Install [uv](https://docs.astral.sh/uv/) (Python ≥ 3.12), then from the repository root:

```bash
uv sync
```

This creates `.venv` with FastAPI, Pydantic, Uvicorn, httpx2, pytest and ruff.

## Run the example API

```bash
uv run uvicorn api.main:app --reload
```

Then open <http://127.0.0.1:8000/docs> to try the endpoints in Swagger UI.

## Labs

Each lab has an `exercise.py` full of `TODO`s and a `test_*.py` that grades it. A lab is done when all its tests pass:

```bash
uv run pytest lab/lab00_python_warmup -v   # one lab
uv run pytest lab -x                       # every lab, stop at the first failure
```

| # | Topic |
|---|-------|
| 00 | Python warm-up: type hints, generators, `async`/`await` |
| 01 | First endpoints: path, query, header and body parameters |
| 02 | Pydantic models and validation |
| 03 | Resource-oriented design: standard methods |
| 04 | Layers (web → service → data) and dependencies |
| 05 | Pagination and filtering |
| 06 | PATCH with field masks, custom methods, soft delete |
| 07 | JWT authentication |
| 08 | Calling an external API and serving an ML model |
| 09 | Reliability: deduplication, retries, backoff |

Full instructions, tips and the final project brief are in [`lab/README.md`](lab/README.md).

## References

- Bill Lubanovic, *FastAPI: Modern Python Web Development*, O'Reilly, 2023
- JJ Geewax, *API Design Patterns*, Manning, 2021
- [FastAPI documentation](https://fastapi.tiangolo.com/)

## License

Public domain ([Unlicense](LICENSE)).
