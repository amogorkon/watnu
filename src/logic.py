from collections import deque
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from functools import reduce
from itertools import product, takewhile
from math import isinf, sqrt
from sqlite3 import Connection
from time import time

import numpy as np
import use
from beartype import beartype
from Levenshtein import ratio, seqratio, setratio

from classes import EVERY, ILK, Task, retrieve_tasks

fuzzy = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/fuzzylogic/master/src/fuzzylogic/functions.py"),
    modes=use.recklessness,
)

pipes = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/libs/main/pipes.py"),
    modes=use.recklessness,
    import_as="pipes",
).pipes

use(
    "nltk",
    version="3.8.1",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "l䓔䱎㬰芰鯽倳疺苅ˤ崠㩡㦌䪑ˌ宐偏嵪",  # py3-any
        "I帵螒倝延襂癑槓䕴茿利鹽簸艦Ȣ鼍䞗唀",  # None-None
    },
)
from nltk.tokenize import WordPunctTokenizer

# fresh tasks have a habit weight of 0.2689414213699951 - HOURS
habit_weight = fuzzy.sigmoid(k=0.0002, L=1, x0=5000)
# neglection weight can trump a fresh habit_weight at 3915, no matter how much time was put in - HOURS
neglection_weight = fuzzy.bounded_sigmoid(0, 5380, inverse=True)


def weight(time_spent, last_checked, now) -> float:
    return min(
        habit_weight(time_spent / (60 * 60)),
        neglection_weight((now - last_checked) / (60 * 60)),
    )


@use.tinny_profiler
def prioritize(tasks: list[Task]) -> deque[Task]:
    sorted_tasks = sorted(
        tasks,
        reverse=True,
        key=lambda t: (t.level_id, t.get_total_priority(), t.last_checked),
    )
    return deque(sorted_tasks)


def balance(tasks: list[Task], activity_time_spent: dict[int, int]) -> deque[Task]:
    # first prefer neglected activity; second prefer neglected tasks/habits
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (
            max(
                activity_time_spent[t.primary_activity_id],
                1.618 * activity_time_spent[t.secondary_activity_id],
            ),
            weight(  # lightest weights float to the top!
                t.time_spent,
                t.last_checked,
                time(),
            ),
        ),
    )
    return deque(sorted_tasks)


def schedule(tasks: list) -> deque[Task]:
    filtered_by_infinity = filter(lambda t: not isinf(float(t.deadline)) or t.ilk is ILK.routine, tasks)
    sorted_by_last_checked = sorted(filtered_by_infinity, key=lambda t: t.last_checked)
    sorted_by_deadline = sorted(sorted_by_last_checked, key=lambda t: float(t.deadline))
    return deque(sorted_by_deadline)


def check_tasks(tasks: list[Task], now: datetime) -> Iterable[Task]:
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
                task.set_("done", False)

        elif task.get_repeats() is not None:
            reset_task(task, datetime.timestamp(now), every_x)

        yield task


def reset_task(db: Connection, task: Task, now: float, every_x: int):
    every_ilk, x_every, per_ilk, x_per = task.get_repeats()

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
def get_doable_tasks(db: Connection) -> list[Task]:
    """Get all viable tasks from the database."""
    now = datetime.now()
    return (
        retrieve_tasks(db)
        >> check_tasks(now=now)
        >> filter_tasks_by_status(0)
        << filter_tasks_by_constraints(now=now)
        >> list
    )


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
        if task.get_constraints() is None:
            yield task
        elif task.get_constraints()[now.weekday(), now.time().hour * 6 + now.time().minute // 5]:
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
    return filter(lambda t: t.space_id == (space_id) if space_id is not None else True, tasks)
