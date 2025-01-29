import ast
import inspect
from functools import wraps
from itertools import takewhile
from textwrap import dedent
from time import time
from types import NoneType, UnionType
from typing import Any, Callable

from beartype import beartype

from src.main import app


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


class _PipeTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if not isinstance(node.op, (ast.LShift, ast.RShift)):
            return node
        if not isinstance(node.right, ast.Call):
            return self.visit(
                ast.Call(
                    func=node.right,
                    args=[node.left],
                    keywords=[],
                    starargs=None,
                    kwargs=None,
                    lineno=node.right.lineno,
                    col_offset=node.right.col_offset,
                )
            )
        node.right.args.insert(
            0 if isinstance(node.op, ast.RShift) else len(node.right.args), node.left
        )
        return self.visit(node.right)


def pipes(func_or_class):
    if inspect.isclass(func_or_class):
        decorator_frame = inspect.stack()[1]
        ctx = decorator_frame[0].f_locals
        first_line_number = decorator_frame[2]
    else:
        ctx = func_or_class.__globals__
        first_line_number = func_or_class.__code__.co_firstlineno
    source = inspect.getsource(func_or_class)
    tree = ast.parse(dedent(source))
    ast.increment_lineno(tree, first_line_number - 1)
    source_indent = sum(1 for _ in takewhile(str.isspace, source)) + 1
    for node in ast.walk(tree):
        if hasattr(node, "col_offset"):
            node.col_offset += source_indent
    tree.body[0].decorator_list = [
        d
        for d in tree.body[0].decorator_list
        if isinstance(d, ast.Call)
        and d.func.id != "pipes"
        or isinstance(d, ast.Name)
        and d.id != "pipes"
    ]
    tree = _PipeTransformer().visit(tree)
    code = compile(
        tree, filename=(ctx["__file__"] if "__file__" in ctx else "repl"), mode="exec"
    )
    exec(code, ctx)
    return ctx[tree.body[0].name]