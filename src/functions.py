from functools import wraps
from time import time
from types import NoneType, UnionType
from typing import Any

from beartype import beartype

from src.stuff import app


def cached_func_static(func):
    last_called = 0
    last_result = ...

    @wraps(func)
    def wrapper(**kwargs):
        nonlocal last_called, last_result
        if app.db_last_modified >= last_called:
            res = func(**kwargs)
            last_result = res
        else:
            res = last_result

        last_called = time()
        return res

    return wrapper


def cached_property(func):
    """
    Cache the return value of a property for the lifetime of the object, update only if the DB is modified.

    Args:

    Returns:
        Any: the cached return value of the property
    """
    last_called = 0
    last_results = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        nonlocal last_called, last_results
        if app.db_last_modified >= last_called or self not in last_results:
            res = func(*args, **kwargs)
            last_results[self] = res
        else:
            res = last_results[self]

        last_called = time()
        return res

    return property(wrapper)


def cached_getter(func):
    """
    Cache a single value for a single argument. Ignore kwargs.

    Args:
        func (callable): a module-level function

    Returns:
        Any: the cached return value of the function for the given argument
    """
    last_called = 0
    last_results = {}

    @wraps(func)
    def wrapper(arg, **kwargs):
        nonlocal last_called, last_results
        if app.db_last_modified >= last_called or arg not in last_results:
            res = func(arg, **kwargs)
            last_results[arg] = res
        else:
            res = last_results[arg]

        last_called = time()
        return res

    return wrapper


@beartype
def typed(thing, kind, default=...):
    if isinstance(thing, kind):
        return thing
    elif default is not ...:
        return default
    else:
        raise ValueError(f"Expected {kind} but got {type(thing)}")


@beartype
def typed_row(
    row: tuple | NoneType,
    idx: int,
    kind: type | UnionType | tuple[type, ...],  # sic. for beartype to work, it needs to be a meta-union
    default: Any = ...,
    debugging=False,
):
    if debugging and row is None:
        breakpoint()

    if row is None and default is not ...:
        return default

    res = row[idx] if isinstance(row, tuple) else row
    if isinstance(res, kind):
        return res
    if res is None and default is not None:
        return default

    raise ValueError(f"Expected {kind} ({res}) but got {type(res)} ({row})")
