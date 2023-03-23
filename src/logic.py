import ast
import inspect
from collections import deque
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from functools import singledispatch, update_wrapper
from itertools import takewhile
from math import isinf, sqrt
from textwrap import dedent
from time import time

import numpy as np
import use
from beartype import beartype

from classes import EVERY, ILK, Task2, retrieve_task_by_id, retrieve_tasks

fuzzy = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/fuzzylogic/master/src/fuzzylogic/functions.py"),
    modes=use.recklessness,
)

# fresh tasks have a habit weight of 0.2689414213699951 - HOURS
habit_weight = fuzzy.sigmoid(k=0.0002, L=1, x0=5000)
# neglection weight can trump a fresh habit_weight at 3915, no matter how much time was put in - HOURS
neglection_weight = fuzzy.bounded_sigmoid(0, 5380, inverse=True)


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
        node.right.args.insert(0 if isinstance(node.op, ast.RShift) else len(node.right.args), node.left)
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
        if isinstance(d, ast.Call) and d.func.id != "pipes" or isinstance(d, ast.Name) and d.id != "pipes"
    ]
    tree = _PipeTransformer().visit(tree)
    code = compile(tree, filename=(ctx["__file__"] if "__file__" in ctx else "repl"), mode="exec")
    exec(code, ctx)
    return ctx[tree.body[0].name]


def weight(time_spent, last_checked, now) -> float:
    return min(
        habit_weight(time_spent / (60 * 60)),
        neglection_weight((now - last_checked) / (60 * 60)),
    )


@use.tinny_profiler
def prioritize(tasks: list[Task2]) -> list:
    sorted_tasks = sorted(
        tasks,
        reverse=True,
        key=lambda t: (t.level_id, t.get_space_priority() + t.priority, t.last_checked),
    )
    return deque(sorted_tasks)


def balance(tasks: list[Task2], activity_time_spent: dict[int, int]) -> list[Task2]:
    # first prefer neglected activity; second prefer neglected tasks/habits
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (
            max(
                activity_time_spent[t.primary_activity_id],
                1.618 * activity_time_spent[t.secondary_activity_id],
            ),
            weight(  # lightest weights float to the top!
                t.get_time_spent(),
                t.last_checked,
                time(),
            ),
        ),
    )
    return deque(sorted_tasks)


def schedule(tasks: list) -> list:
    filtered_by_infinity = filter(lambda t: not isinf(float(t.get_deadline())) or t.ilk is ILK.routine, tasks)
    sorted_by_last_checked = sorted(filtered_by_infinity, key=lambda t: t.last_checked)
    sorted_by_deadline = sorted(sorted_by_last_checked, key=lambda t: float(t.get_deadline()))
    return deque(sorted_by_deadline)


def check_tasks(tasks: list[Task2], now: datetime):
    for task in tasks:
        if not task.done:
            yield task
            continue
        if task.get_repeats() is None:
            yield task
            continue

        every_x = task.get_repeats().x_every

        then = datetime.fromtimestamp(task.last_finished)
        if task.ilk is ILK.habit:
            if now.date() > then.date():
                task.set_done(False)

        elif task.get_repeats() is not None:
            reset_task(task, now, every_x)

        yield task


def reset_task(db, task, now, every_x):
    every_ilk, x_every, per_ilk, x_per = task.get_repeats()

    now = datetime.timestamp(now)

    match every_ilk:
        case EVERY.minute:
            then_minute = task.last_finished // 60
            now_minute = now // 60
            if (now_minute - then_minute) % every_x == 0:
                task.is_done = False
        case EVERY.hour:
            then_hour = task.last_finished // (60 * 60)
            now_hour = now // (60 * 60)
            if (now_hour - then_hour) % every_x == 0:
                task.is_done = False
        case EVERY.day:
            then_day = task.last_finished // (60 * 60 * 24)
            now_day = now // (60 * 60 * 24)
            if (now_day - then_day) % every_x == 0:
                task.is_done = False
        case EVERY.week:
            reset_task_if_time_passed(now, 7, task, every_x)
        case EVERY.year:
            reset_task_if_time_passed(now, 365.25, task, every_x)
        case EVERY.undetermined:
            td = timedelta(
                seconds={
                    EVERY.minute: 60,
                    EVERY.hour: 60 * 60,
                    EVERY.day: 60 * 60 * 24,
                    EVERY.week: 60 * 60 * 24 * 7,
                    EVERY.year: 60 * 60 * 24 * 365.25,
                }[per_ilk]
            )
            query = db.execute(
                f"""
    SELECT COUNT(*) FROM sessions WHERE task_id = {task.id} and stop > {(now - td).timestamp()} and (stop - start) > 5  
    """
            )

            if len(list(query.fetchall())) < x_per:
                task.is_done = False


def reset_task_if_time_passed(now, days, task, every_x):
    now_week = now // (60 * 60 * 24 * days)
    then_week = task.last_finished // (60 * 60 * 24 * days)
    if (now_week - then_week) % every_x == 0:
        task.is_done = False


def levenshtein_distance(text, pattern) -> int:
    """Calculates the Levenshtein distance between two strings."""


def filter_tasks(tasks: Iterable[Task2], pattern: str) -> Iterable[Task2]:
    # TODO: use fuzzy matching from https://github.com/taleinat/fuzzysearch
    if pattern.isspace() or not pattern:
        return tasks
    return filter(lambda t: pattern in t.do.casefold(), tasks)


def skill_level(seconds):
    """Maps a number of hours to a small number of levels.

    Assumptions:
    0 h -> 0 L
    10000 h -> 100 L
    25000 h -> 200 L

    Wolfram Alpha proposes x^2/4+75x as best fitting function, solved for x:
    y = 2(sqrt(x+5625) - 75)
    which is a pretty neat function!
    On one extreme, if someone were to log their whole life over 100 years, the level would be 1729,
    thus giving a nice, relatively flat curve with "diminishing returns" but never approaching a maximum.
    On the other hand, for a beginner, the "Level-UPs" come nicely at
    Level -> Hours
    1 75.25
    2 151.0
    3 227.25
    4 304.0
    5 381.25
    6 459.0
    7 537.25
    8 616.0
    9 695.25
    10 775.0
    """
    x = seconds / (60 * 60)

    return 2 * (sqrt(x + 5625) - 75)


@use.woody_logger
@beartype
def filter_by_constraints(tasks: Iterable[Task2], /, *, now: datetime) -> Iterable[Task2]:
    for task in tasks:
        if task.get_constraints() is None:
            yield task
        elif task.get_constraints()[now.weekday(), now.time().hour * 6 + now.time().minute // 10]:
            yield task


@beartype
def consider_tasks(tasks: Iterable[Task2]) -> Iterable[Task2]:
    return filter(lambda t: not t.deleted and not t.draft and not t.inactive, tasks)


@pipes
def get_tasks(db) -> list[Task2]:
    now = datetime.now()
    return (
        retrieve_tasks(db) >> check_tasks(now=now) >> consider_tasks << filter_by_constraints(now=now) >> list
    )


def get_string_representation_of_dict_without_quotation_marks(d: dict) -> str:
    return str(d).replace("'", "").replace('"', "")
