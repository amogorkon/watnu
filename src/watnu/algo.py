from collections import deque
from datetime import datetime
from lib.functions import bounded_sigmoid
from lib.functions import sigmoid
from math import isinf
from math import sqrt
from time import time

WEEKTIME = {
    name: i
    for i, name in enumerate(
        [
            (day, hour, part)
            for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            for hour in range(24)
            for part in range(6)
        ]
    )
}

# fresh tasks have a habit weight of 0.2689414213699951 - HOURS
habit_weight = sigmoid(k=0.0002, L=1, x0=5000)
# neglection weight can trump a fresh habit_weight at 3915, no matter how much time was put in - HOURS
neglection_weight = bounded_sigmoid(0, 5380, inverse=True)


def weight(primary_activity_time, secondary_activity_time, time_spent, last_checked, now):
    return min(
        habit_weight(time_spent / (60 * 60)),
        neglection_weight((now - last_checked) / (60 * 60)),
    )


def prioritize(tasks: list) -> list:
    sorted_tasks = sorted(
        tasks,
        reverse=True,
        key=lambda t: (t.level_id, t.space_priority + t.priority, t.last_checked),
    )
    return deque(sorted_tasks)


def balance(tasks: list, activity_time_spent: dict) -> list:
    # first prefer neglected activity; second prefer neglected tasks/habits
    sorted_tasks = sorted(
        tasks,
        key=lambda t: weight(
            activity_time_spent[t.activity_id],
            activity_time_spent[t.secondary_activity_id],
            t.time_spent,
            t.last_checked,
            time(),
        ),
    )
    return deque(sorted_tasks)


def schedule(tasks: list) -> list:
    filtered_by_infinity = filter(lambda t: not isinf(float(t.deadline)), tasks)
    sorted_by_last_checked = sorted(filtered_by_infinity, key=lambda t: t.last_checked)
    sorted_by_deadline = sorted(sorted_by_last_checked, key=lambda t: float(t.deadline))
    return deque(sorted_by_deadline)


def check_task_conditions(task, now: datetime):
    if task.habit:
        if (today := now.date()) > (then := datetime.fromtimestamp(task.last_finished).date()):
            task.done = False


def filter_tasks(tasks, pattern):
    if pattern.isspace() or not pattern:
        return tasks
    return list(filter(lambda t: pattern in t.do.casefold(), tasks))


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


def check_weektime(bitfield):
    print(bitfield)
