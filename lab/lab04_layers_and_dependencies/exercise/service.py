"""Service layer: business rules — no HTTP, no SQL.

[FA] ch. 9. This layer would stay identical if we replaced FastAPI by a
CLI, or sqlite by PostgreSQL. Business rules for this lab:
  * names are stored stripped and lower-case ("  Yeti " -> "yeti")
  * countries are stored upper-case ("cn" -> "CN")
  * lookups are case-insensitive (GET /creature/YETI finds "yeti")
"""

import sqlite3

from . import data
from .model import Creature


def _normalise(creature: Creature) -> Creature:
    """TODO S1: return a *copy* with the name and country normalised."""
    raise NotImplementedError("TODO S1")


def get_one(conn: sqlite3.Connection, name: str) -> Creature:
    """Given."""
    return data.get_one(conn, name.strip().lower())


def get_all(conn: sqlite3.Connection, skip: int = 0, limit: int = 100) -> list[Creature]:
    """TODO S2"""
    raise NotImplementedError("TODO S2")


def create(conn: sqlite3.Connection, creature: Creature) -> Creature:
    """TODO S3: normalise, then store."""
    raise NotImplementedError("TODO S3")


def replace(conn: sqlite3.Connection, name: str, creature: Creature) -> Creature:
    """TODO S4"""
    raise NotImplementedError("TODO S4")


def delete(conn: sqlite3.Connection, name: str) -> None:
    """TODO S5"""
    raise NotImplementedError("TODO S5")


def count_by_country(conn: sqlite3.Connection) -> dict[str, int]:
    """TODO S6: {"CN": 1, "US": 2, ...} — a tiny analytics feature (see data.count_by_country)."""
    raise NotImplementedError("TODO S6")
