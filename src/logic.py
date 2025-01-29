from collections import deque
from collections.abc import Iterable
from datetime import datetime, timedelta
from functools import reduce
from math import sqrt
from sqlite3 import Connection
from time import time

import numpy as np
from Levenshtein import ratio
from nltk.tokenize import WordPunctTokenizer  # noqa: E402

from src.classes import EVERY, ILK, Task
from src.functions import bounded_sigmoid, sigmoid
from src.helpers import cached_getter, pipes

# fresh tasks have a habit weight of 0.2689414213699951 - HOURS
habit_weight = sigmoid(k=0.0002, L=1, x0=5000)
# neglection weight can trump a fresh habit_weight at 3915, no matter how much time was put in - HOURS
neglection_weight = bounded_sigmoid(0, 5380, inverse=True)


def weight(time_spent, last_checked, now) -> float:
    return min(
        habit_weight(time_spent / (60 * 60)),
        neglection_weight((now - last_checked) / (60 * 60)),
    )


def piped_print(iterator_of_things, enumerated=True):
    if enumerated:
        for i, thing in enumerate(iterator_of_things):
            print(f"{i}: {thing}")
            yield thing
    else:
        for thing in iterator_of_things:
            print(thing)
            yield thing


@pipes
def prioritize(tasks: list[Task]) -> deque[Task]:
    return (
        tasks
        >> sorted(key=lambda t: t.level_id, reverse=True)
        >> sorted(key=lambda t: t.get_total_priority(), reverse=True)
        >> sorted(key=lambda t: min(t.last_checked, app.startup_time))
        >> deque
    )


def balance(tasks: list[Task], activity_time_spent: dict[int, int]) -> deque[Task]:
    # first prefer neglected activity; second prefer neglected tasks/habits
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (
            max(
                activity_time_spent[t.primary_activity.value],
                1.618 * activity_time_spent[t.secondary_activity.value],
            ),
            weight(  # lightest weights float to the top!
                t.time_spent,
                t.last_checked,
                time(),
            ),
        ),
    )
    return deque(sorted_tasks)


@cached_getter
def sum_of_timeslots_per_year(task: Task) -> int:
    """Timeslots are based on boolean numpy arrays.
    The sum of the array is the number of timeslots."""

    constraints = task.constraints or np.ones((7, 288))
    constraints_over_the_year = np.tile(constraints, (52, 1))

    # cut the array if the deadline is within the same year
    if task.deadline != float("inf"):
        deadline = datetime.fromtimestamp(task.deadline)
        days_until_deadline = (deadline - datetime.now()).days
        if days_until_deadline < 365:
            constraints_over_the_year = constraints_over_the_year[:days_until_deadline]

    return np.sum(constraints_over_the_year)


def filter_by_timeslots(tasks: list[Task]) -> list[Task]:
    """Filter if there is any timing restriction at all."""
    # 7*288 (slots per week) * 52 (weeks per year) = 104832
    return [task for task in tasks if sum_of_timeslots_per_year(task) < 104832]


@pipes
def schedule(tasks: list) -> deque[Task]:
    return (
        tasks
        >> filter_by_timeslots
        >> sorted(key=lambda t: sum_of_timeslots_per_year(t), reverse=True)
        >> sorted(key=lambda t: t.last_checked)
        >> sorted(key=lambda t: float(t.deadline))
        >> deque
    )


def check_tasks(tasks: list[Task], now: datetime) -> Iterable[Task]:
    for task in tasks:
        if not task.done:
            yield task
            continue
        if task.repeats is None:
            yield task
            continue

        every_x = task.repeats.x_every

        then = datetime.fromtimestamp(task.last_finished)
        if task.ilk is ILK.habit:
            if now.date() > then.date():
                task.set_("done", False)

        elif task.repeats is not None:
            reset_task(task, datetime.timestamp(now), every_x)

        yield task


def reset_task(db: Connection, task: Task, now: float, every_x: int):
    every_ilk, x_every, per_ilk, x_per = task.repeats

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
    SELECT COUNT(*) FROM sessions WHERE task_id = {task.id}
    and stop > {(now - td).timestamp()}
    and (stop - start) > 5
    """
            )

            if len(list(query.fetchall())) < x_per:
                task.is_done = False


def reset_task_if_time_passed(now, days, task, every_x):
    now_week = now // (60 * 60 * 24 * days)
    then_week = task.last_finished // (60 * 60 * 24 * days)
    if (now_week - then_week) % every_x == 0:
        task.is_done = False


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


@pipes
def get_doable_tasks(tasks: list[Task]) -> list[Task]:
    """Get all tasks that are doable at this moment."""
    now = datetime.now()
    return (
        tasks
        >> check_tasks(now=now)
        >> filter_tasks_by_requirements
        >> filter_tasks_by_constraints(now=now)
        >> list
    )


def filter_tasks_by_requirements(tasks: list[Task]) -> Iterable[Task]:
    for task in tasks:
        if task.is_doable:
            yield task


def filter_tasks_by_status(tasks: list[Task], status: int) -> Iterable[Task]:
    match status:
        # open
        case 0:
            return filter(
                lambda t: not t.done and not t.draft and not t.inactive and not t.deleted,
                tasks,
            )
        # draft
        case 1:
            return filter(
                lambda t: t.draft,
                tasks,
            )
        # inactive
        case 2:
            return filter(
                lambda t: t.inactive,
                tasks,
            )
        # done
        case 3:
            return filter(
                lambda t: t.done,
                tasks,
            )
        # deleted
        case 4:
            return filter(
                lambda t: t.deleted,
                tasks,
            )
        case 5:
            return tasks


def filter_tasks_by_constraints(tasks: Iterable[Task], /, *, now: datetime) -> Iterable[Task]:
    for task in tasks:
        if task.constraints is None:
            yield task
        elif task.constraints[
            now.weekday(),
            now.time().hour * 6 + now.time().minute // 5,
        ]:
            yield task


def einstein_sum(values):
    """OR variant."""

    def op(x, y):
        return (x + y) / (1 + x * y)

    return reduce(op, values)


def filter_ratio(pattern, text):
    """Calculate the maximum ratio between pattern and text."""
    P = WordPunctTokenizer().tokenize(pattern.casefold())
    T = WordPunctTokenizer().tokenize(text.casefold())
    if not P or not T:
        return 0

    ratios = [max(ratio(p, t) for t in T) for p in P]

    return einstein_sum(ratios)


def _by_simple_matching(tasks, pattern) -> list[Task]:
    return list(filter(lambda t: pattern in t.do.casefold(), tasks))


def _by_levenshtein(tasks, pattern) -> list[Task]:
    # https://maxbachmann.github.io/Levenshtein/index.html
    # return sorted tasks by levenshtein ratios with cutoff

    ratios = zip(tasks, (filter_ratio(pattern, t.do) for t in tasks))
    cutoff = filter(lambda item: item[1] > 0.7, ratios)
    return [item[0] for item in sorted(cutoff, key=lambda item: item[1], reverse=True)]


def filter_tasks_by_content(tasks: Iterable[Task], pattern: str) -> Iterable[Task]:
    if pattern.isspace() or not pattern:
        return tasks
    return _by_levenshtein(tasks, pattern) or _by_simple_matching(tasks, pattern.casefold())


def filter_tasks_by_ilk(tasks: Iterable[Task], ilk: int | None) -> Iterable[Task]:
    if ilk is None:
        return list(tasks)
    return list(filter(lambda t: t.ilk == ilk if ilk else True, tasks))


def filter_tasks_by_space(tasks: Iterable[Task], space_id: int) -> Iterable[Task]:
    """Filter tasks by space id."""
    return filter(
        lambda t: t.space_id == (space_id) if space_id is not None else True,
        tasks,
    )


def filter_filter_history_whitespace(history: Iterable[str]):
    for text in history:
        if not text.isspace():
            yield text


def filter_filter_history_if_included(history: Iterable[str]):
    """Remove sub-strings from the history and only keep the longest entries."""
    seen = set()
    for text in history:
        if any(text in s for s in seen):
            continue
        seen.add(text)
        yield text


@pipes
def filter_filter_history(history: Iterable[str]):
    return history >> filter_filter_history_whitespace >> filter_filter_history_if_included


@pipes
def calculate_sum_of_timeslots_for_next_year(constraints: np.array):
    """
    Calculate the sum of timeslots allocated for this task for the next 52 weeks (~365 days).

    Args:
        constraints (np.array): 5 min timeslots per week
    """
    sum(constraints) * 52
