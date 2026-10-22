class Missing(Exception):
    """The resource does not exist (-> 404)."""


class Duplicate(Exception):
    """The resource already exists (-> 409)."""
