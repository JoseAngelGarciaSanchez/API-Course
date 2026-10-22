"""Data layer: the only place that knows about SQL.

[FA] ch. 10. Rules of the game:
  * always use ``?`` placeholders, NEVER f-strings, to build SQL
    (the tests try a SQL injection on you!)
  * translate database errors into the layer-neutral exceptions of errors.py
  * let the database do the heavy lifting (sorting, paging, aggregating)
"""

import sqlite3

from .errors import Duplicate, Missing  # noqa: F401
from .model import Creature

FIELDS = ("name", "country", "area", "description", "aka")


def init(conn: sqlite3.Connection) -> None:
    """Given."""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS creature(
            name TEXT PRIMARY KEY,
            country TEXT,
            area TEXT,
            description TEXT,
            aka TEXT)"""
    )
    conn.commit()


def _row_to_model(row: tuple) -> Creature:
    return Creature(**dict(zip(FIELDS, row, strict=True)))


def get_one(conn: sqlite3.Connection, name: str) -> Creature:
    """Given — use it as a model for the others."""
    row = conn.execute("SELECT name, country, area, description, aka FROM creature WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise Missing(f"Creature {name} not found")
    return _row_to_model(row)


def get_all(conn: sqlite3.Connection, skip: int = 0, limit: int = 100) -> list[Creature]:
    """TODO D1: all creatures ordered by name, honouring skip (OFFSET) and limit (LIMIT)."""
    raise NotImplementedError("TODO D1")


def create(conn: sqlite3.Connection, creature: Creature) -> Creature:
    """TODO D2: INSERT the creature and commit.

    sqlite raises ``sqlite3.IntegrityError`` when the primary key exists:
    turn it into ``Duplicate``.
    """
    raise NotImplementedError("TODO D2")


def modify(conn: sqlite3.Connection, name: str, creature: Creature) -> Creature:
    """TODO D3: UPDATE every column of the row whose name is ``name``.

    ``cursor.rowcount == 0`` means nothing matched -> raise ``Missing``.
    """
    raise NotImplementedError("TODO D3")


def delete(conn: sqlite3.Connection, name: str) -> None:
    """TODO D4: DELETE the row, raise ``Missing`` if there was none."""
    raise NotImplementedError("TODO D4")


def count_by_country(conn: sqlite3.Connection) -> dict[str, int]:
    """TODO D5: {"CN": 1, "US": 2, ...} computed by SQL (GROUP BY), ordered by country.

    Why not load every creature in Python and count them there?
    """
    raise NotImplementedError("TODO D5")
