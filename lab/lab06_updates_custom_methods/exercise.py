"""Lab 06 — Partial updates, partial retrievals, custom methods, soft deletion.

Goal
    Go beyond the five standard methods on a cryptid resource with nested fields.

Key ideas
    * PATCH + field mask: the client says exactly which fields it wants to change.
      Without a mask, the mask is *implicit*: every leaf field present in the body.
      A field listed in the mask but absent from the body is reset to its default.
    * Partial GET: ?fields=name,location.area returns only those fields.
    * Custom methods (anything that is not Create/Get/List/Update/Delete) are
      POST on  /collection/{id}:verb   — e.g.  POST /creatures/yeti:reportSighting
    * Soft delete: DELETE only flags the resource; :undelete restores it,
      :expunge removes it for good. Wrong state -> 412 Precondition Failed.

References
    Books : [ADP] ch. 8 (Partial updates and retrievals), ch. 9 (Custom methods),
            ch. 25 (Soft deletion) ; [FA] ch. 8 (Web layer)

Run it
    uv run uvicorn lab.lab06_updates_custom_methods.exercise:app --reload

Check your work
    uv run pytest lab/lab06_updates_custom_methods -v
"""

import copy  # noqa: F401
from datetime import UTC, datetime  # noqa: F401
from typing import Annotated, Any  # noqa: F401

from fastapi import Body, FastAPI, HTTPException, status  # noqa: F401

OUTPUT_ONLY = {"id", "deleted", "sightings", "last_seen"}
# fmt: off
TEMPLATE = {"id": None, "name": None, "aka": None, "location": {"country": None, "area": None},
            "sightings": 0, "last_seen": None, "deleted": False}


def seed() -> dict[str, dict]:
    return {
        "yeti": {"id": "yeti", "name": "Yeti", "aka": "Abominable Snowman",
                 "location": {"country": "CN", "area": "Himalayas"},
                 "sightings": 0, "last_seen": None, "deleted": False},
        "nessie": {"id": "nessie", "name": "Loch Ness Monster", "aka": "Nessie",
                   "location": {"country": "GB", "area": "Loch Ness"},
                   "sightings": 0, "last_seen": None, "deleted": False},
    }
# fmt: on


DB: dict[str, dict] = seed()


# --- Part A: field masks ----------------------------------------------------
def leaf_paths(d: dict, prefix: str = "") -> list[str]:
    """TODO A1: every "dotted" path to a non-dict value.

    {"name": "x", "location": {"area": "y"}} -> ["name", "location.area"]
    Hint: recursion, passing prefix + "." down.
    """
    raise NotImplementedError("TODO A1")


def _lookup(d: dict, path: str) -> tuple[bool, Any]:
    node: Any = d
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def _set(d: dict, path: str, value: Any) -> None:
    *parents, last = path.split(".")
    for part in parents:
        d = d.setdefault(part, {})
    d[last] = value


def _is_valid_path(path: str) -> bool:
    return _lookup(TEMPLATE, path)[0]


def apply_field_mask(resource: dict, patch: dict, mask: list[str] | None = None) -> dict:
    """TODO A2: return an UPDATED COPY of ``resource`` (never mutate the input).

    1. if mask is None, use the implicit mask: leaf_paths(patch)
    2. raise ValueError if a path starts with an OUTPUT_ONLY field or is not
       a valid path (use _is_valid_path)
    3. for each path: present in patch -> copy its value; absent -> reset to the
       default found in TEMPLATE.
    Use _lookup / _set and copy.deepcopy."""
    raise NotImplementedError("TODO A2")


def project(resource: dict, fields: list[str]) -> dict:
    """TODO A3: partial retrieval: keep only ``fields`` (dotted paths).

    project(yeti, ["name", "location.country"]) -> {"name": "Yeti", "location": {"country": "CN"}}
    Unknown path -> ValueError."""
    raise NotImplementedError("TODO A3")


# --- Part B: the API ----------------------------------------------------------
app = FastAPI()


def _get(creature_id: str) -> dict:
    if creature_id not in DB:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"creatures/{creature_id} not found")
    return DB[creature_id]


def _split(csv: str | None) -> list[str] | None:
    return None if csv is None else [p.strip() for p in csv.split(",") if p.strip()]


@app.get("/creatures")
def list_creatures() -> dict:
    """TODO C4: hide soft-deleted creatures, unless ?include_deleted=true."""
    return {"results": list(DB.values())}


@app.get("/creatures/{creature_id}")
def get_creature(creature_id: str, fields: str | None = None) -> dict:
    creature = _get(creature_id)
    # TODO B1: if ?fields=name,location.area is given, return project(...)
    #          instead; a ValueError -> 400.
    return creature


# TODO B2: app.patch("/creatures/{creature_id}")
def update_creature():
    """PATCH /creatures/{creature_id}?update_mask=name,location.area with a JSON dict body.
    Use apply_field_mask; ValueError -> 400; unknown id -> 404 (use _get).
    Hint for the body parameter: patch: Annotated[dict[str, Any], Body()]"""
    raise NotImplementedError("TODO B2")


# TODO B3: app.post("/creatures/{creature_id}:reportSighting")
def report_sighting():
    """custom method. Increment sightings, set last_seen to now (``datetime.now(UTC)``, ISO string).
    404 if unknown, 412 if the creature is soft-deleted."""
    raise NotImplementedError("TODO B3")


# TODO C1: app.delete("/creatures/{creature_id}")
def delete_creature():
    """SOFT delete: set deleted=True and return the resource (200).
    Already deleted -> 412."""
    raise NotImplementedError("TODO C1")


# TODO C2: app.post("/creatures/{creature_id}:undelete")
def undelete_creature():
    """custom method :undelete. Not deleted -> 412."""
    raise NotImplementedError("TODO C2")


# TODO C3: app.post("/creatures/{creature_id}:expunge", status_code=204)
def expunge_creature():
    """custom method :expunge. Really remove it, answer 204 with no body (-> None)."""
    raise NotImplementedError("TODO C3")
