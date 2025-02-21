from __future__ import annotations

import json
from collections import namedtuple
from datetime import datetime
from enum import Enum
from typing import Any, Generator, NamedTuple, Self

import numpy as np
from beartype import BeartypeConf, beartype

from src import app, config, db
from src.helpers import (
    cached_func_static,
    cached_getter,
    cached_property,
    typed,
    typed_row,
)

conf = BeartypeConf(is_pep484_tower=False)

last_sql_access = 0
# * enum numbering starts with 1!
ILK = Enum("TaskType", "task habit tradition routine")


class LEVEL(Enum):
    MUST_NOT = -2
    SHOULD_NOT = -1
    MAY = 0
    SHOULD = 1
    MUST = 2


class EVERY(Enum):
    undetermined = -1
    minute = 1
    hour = 2
    day = 3
    week = 4
    month = 5
    year = 6


class ACTIVITY(Enum):
    unspecified = -1  # when the user didn't make up their mind yet
    undefined = 0  # when it's really none of the above, specifically
    MIND = 1
    BODY = 2
    SOUL = 3


Every = namedtuple("Every", "every_ilk x_every per_ilk x_per")


class Skill(NamedTuple):
    id: int

    @cached_property
    def time_spent(self) -> int:
        query = db.execute(f"""SELECT task_id from task_trains_skill where skill_id={self.id}""")
        tasks = (app.tasks[ID] for (ID,) in query.fetchall())
        return sum(
            task.time_spent for task in tasks if not task.deleted and not task.draft and not task.inactive
        )


@beartype(conf=conf)
class Space:
    __slots__ = (
        "space_id",
        "name",
        "priority",
        "primary_activity_id",
        "secondary_activity_id",
        "inactive",
    )

    def __init__(self, **kwargs) -> None:
        self.space_id: int | None = None
        self.name: str | None = None
        self.priority: float = 0
        self.primary_activity_id: int | None = None
        self.secondary_activity_id: int | None = None
        self.inactive: bool = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_id(cls, ID: int) -> Space | None:
        return retrieve_space_by_id(ID)

    @classmethod
    def from_json(cls, json_str: str) -> Space:
        return cls(**json.loads(json_str))

    @cached_property
    def primary_activity(self) -> ACTIVITY:
        """Get the primary activity of the space if not set."""
        return ACTIVITY(self.primary_activity_id) if self.primary_activity_id else ACTIVITY.unspecified

    @cached_property
    def secondary_activity(self) -> ACTIVITY:
        """Get the secondary activity of the space if not set."""
        return ACTIVITY(self.secondary_activity_id) if self.secondary_activity_id else ACTIVITY.unspecified

    @cached_property
    def number_of_tasks(self) -> int:
        """Get the number of tasks in the space."""
        return db.execute(
            """
            SELECT COUNT(*) FROM tasks WHERE space_id=?;
            """,
            (self.space_id,),
        ).fetchone()[0]


@cached_getter
def retrieve_space_by_id(ID: int | None, db=db) -> Space | None:
    """Retrieve a space from the database by its ID.

    Args:
        ID (int | None): The ID of the space to retrieve.
        db (sqlite3.Connection): The database connection to use.

    Returns:
        Space | None: The space with the given ID, or None if no such space exists.
    """
    if ID is None:
        return None
    query = db.execute(f"SELECT {', '.join(Space.__slots__)} FROM spaces WHERE space_id == {ID};")
    res = query.fetchone()
    assert res is not None, breakpoint()
    kwargs = dict(zip(Space.__slots__, res))
    return Space(**kwargs)


@beartype(conf=conf)
class Task:
    __slots__ = (
        "id",
        "do",
        "deleted",
        "draft",
        "inactive",
        "done",
        "space_id",
        "priority",
        "level_id",
        "adjust_time_spent",
        "difficulty",
        "fear",
        "embarrassment",
        "last_checked",
        "ilk",
        "notes",
    )

    @staticmethod
    def clean_orphaned_tasks():
        """Clean up orphaned task references in the database."""
        orphaned_tasks = db.execute(
            """
            SELECT required_task FROM task_requires_task
            WHERE required_task NOT IN (SELECT id FROM tasks)
            UNION
            SELECT task_of_concern FROM task_requires_task
            WHERE task_of_concern NOT IN (SELECT id FROM tasks)
            """
        ).fetchall()

        for (orphaned_task,) in orphaned_tasks:
            db.execute(
                "DELETE FROM task_requires_task WHERE required_task=? OR task_of_concern=?",
                (orphaned_task, orphaned_task),
            )
        db.commit()

    def __init__(self, **kwargs):
        Task.clean_orphaned_tasks()
        for name, value in kwargs.items():
            self.set_(name, value, to_db=False)

    @cached_property
    def repeats(self) -> Every[EVERY, int] | None:
        """
        Return the repeats for this task.

        Returns:
            Every[EVERY, int] | None: Returns a namedtuple Every for EVERY unit of time,
                                      ints of unit, per EVERY unit of time, ints of unit.
        """
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

    @cached_property
    def constraints(self) -> np.ndarray | None:
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

    @cached_property
    def space_priority(self) -> float:
        return self.space.priority if self.space else 0

    @cached_property
    def space(self) -> Space | None:
        return retrieve_space_by_id(self.space_id)

    @cached_property
    def time_spent(self) -> int:
        """Return the time spent on this task in seconds from all sessions."""
        query = db.execute(f"""SELECT start, stop, pause_time FROM sessions WHERE task_id={self.id}""")
        return sum((stop - start) - pause_time for start, stop, pause_time in query.fetchall())

    @cached_property
    def printable_percentage(self) -> str:
        """Return the percentage of the task that is done as a printable str."""
        return f"{(self.time_spent / self.workload) * 100:.2}%" if self.workload else ""

    @cached_property
    def deadline(self) -> float:
        return min([task.deadline for task in self.doable_supertasks] + [self.own_deadline]) - (
            self.workload or 0
        )

    @cached_getter
    def is_overdue(self, /, *, now: datetime) -> bool:
        return (
            self.own_deadline != float("inf")
            and datetime.fromtimestamp(self.deadline) < now
            and not self.done
            and not self.deleted
            and not self.draft
            and not self.inactive
        )

    @cached_getter
    def is_open(self) -> bool:
        return not self.done and not self.deleted and not self.draft and not self.inactive

    @cached_property
    def printable_deadline(self) -> str:
        return (
            f"{datetime.fromtimestamp(self.deadline).strftime('%d/%m/%Y')}"
            if self.deadline != float("inf")
            else ""
        )

    @cached_property
    def own_deadline(self) -> float:
        query = db.execute(
            f"""
        SELECT time_of_reference FROM deadlines WHERE task_id={self.id}
        """
        )
        return typed_row(query.fetchone(), 0, float, default=float("inf"))

    @cached_property
    def time_buffer(self) -> float:
        """Calculate how much time is left for a task to complete.
        Considering deadline and workload and constraints."""
        if self.deadline == float("inf"):
            return float("inf")

        now = datetime.now()

        if self.constraints is None:
            return (self.deadline - now.timestamp()) - self.workload

        deadline = datetime.fromtimestamp(self.deadline)
        days_until_deadline = (deadline - now).days
        rest = (deadline - now).days % 7
        weeks = (days_until_deadline // 7) + (1 if rest else 0)

        timeslots_until_deadline = np.tile(self.constraints, (weeks, 1))

        return np.sum(timeslots_until_deadline[:days_until_deadline]) * 5 - self.workload

    @cached_property
    def workload(self) -> int:
        """Workload in minutes."""
        query = db.execute("SELECT workload FROM tasks WHERE id=?", (self.id,))
        return typed_row(query.fetchone(), 0, int, default=0)

    def set_deadline(self, deadline: float) -> None:
        """Sets the deadline for a task.

        If deadline is set to infinity, the deadline is removed from the database.
        If the deadline already exists, it is updated with the new deadline.
        If the deadline does not exist, a new deadline is created in the database.

        Args:
            deadline (float): The deadline to be set for the task.

        Returns:
            None

        Raises:
            AssertionError: If deadline is not a float.
            AssertionError: If deadline is negative.

        Examples:
            >>> task = Task()
            >>> task.set_deadline(10.0)
            >>> task.set_deadline(float("inf"))
            >>> task.set_deadline(-1.0)
            Traceback (most recent call last):
                ...
            AssertionError: Deadline cannot be negative.
        """
        assert isinstance(deadline, float), "Deadline must be a float."
        assert deadline >= 0, "Deadline cannot be negative."

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

    @cached_property
    def supertasks(self) -> set[Task]:
        query = db.execute(
            f"""
SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return {app.tasks[typed_row(row, 0, int)] for row in query.fetchall()}

    @cached_property
    def skill_ids(self) -> list[int]:
        query = db.execute(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id}
        """
        )
        return [Skill(typed_row(skill_id, 0, int)) for skill_id in query.fetchall()]

    def set_adjust_time_spent(self, value: int) -> None:
        self.set_("adjust_time_spent", value)

    @cached_property
    def doable_supertasks(self) -> set[Task]:
        return {
            task for task in self.supertasks if not (task.done or task.deleted or task.inactive or task.draft)
        }

    @cached_property
    def total_time_spent(self) -> int:
        """Return the time spent on this task in seconds, including adjustment."""
        return self.adjust_time_spent + self.time_spent

    def get_total_priority(self, priority: float = None, space_priority: float = None) -> float:
        """
        Calculates the total priority of the task, taking into account its own priority, space priority,
        and the priority of its subtasks.

        Args:
            priority (float, optional): The priority of the task. Defaults to None.
            space_priority (float, optional): The space priority of the task. Defaults to None.

        Returns:
            float: The total priority of the task.

        Raises:
            None

        Examples:
            >>> task = Task()
            >>> task.get_total_priority()
            1.0
        """
        own_priority = (self.priority if priority is None else priority) + (
            self.space_priority if space_priority is None else space_priority
        )

        max_supertask = max(
            self.doable_supertasks,
            key=lambda t: t.get_total_priority(),
            default=None,
        )
        sibling_priorities = (
            {t.priority for t in max_supertask.subtasks} if max_supertask else {self.priority}
        )
        normalized = own_priority / max(sibling_priorities | {1})  # set(1) if no siblings
        return (normalized + max_supertask.get_total_priority()) if max_supertask else own_priority

    @cached_property
    def is_doable(self) -> bool:
        self_doable = not self.deleted and not self.draft and not self.inactive and not self.done
        # what about supertasks?
        return self_doable and not any(s.is_doable for s in self.subtasks)

    def get_short_do(self, max_len: int = None) -> str:
        """
        Get the first line of the do, or the first line truncated to max_len.

        Args:
            max_len (int): The maximum length of the returned string.

        Returns:
            str: The first line of the do, or the first line truncated to max_len.

        Examples:
            >>> todo = Todo("do this", "do that")
            >>> todo.get_short_do()
            'do this'
            >>> todo.get_short_do(max_len=5)
            'do th'
        """
        lines = self.do.split("\n")
        if not max_len:
            return lines[0] + ("" if len(lines) == 1 else " […]")
        line = lines[0][:max_len]

        return line + ("" if len(lines) == 1 else " […]")

    def delete(self) -> None:
        self.set_("deleted", True)

    def really_delete(self) -> None:
        db.execute(
            f"""
        DELETE FROM tasks WHERE id={self.id}
        """
        )
        db.commit()
        del app.tasks[self.id]

    @cached_property
    def resources(self) -> list[tuple[str, int]]:
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

    @cached_property
    def level(self) -> str:
        actual_level = max(t.level_id for t in self.doable_supertasks | {self})
        return get_level_name(actual_level)

    @cached_property
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
        return typed(query.fetchone(), int, default=0)

    @cached_property
    def primary_activity(self) -> ACTIVITY:
        """
        Get the primary activity for the task and default to the activity of the space if not set.

        Returns:
            ACTIVITY: ACTIVITY enum value
        """
        query = db.execute(
            "SELECT primary_activity_id FROM tasks WHERE id=?",
            (self.id,),
        )
        own_activity_id = typed_row(
            query.fetchone(),
            0,
            int,
            default=ACTIVITY.unspecified.value,
        )
        own_activity = ACTIVITY(own_activity_id)
        space_activity = self.space.primary_activity if self.space else ACTIVITY.unspecified

        return space_activity if self.space else own_activity

    @cached_property
    def secondary_activity(self) -> ACTIVITY:
        """Get the secondary activity for the task and default to the activity of the space if not set."""
        if own_activity := db.execute(
            "SELECT secondary_activity_id FROM tasks WHERE id=?",
            (self.id,),
        ).fetchone()[0]:
            return ACTIVITY(own_activity)
        else:
            return self.space.secondary_activity if self.space else ACTIVITY.unspecified

    @cached_property
    def primary_color(self) -> str:
        match self.primary_activity:
            case ACTIVITY.MIND:
                return config.activity_color_mind
            case ACTIVITY.BODY:
                return config.activity_color_body
            case ACTIVITY.SOUL:
                return config.activity_color_soul
            case ACTIVITY.unspecified:
                return "black"

    @cached_property
    def secondary_color(self) -> str:
        match self.secondary_activity:
            case ACTIVITY.MIND:
                return config.activity_color_mind
            case ACTIVITY.BODY:
                return config.activity_color_body
            case ACTIVITY.SOUL:
                return config.activity_color_soul
            case ACTIVITY.unspecified:
                return "black"

    @cached_property
    def subtasks(self) -> set[Task]:
        """Returns a set of subtasks that are required to complete this task."""
        query = db.execute(
            f"""
            SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
            """
        )
        ids = [typed_row(row, 0, int) for row in query.fetchall() if row is not None]
        return {app.tasks[id_] for id_ in ids}

    def set_subtasks(self, tasks: set[Task]) -> None:
        db.executemany(
            "INSERT INTO task_requires_task (task_of_concern, required_task) VALUES (?, ?)",
            [(self.id, t.id) for t in tasks],
        )
        db.commit()

    def set_supertasks(self, tasks: set[Task]) -> None:
        db.executemany(
            "INSERT INTO task_requires_task (task_of_concern, required_task) VALUES (?, ?)",
            [(t.id, self.id) for t in tasks],
        )
        db.commit()

    def set_primary_activity(self, activity: ACTIVITY) -> None:
        self.set_("primary_activity_id", activity.value)

    def set_last_checked(self, time_: float) -> None:
        self.set_("last_checked", time_)

    def set_[T](self, name: str, value: T, to_db: bool = True) -> T:
        if to_db:
            db.execute(
                f"UPDATE tasks SET {name}=? WHERE id={self.id}",
                (value,),
            )
            db.commit()
        object.__setattr__(self, name, value)

        return value

    def __str__(self) -> str:
        return f"""
# {self.space}
## Task({self.id})
- {self.do}
- {self.get_status_text()}
- {self.level}
- {self.priority}
- {self.primary_activity}
- {self.secondary_activity}
"""

    def __repr__(self) -> str:
        return f"Task(**{ {k: getattr(self, k) for k in Task.__slots__} })"

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in Task.__slots__} | {"space": self.space.name}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __setattr__(self, name: str, value: Any) -> None:
        print(f"attempted assignment to read-only attribute {name}={value}")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Task) and all(getattr(self, k) == getattr(other, k) for k in Task.__slots__)

    def __hash__(self) -> int:
        return self.id

    def __iter__(self) -> Generator[tuple[str, Any], None, None]:
        for k in self.__slots__:
            yield k, getattr(self, k)

    @classmethod
    def from_id(cls, ID: int) -> Task:
        return app.tasks[ID] if ID in app.tasks else _retrieve_task_by_id(ID)

    def reload(self) -> Self:
        """Reload the task from the database.

        Args:
            None

        Returns:
            Task: The task itself.

        Examples:
            >>> task = Task(id=1)
            >>> task.reload()
            <Task(id=1, name='Task 1', ...)>
        """
        new = _retrieve_task_by_id(self.id)
        for k in self.__slots__:
            self.set_(k, getattr(new, k), to_db=False)
        print(repr(self))
        for win in app.list_of_task_lists + app.list_of_task_organizers:
            win.build_task_table()
        return self

    def get_status(self) -> tuple[bool, bool, bool, bool]:
        return (
            not self.done,
            not self.draft,
            not self.inactive,
            not self.deleted,
        )

    def get_status_text(self) -> str:
        return f"""{"done" if self.done else "not done"}
{"draft" if self.draft else "not draft"}
{"inactive" if self.inactive else "active"}
{"deleted" if self.deleted else "not deleted"}"""


class TaskDict(dict):
    def __missing__(self, key):
        value = Task.from_id(key)
        self[key] = value
        return value


class SpaceDict(dict):
    def __missing__(self, key):
        value = Space.from_id(key)
        self[key] = value
        return value


class SkillDict(dict):
    def __missing__(self, key):
        value = Skill.from_id(key)
        self[key] = value
        return value


def _retrieve_task_by_id(ID: int) -> Task:
    """Load a task directly from the database by its ID."""
    query = db.execute(f"SELECT {', '.join(Task.__slots__)} FROM tasks WHERE id == {ID};")
    res = query.fetchone()
    assert res is not None, breakpoint()
    kwargs = dict(zip(Task.__slots__, res))
    return Task(**kwargs)


@cached_func_static
@beartype
def retrieve_tasks() -> list[Task]:
    """Load all tasks from the database."""
    query = db.execute(f"SELECT {', '.join(Task.__slots__)} FROM tasks;")
    return [Task(**dict(zip(Task.__slots__, res))) for res in query.fetchall()]


@cached_func_static
@beartype
def retrieve_spaces() -> list[Space]:
    """Load all spaces from the database."""
    query = db.execute(f"SELECT {', '.join(Space.__slots__)} FROM spaces;")
    return [Space(**dict(zip(Space.__slots__, res))) for res in query.fetchall()]


@cached_getter
@beartype
def get_level_name(level_id: int) -> str:
    query = db.execute(
        f"""
SELECT name FROM levels WHERE level_id={level_id};
"""
    )
    return typed_row(query.fetchone(), 0, str)
