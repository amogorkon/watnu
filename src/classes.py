from collections import namedtuple
from enum import Enum, Flag
from functools import wraps
from pathlib import Path
from time import time
from typing import Any, NamedTuple

import use
from beartype import beartype

from stuff import config, db, app

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
        db.commit()

    @cached_and_invalidated
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

    @cached_and_invalidated
    def get_constraints(self) -> np.ndarray:
        return (
            np.fromiter((int(x) for x in typed_row(query, 0, str)), int).reshape(7, 144)
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

    @cached_and_invalidated
    def get_space_priority(self) -> float:
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

    @cached_and_invalidated
    def get_space(self) -> str:
        if self.space_id:
            return typed_row(
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

    @cached_and_invalidated
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
        return sum(
            typed(time_spent, int) + typed(adjust_time_spent, int)
            for time_spent, adjust_time_spent in query.fetchall()
        )

    @cached_and_invalidated
    def get_deadline(self) -> float:
        query = db.execute(
            f"""
        SELECT time_of_reference FROM deadlines WHERE task_id={self.id}
        """
        )
        own_deadline = typed_row(query.fetchone(), 0, float, default=float("inf"))
        return min([t.get_deadline() for t in self.get_supertasks()] + [own_deadline]) - self.workload

    @cached_and_invalidated
    def get_supertasks(self):
        query = db.execute(
            f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return [retrieve_task_by_id(db, typed(task_of_concern, int)) for task_of_concern in query.fetchall()]

    @cached_and_invalidated
    def get_skills(self) -> list[int]:
        query = db.execute(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id}
        """
        )
        return [Skill(typed(skill_id, int)) for skill_id in query.fetchall()]

    @cached_and_invalidated
    def get_adjust_time_spent(self) -> int:
        query = db.execute(
            f"""
        SELECT adjust_time_spent FROM tasks WHERE id={self.id}
        """
        )
        return typed_row(query.fetchone(), 0, int, 0)

    def set_adjust_time_spent(self, value) -> None:
        db.execute(
            f"""
        UPDATE tasks SET adjust_time_spent={value} 
        WHERE id={self.id}
        """
        )
        db.commit()

    def get_total_time_spent(self) -> int:
        return self.get_adjust_time_spent() + self.get_time_spent()

    def delete(self):
        db.execute(
            f"""
        UPDATE tasks SET deleted=1 WHERE id={self.id}
        """
        )
        db.commit()

    def really_delete(self):
        db.execute(
            f"""
        DELETE FROM tasks WHERE id={self.id}
        """
        )
        db.commit()

    @cached_and_invalidated
    def get_resources(self) -> list[str]:
        return [
            (typed(resource_id, str), typed(url, int))
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

    @cached_and_invalidated
    def get_level(self) -> str:
        actual_level = max(t.level_id for t in self.get_supertasks() | {self})
        query = db.execute(
            f"""
        SELECT name FROM levels WHERE level_id={actual_level};
        """
        )
        return typed_row(query.fetchone(), 0, str)

    @cached_and_invalidated
    def get_supertasks(self) -> set["Task"]:
        query = db.execute(
            f"""
SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return {retrieve_task_by_id(typed_row(row, 0, int)) for row in query.fetchall()}

    @cached_and_invalidated
    def get_subtasks(self) -> set["Task"]:
        query = db.execute(
            f"""
SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
            """
        )
        return {retrieve_task_by_id(typed(required_task, int)) for required_task in query.fetchall()}

    @cached_and_invalidated
    def get_primary_activity_id(self) -> int | None:
        query = db.execute(
            f"""
        SELECT primary_activity_id FROM tasks WHERE id={self.id}
        """
        )

        return typed_row(query.fetchone(), 0, int | None, default=None)

    @cached_and_invalidated
    def get_secondary_activity_id(self) -> int | None:
        query = db.execute(
            f"""
        SELECT secondary_activity_id FROM tasks WHERE id={self.id}
        """
        )
        return typed_row(query.fetchone(), 0, int | None, default=None)

    @cached_and_invalidated
    def get_primary_activity_name(self) -> str:
        if (activity := self.get_primary_activity_id()) is None:
            return ""
        query = db.execute(
            f"""
        SELECT name FROM activities WHERE activity_id={activity};
        """
        )
        return typed_row(query.fetchone(), 0, str, default="")

    @cached_and_invalidated
    def get_secondary_activity_name(self) -> str:
        if (activity := self.get_secondary_activity_id()) is None:
            return ""
        query = db.execute(
            f"""
        SELECT name FROM activities WHERE activity_id={activity};
        """
        )
        return typed_row(query.fetchone(), 0, str, default="")


def retrieve_task_by_id(db, ID: int) -> Task:
    query = db.execute(
        f"""
SELECT id, do, notes, deleted, draft, inactive, done, primary_activity_id, secondary_activity_id, space_id, priority, level_id, adjust_time_spent, difficulty, fear, embarrassment, last_checked, workload, ilk FROM tasks WHERE id == {ID};
    """
    )
    res = query.fetchone()
    assert res is not None, breakpoint()
    return Task(*res)


@use.woody_logger
@cached_and_invalidated
def retrieve_tasks(db) -> list[Task]:
    """Load all tasks from the database."""
    query = db.execute(
        """
        SELECT id, do, notes, deleted, draft, inactive, done, primary_activity_id, secondary_activity_id, space_id, priority, level_id, adjust_time_spent, difficulty, fear, embarrassment, last_checked, workload, ilk FROM tasks;
    """
    )

    return [
        Task(
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
