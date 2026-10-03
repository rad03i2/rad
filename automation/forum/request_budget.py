"""Bound external requests across a whole publication attempt."""
from contextlib import contextmanager
from contextvars import ContextVar
import time

_deadline = ContextVar("publication_request_deadline", default=None)


class RequestBudgetExceeded(TimeoutError):
    pass


@contextmanager
def bounded_requests(seconds: float):
    current = _deadline.get()
    deadline = time.monotonic() + seconds
    token = _deadline.set(min(current, deadline) if current is not None else deadline)
    try:
        yield
    finally:
        _deadline.reset(token)


def request_timeout(default: float) -> float:
    deadline = _deadline.get()
    if deadline is None:
        return default
    remaining = deadline - time.monotonic()
    if remaining < 1:
        raise RequestBudgetExceeded("Publication request budget exhausted; retry in a later cycle")
    return min(default, remaining)
