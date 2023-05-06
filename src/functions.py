from time import time
from functools import wraps

from src.stuff import app, config, db


def cached_func_noarg(func):
    last_called = 0
    last_result = ...

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_called, last_result
        if app.db_last_modified >= last_called:
            res = func(*args, **kwargs)
            last_result = res
        else:
            res = last_result

        last_called = time()
        return res

    return wrapper


def cached_func_single_arg(func):
    last_called = 0
    last_result = ...

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_called, last_result
        if app.db_last_modified >= last_called:
            res = func(*args, **kwargs)
            last_result = res
        else:
            res = last_result

        last_called = time()
        return res

    return wrapper


def cached_property(func):
    last_called = 0
    last_results = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        nonlocal last_called, last_results
        # print(3223, last_results)
        if app.db_last_modified >= last_called or self not in last_results:
            res = func(*args, **kwargs)
            last_results[self] = res
        else:
            res = last_results[self]

        last_called = time()
        return res

    return property(wrapper)


def cached_getter(func):
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

    return wrapper


def typed(thing, kind, default=...):
    if isinstance(thing, kind):
        return thing
    elif default is not ...:
        return default
    else:
        raise ValueError(f"Expected {kind} but got {type(thing)}")


def typed_row(row: tuple, idx: int, kind: type, default=..., debugging=False):
    if debugging and row is None:
        breakpoint()

    if row is None and default is not ...:
        return default

    res = row[idx] if isinstance(row, tuple) else row
    if isinstance(res, kind):
        return res
    if res is None and default is not None:
        return default

    raise ValueError(f"Expected {kind} but got {type(res)}")
