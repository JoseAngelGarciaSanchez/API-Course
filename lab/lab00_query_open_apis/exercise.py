"""Lab 00 — Query an open API from Python.

Goal
    Before building APIs, use one. You call JSONPlaceholder, a free fake REST API,
    and learn the verbs, status codes and JSON you will design in the next labs.

You will learn
    * sending GET / POST requests with httpx2 and reading the JSON answer
    * query parameters (``?userId=1``) and path parameters (``/posts/1``)
    * checking the status code: ``404`` is an answer, ``500`` is an error
    * finding other open APIs and reading their documentation

References
    Slides : "Calling APIs from Python" (50)
    Docs   : https://jsonplaceholder.typicode.com/guide/
             https://github.com/public-apis/public-apis (hundreds of free APIs)

Try it by hand first (no code, no key)
    curl https://jsonplaceholder.typicode.com/posts/1
    curl "https://jsonplaceholder.typicode.com/posts?userId=1"

Run your functions against the real API
    uv run python -m lab.lab00_query_open_apis.exercise

Check your work (the tests never touch the network)
    uv run pytest lab/lab00_query_open_apis -v
"""

import httpx2

BASE_URL = "https://jsonplaceholder.typicode.com"


def make_client() -> httpx2.Client:
    """Given (helper): one client, reused by every call, with a timeout."""
    return httpx2.Client(base_url=BASE_URL, timeout=5.0)


# --- Part A: GET a collection and a resource ---------------------------------
def get_posts(client: httpx2.Client) -> list[dict]:
    """TODO A1: GET /posts and return the JSON list.

    Raise on a 4xx/5xx answer: ``response.raise_for_status()``.
    """
    raise NotImplementedError("TODO A1")


def get_post(client: httpx2.Client, post_id: int) -> dict | None:
    """TODO A2: GET /posts/{post_id}. Return the post, or ``None`` if the API says 404.

    Any other error status must still raise.
    """
    raise NotImplementedError("TODO A2")


# --- Part B: query parameters ------------------------------------------------
def posts_by_user(client: httpx2.Client, user_id: int) -> list[dict]:
    """TODO B1: GET /posts?userId={user_id}.

    Pass ``params={"userId": user_id}`` instead of building the URL by hand.
    """
    raise NotImplementedError("TODO B1")


def titles_with_word(client: httpx2.Client, word: str) -> list[str]:
    """TODO B2: titles of all posts whose title contains ``word`` (case-insensitive)."""
    raise NotImplementedError("TODO B2")


# --- Part C: POST ------------------------------------------------------------
def create_post(client: httpx2.Client, user_id: int, title: str, body: str) -> dict:
    """TODO C1: POST /posts with a JSON body {userId, title, body} and return the created post.

    Use ``json=...`` (it sets the JSON Content-Type). JSONPlaceholder answers 201 and
    adds an ``id``, but fakes it: nothing is really saved.
    """
    raise NotImplementedError("TODO C1")


# --- Part D: explore ---------------------------------------------------------
# TODO D1: open https://github.com/public-apis/public-apis, pick ONE API whose Auth
# column is "No", and fill in the three values below (not graded).
MY_API = {
    "name": "TODO",
    "base_url": "TODO",
    "first_request": "TODO",  # e.g. "GET /posts/1"
}
# TODO D2: JSONPlaceholder answers 201 to your POST but a GET of the new id gives 404.
# Why? (answer in a comment, it may come up in the oral exam)


if __name__ == "__main__":
    with make_client() as client:
        print(get_post(client, 1))
        print(len(posts_by_user(client, 1)), "posts for user 1")
        print(create_post(client, 1, "Hello", "My first POST"))
