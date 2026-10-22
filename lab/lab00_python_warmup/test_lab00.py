import inspect

import pytest

from lab._loader import load

ex = load("lab00_python_warmup")


def test_average_mark():
    assert ex.average_mark([10, 12, 14]) == 12
    assert ex.average_mark([12.5, 13.25]) == 12.88


def test_average_mark_empty():
    with pytest.raises(ValueError):
        ex.average_mark([])


def test_countdown_is_a_generator():
    assert inspect.isgeneratorfunction(ex.countdown), "use `yield`, not a list"
    assert list(ex.countdown(3)) == [3, 2, 1]
    assert list(ex.countdown(0)) == []


def test_chunks():
    assert inspect.isgeneratorfunction(ex.chunks)
    assert list(ex.chunks([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(ex.chunks([], 3)) == []
    with pytest.raises(ValueError):
        list(ex.chunks([1], 0))


def test_fake_download():
    result, elapsed = ex.timed(lambda: ex.fake_download("a", 0.1))
    assert result == "a: done"
    assert elapsed >= 0.09


def test_download_all_is_concurrent():
    jobs = {"slides.pdf": 0.3, "dataset.csv": 0.3, "model.pkl": 0.3}
    result, elapsed = ex.timed(lambda: ex.download_all(jobs))
    assert result == ["slides.pdf: done", "dataset.csv: done", "model.pkl: done"]
    assert elapsed < 0.6, f"took {elapsed:.2f}s: the downloads ran one after another"


def test_concurrency_choices():
    allowed = {"async", "threadpool", "processes"}
    assert set(ex.CONCURRENCY_CHOICE.values()) <= allowed, "use only " + str(allowed)
    wrong = [k for k, v in ex.CONCURRENCY_CHOICE.items() if v != _ANSWERS[k]]
    assert not wrong, f"re-think: {wrong}"


_ANSWERS = {
    "call 50 external weather APIs and combine the answers": "async",
    "train a random forest on 10 million rows": "processes",
    "read a file with a legacy library that has no async version": "threadpool",
    "resize 10,000 images on an 8-core laptop": "processes",
    "serve thousands of clients that each wait on a database": "async",
}
