from collections import namedtuple
from enum import Enum, Flag
from functools import wraps
from pathlib import Path
from time import time
from typing import Any, NamedTuple

import use
from beartype import beartype

np = use(
    "numpy",
    version="1.24.1",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "i㹄臲嬁㯁㜇䕀蓴卄闳䘟菽掸䢋䦼亱弿椊",  # cp311-win_amd64
    },
)

q = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/q/main/q.py"), modes=use.recklessness, import_as="q"
).Q()

use(use.Path("lib/utils.py"), import_as="lib.utils")

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


def set_globals(config_, db_, app_):
    global config, db, app
    config = config_
    db = db_
    app = app_


def cached_and_invalidated(func):
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


def typed(row: tuple, idx: int, kind: type, default=None, debugging=False):
    if debugging and row is None:
        breakpoint()

    if row is None and default is not None:
        return default

    res = row[idx]

    if isinstance(res, kind):
        return res
    if res is None and default is not None:
        return default

    raise ValueError(f"Expected {kind} but got {type(res)}")


class Skill(NamedTuple):
    id: int

    @property
    @cached_and_invalidated
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
        return sum(typed(row, 0, int) + typed(row, 1, int) for row in query.fetchall())


class Task2:
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

    def __init__(
        self,
        ID,
        do,
        notes,
        deleted,
        draft,
        inactive,
        done,
        primary_activity_id,
        secondary_activity_id,
        space_id,
        priority,
        level_id,
        adjust_time_spent,
        difficulty,
        fear,
        embarrassment,
        last_checked,
        workload,
        ilk,
    ):
        self.id = ID
        self.do = do
        self.deleted = deleted
        self.draft = draft
        self.inactive = inactive
        self.done = done
        self.primary_activity_id = primary_activity_id
        self.secondary_activity_id = secondary_activity_id
        self.space_id = space_id
        self.priority = priority
        self.level_id = level_id
        self.adjust_time_spent = adjust_time_spent
        self.difficulty = difficulty
        self.fear = fear
        self.embarrassment = embarrassment
        self.last_checked = last_checked
        self.workload = workload if workload is not None else 0  # How to estimate a default?
        self.ilk = ilk
        self.notes = notes

    def set_done(self, value: bool) -> None:
        self.done = value
        db.execute(
            f"""
UPDATE tasks
SET done={value} 
WHERE id={self.id}
        """
        )

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
                    typed(
                        query,
                        0,
                        int,
                    )
                ),
                typed(query, 1, int),
                EVERY(typed(query, 2, int)),
                typed(
                    query.value,
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

    def get_constraints(self) -> np.ndarray:
        return (
            np.fromiter((int(x) for x in typed(query, 0, str)), int).reshape(7, 144)
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

    def get_space_priority(self) -> float:
        if self.space_id:
            return typed(
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

    def get_space(self) -> str:
        if self.space_id:
            return typed(
                db.execute(
                    f"""
        SELECT name FROM spaces WHERE space_id={self.space_id};
        """
                ).fetchone(),
                0,
                str,
                default=None,
            )
        else:
            return ""

    def get_time_spent(self):
        query = db.execute(
            f"""
SELECT time_spent, adjust_time_spent
FROM tasks
INNER JOIN task_trains_skill
ON tasks.id = task_trains_skill.task_id
WHERE skill_id = {self.id} AND NOT (deleted OR draft or inactive)
"""
        )
        return sum(typed(row, 0, int) + typed(row, 1, int) for row in query.fetchall())

    def get_deadline(self) -> float:
        query = db.execute(
            f"""
        SELECT time_of_reference FROM deadlines WHERE task_id={self.id}
        """
        )
        own_deadline = typed(query.fetchone(), 0, float, default=float("inf"))
        return min([t.get_deadline() for t in self.get_supertasks()] + [own_deadline]) - self.workload

    def get_supertasks(self):
        query = db.execute(
            f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return [retrieve_task_by_id(db, typed(row, 0, int)) for row in query.fetchall()]

    def get_skills(self) -> list[int]:
        query = db.execute(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id}
        """
        )
        return [Skill(typed(row, 0, int)) for row in query.fetchall()]

    def get_adjust_time_spent(self) -> int:
        query = db.execute(
            f"""
        SELECT adjust_time_spent FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.fetchone(), 0, int, 0)

    def set_adjust_time_spent(self, value) -> None:
        db.execute(
            f"""
        UPDATE tasks SET adjust_time_spent={value} 
        WHERE id={self.id}
        """
        )

    def get_total_time_spent(self) -> int:
        return self.get_adjust_time_spent() + self.get_time_spent()


def retrieve_task_by_id(db, ID: int) -> Task2:
    query = db.execute(
        f"""
SELECT id, do, notes, deleted, draft, inactive, done, primary_activity_id, secondary_activity_id, space_id, priority, level_id, adjust_time_spent, difficulty, fear, embarrassment, last_checked, workload, ilk FROM tasks WHERE id == {ID};
    """
    )
    res = query.fetchone()
    if res is None:
        breakpoint()
    return Task2(*res)


@use.woody_logger
@cached_and_invalidated
def retrieve_tasks(db) -> list[Task2]:
    query = db.execute(
        """
        SELECT id, do, notes, deleted, draft, inactive, done, primary_activity_id, secondary_activity_id, space_id, priority, level_id, adjust_time_spent, difficulty, fear, embarrassment, last_checked, workload, ilk FROM tasks;
    """
    )

    return [
        Task2(
            ID,
            do,
            notes,
            deleted,
            draft,
            inactive,
            done,
            primary_activity_id,
            secondary_activity_id,
            space_id,
            priority,
            level_id,
            adjust_time_spent,
            difficulty,
            fear,
            embarrassment,
            last_checked,
            workload,
            ilk,
        )
        for ID, do, notes, deleted, draft, inactive, done, primary_activity_id, secondary_activity_id, space_id, priority, level_id, adjust_time_spent, difficulty, fear, embarrassment, last_checked, workload, ilk in query.fetchall()
    ]
