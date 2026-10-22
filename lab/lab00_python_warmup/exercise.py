"""Lab 00 — Python warm-up: type hints, generators, async/await.

Goal
    Refresh the modern Python that FastAPI is built on, before writing any endpoint.

You will learn
    * type hints, including Python 3.12 generic functions (``def f[T](...)``)
    * generators: producing values lazily with ``yield``
    * ``async``/``await``: waiting for I/O without blocking, running coroutines concurrently
    * choosing between async, a thread pool and processes for a given workload

References
    Slides : "Types of concurrency" (processes, threads, async I/O)
    Book   : [FA] ch. 2 (Modern Python), ch. 4 (Async, Concurrency)
    Repo   : api/generators.py and api/async_await_asyncio.py

Check your work
    uv run pytest lab/lab00_python_warmup -v
"""

import asyncio
import time
from collections.abc import Awaitable, Callable, Iterator


# --- Part A: type hints -----------------------------------------------------
def average_mark(marks: list[float]) -> float:
    """TODO A1: return the mean of ``marks`` rounded to 2 decimals.

    Raise ``ValueError`` if the list is empty (never divide by zero!).
    """
    raise NotImplementedError("TODO A1")


# --- Part B: generators -----------------------------------------------------
def countdown(n: int) -> Iterator[int]:
    """TODO B1: *yield* n, n-1, ..., 1 (one value at a time, no list)."""
    raise NotImplementedError("TODO B1")


def chunks[T](items: list[T], size: int) -> Iterator[list[T]]:
    """TODO B2: yield consecutive slices of ``items`` of length ``size``.

    chunks([1, 2, 3, 4, 5], 2) -> [1, 2], [3, 4], [5]
    Raise ``ValueError`` if size <= 0.
    ``[T]`` makes the function generic: chunks of ints are lists of ints.
    (You'll reuse this idea for pagination in lab 05.)
    """
    raise NotImplementedError("TODO B2")


# --- Part C: async / await --------------------------------------------------
async def fake_download(name: str, delay: float) -> str:
    """TODO C1: wait ``delay`` seconds *without blocking* and return
    ``"<name>: done"``. Hint: ``time.sleep`` blocks, ``asyncio.sleep`` doesn't.
    """
    raise NotImplementedError("TODO C1")


async def download_all(jobs: dict[str, float]) -> list[str]:
    """TODO C2: run every ``fake_download(name, delay)`` *concurrently*.

    The total time must be close to max(delays), not sum(delays).
    Keep the results in the same order as ``jobs``.
    Hint: ``asyncio.gather``, or ``asyncio.TaskGroup`` (Python 3.11+), which also
    cancels the other downloads if one of them fails.
    """
    raise NotImplementedError("TODO C2")


def timed[T](coro_factory: Callable[[], Awaitable[T]]) -> tuple[T, float]:
    """Given (helper): run ``coro_factory()`` and return (result, seconds)."""

    async def main() -> T:
        return await coro_factory()

    start = time.perf_counter()
    result = asyncio.run(main())
    return result, time.perf_counter() - start


# --- Part D: pick the right concurrency tool --------------------------------
# TODO D1: for each workload, choose "async", "threadpool" or "processes"
# (see the "Conclusion" slide of the concurrency section).
CONCURRENCY_CHOICE = {
    "call 50 external weather APIs and combine the answers": "TODO",
    "train a random forest on 10 million rows": "TODO",
    "read a file with a legacy library that has no async version": "TODO",
    "resize 10,000 images on an 8-core laptop": "TODO",
    "serve thousands of clients that each wait on a database": "TODO",
}
