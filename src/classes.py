import unicodedata
from collections import namedtuple
from datetime import datetime
from enum import Enum, Flag
from functools import wraps
from pathlib import Path
from time import time
from typing import Any, NamedTuple

import use
from beartype import beartype

from stuff import app, config, db

np = use(
    "numpy",
    version="1.24.1",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "i㹄臲嬁㯁㜇䕀蓴卄闳䘟菽掸䢋䦼亱弿椊",  # cp311-win_amd64
    },
    import_as="np",
)

import numpy as np  # to make pylance happy - they don't know justuse YET :)

q = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/q/main/q.py"), modes=use.recklessness, import_as="q"
).Q()


last_sql_access = 0

ILK = Enum("TaskType", "task habit tradition routine")  # * enum numbering starts with 1!
ACTIVITY = Enum("ACTIVITY", "body mind spirit")
LEVEL = Enum("LEVEL", "MUST SHOULD MAY SHOULD_NOT MUST_NOT")


class EVERY(Enum):
    undetermined = -1
    minute = 1
    hour = 2
    day = 3
    week = 4
    month = 5
    year = 6


Every = namedtuple("Every", "every_ilk x_every per_ilk x_per")


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


class Skill(NamedTuple):
    id: int

    @property
    @cached_getter
    def time_spent(self):
        query = db.execute(
            f"""
SELECT time_spent, adjust_time_spent
FROM tasks
INNER JOIN task_trains_skill
ON tasks.id = task_trains_skill.task_id
WHERE skill_id = {self.id} AND NOT (deleted OR draft or inactive)
"""
        )
        return sum(
            typed(time_spent, int) + typed(adjust_time_spent, int)
            for time_spent, adjust_time_spent in query.fetchall()
        )


class Task:
    __slots__ = (
        "id",
        "do",
        "deleted",
        "draft",
        "inactive",
        "done",
        "primary_activity_id",
        "secondary_activity_id",
        "space_id",
        "priority",
        "level_id",
        "adjust_time_spent",
        "difficulty",
        "fear",
        "embarrassment",
        "last_checked",
        "workload",
        "ilk",
        "notes",
    )

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            self.set_(name, value, to_db=False)

    @cached_getter
    def get_repeats(self) -> Every[EVERY, int]:
        """
        Return the repeats for this task.

        Returns:
            Every[EVERY, int]: Returns a namedtuple Every for EVERY unit of time, 
                                ints of unit, per EVERY unit of time, ints of unit.
        """ """"""
        return (
            Every(
                EVERY(
                    typed_row(
                        query,
                        0,
                        int,
                    )
                ),
                typed_row(query, 1, int),
                EVERY(typed_row(query, 2, int)),
                typed_row(
                    query,
                    3,
                    int,
                ),
            )
            if (
                query := db.execute(
                    f"""
SELECT every_ilk, x_every, per_ilk, x_per  FROM repeats WHERE task_id={self.id}
                           """
                ).fetchone()
            )
            else None
        )

    @cached_getter
    def get_constraints(self) -> np.ndarray | None:
        return (
            np.fromiter((int(x) for x in typed_row(query, 0, str)), int).reshape(7, 288)
            if (
                query := db.execute(
                    f"""
    SELECT flags FROM constraints WHERE task_id = {self.id}
            """
                ).fetchone()
            )
            is not None
            else None
        )

    @property
    @cached_getter
    def space_priority(self) -> float:
        if self.space_id:
            return typed_row(
                db.execute(
                    f"""
            SELECT priority FROM spaces WHERE space_id={self.space_id};
            """
                ).fetchone(),
                0,
                float,
            )
        else:
            return 0

    @property
    @cached_getter
    def space(self) -> str:
        return get_space_name(self.space_id)

    @property
    @cached_getter
    def time_spent(self):
        query = db.execute(
            f"""
SELECT time_spent, adjust_time_spent
FROM tasks
INNER JOIN task_trains_skill
ON tasks.id = task_trains_skill.task_id
WHERE skill_id = {self.id} AND NOT (deleted OR draft or inactive)
"""
        )
        return sum(
            typed(time_spent, int) + typed(adjust_time_spent, int)
            for time_spent, adjust_time_spent in query.fetchall()
        )

    @property
    @cached_getter
    def deadline(self) -> float:
        query = db.execute(
            f"""
        SELECT time_of_reference FROM deadlines WHERE task_id={self.id}
        """
        )
        own_deadline = typed_row(query.fetchone(), 0, float, default=float("inf"))
        return min([t.deadline for t in self.supertasks] + [own_deadline]) - (self.workload or 0)

    def set_deadline(self, deadline: float) -> float:
        # removing deadline
        if deadline == float("inf"):
            db.execute(f"DELETE FROM deadlines WHERE task_id={self.id}")
            db.commit()
            return

        query = db.execute(f"SELECT time_of_reference FROM deadlines WHERE task_id={self.id}")

        # changing deadline
        if query.fetchone():
            db.execute(f"UPDATE deadlines SET time_of_reference={deadline} WHERE task_id={self.id}")
        else:  # new deadline
            db.execute(f"INSERT INTO deadlines (task_id, time_of_reference) VALUES ({self.id}, {deadline})")

        db.commit()

    @property
    @cached_getter
    def supertasks(self):
        query = db.execute(
            f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return [retrieve_task_by_id(db, typed(task_of_concern, int)) for task_of_concern in query.fetchall()]

    @property
    @cached_getter
    def skill_ids(self) -> list[int]:
        query = db.execute(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id}
        """
        )
        return [Skill(typed_row(skill_id, 0, int)) for skill_id in query.fetchall()]

    def set_adjust_time_spent(self, value) -> None:
        self.set_("adjust_time_spent", value)

    @property
    def total_time_spent(self) -> int:
        return self.adjust_time_spent + self.time_spent

    def get_total_priority(self, priority=None, space_priority=None) -> float:
        own_priority = (self.priority if priority is None else priority) + (
            self.space_priority if space_priority is None else space_priority
        )

        max_supertask = max(self.supertasks, key=lambda t: t.get_total_priority(), default=None)
        sibling_priorities = (
            {t.priority for t in max_supertask.subtasks} if max_supertask else {self.priority}
        )
        normalized = own_priority / max(sibling_priorities | {1})
        return (normalized + max_supertask.get_total_priority()) if max_supertask else own_priority

    def get_short_do(self, max_len=None):
        lines = self.do.split("\n")
        if not max_len:
            return lines[0] + ("" if len(lines) == 1 else " […]")
        first_line_parts = lines[0].split()
        # line = (
        #     f"{first_line_parts[0]} "
        #     + disemvowel(" ".join(first_line_parts[1:-1]))
        #     + " "
        #     + first_line_parts[-1]
        # )
        line = lines[0][:max_len]

        return line + ("" if len(lines) == 1 else " […]")

    def delete(self):
        self.set_("deleted", True)

    def really_delete(self):
        db.execute(
            f"""
        DELETE FROM tasks WHERE id={self.id}
        """
        )
        db.commit()

    @property
    @cached_getter
    def resources(self) -> list[str]:
        return [
            (typed(url, str), typed(resource_id, int))
            for url, resource_id in db.execute(
                f"""
SELECT resources.url, resources.resource_id
FROM resources
INNER JOIN task_uses_resource
ON resources.resource_id= task_uses_resource.resource_id
INNER JOIN tasks
ON task_uses_resource.task_id = tasks.id
WHERE tasks.id = {self.id}
        """
            ).fetchall()
        ]

    @property
    @cached_getter
    def level(self) -> str:
        actual_level = max(t.level_id for t in self.supertasks | {self})
        return get_level_name(actual_level)

    @property
    @cached_getter
    def last_finished(self) -> int:
        query = db.execute(
            f"""
        SELECT stop
        FROM sessions
        WHERE task_id == {self.id} AND finished == TRUE
        ORDER BY
            stop DESC
        ;
        """
        )
        return typed(query.fetchone(), 0, int, default=0)

    @property
    @cached_getter
    def supertasks(self) -> set["Task"]:
        query = db.execute(
            f"""
SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return {retrieve_task_by_id(db, typed_row(row, 0, int)) for row in query.fetchall()}

    @property
    @cached_getter
    def subtasks(self) -> set["Task"]:
        query = db.execute(
            f"""
SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
            """
        )
        return {retrieve_task_by_id(db, typed_row(row, 0, int)) for row in query.fetchall()}

    def set_subtasks(self, tasks: set["Task"]) -> None:
        db.executemany(
            "INSERT INTO task_requires_task (task_of_concern, required_task) VALUES (?, ?)",
            [(self.id, t.id) for t in tasks],
        )

    def set_supertasks(self, tasks: set["Task"]) -> None:
        db.executemany(
            "INSERT INTO task_requires_task (task_of_concern, required_task) VALUES (?, ?)",
            [(t.id, self.id) for t in tasks],
        )

    def set_primary_activity_id(self, activity_id: int) -> None:
        self.set_("primary_activity_id", activity_id)

    def set_last_checked(self, time_: float) -> None:
        self.set_("last_checked", time_)

    def set_(self, name: str, value: Any, to_db=True):
        if to_db:
            db.execute(f"UPDATE tasks SET {name}=? WHERE id={self.id}", (value,))
            db.commit()
        object.__setattr__(self, name, value)

        return value

    def __str__(self):
        return f"Task({self.id}, ...)"

    def __repr__(self):
        return f"Task(**{ {k: getattr(self, k) for k in Task.__slots__}})"

    def __setattr__(self, name, value):
        print(f"attempted assignment to read-only attribute {name}={value}")

    def __eq__(self, other):
        return False if other is None else self.id == other.id

    def __hash__(self):
        return self.id

    def __iter__(self):
        for k in self.__slots__:
            yield k, getattr(self, k)

    @classmethod
    def from_id(cls, ID: int) -> "Task":
        return retrieve_task_by_id(db, ID)


def retrieve_task_by_id(db, ID: int) -> Task:
    query = db.execute(f"SELECT {', '.join(Task.__slots__)} FROM tasks WHERE id == {ID};")
    res = query.fetchone()
    assert res is not None, breakpoint()
    kwargs = dict(zip(Task.__slots__, res))
    return Task(**kwargs)


@cached_func_noarg
def retrieve_tasks(db) -> list[Task]:
    """Load all tasks from the database."""
    query = db.execute(f"SELECT {', '.join(Task.__slots__)} FROM tasks;")

    return [Task(**dict(zip(Task.__slots__, res))) for res in query.fetchall()]


@cached_getter
def get_level_name(level_id) -> str:
    query = db.execute(
        f"""
SELECT name FROM levels WHERE level_id={level_id};
"""
    )
    return typed_row(query.fetchone(), 0, str)


@cached_getter
def get_space_name(space_id) -> str:
    if space_id is not None:
        return typed_row(
            db.execute(
                f"""
    SELECT name FROM spaces WHERE space_id={space_id};
    """
            ).fetchone(),
            0,
            str,
        )
    else:
        return ""


def get_activity_name(activity_id) -> str:
    if activity_id is None:
        return ""
    query = db.execute(
        f"""
        SELECT name FROM activities WHERE activity_id={activity_id};
        """
    )
    return typed_row(query.fetchone(), 0, str, default="")


def disemvowel(text: str) -> str:
    for word in text.split():
        yield disemvowel(word)
    first, middle, last = text[0], text[1:-1], text[-1]

    ascii_text = unicodedata.normalize("NFD", middle).encode("ascii", "ignore").decode()
    return first + ascii_text.translate(str.maketrans("", "", "aeiouAEIOU")) + last
