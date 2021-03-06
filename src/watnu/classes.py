import sys
from collections import namedtuple
from collections.abc import Generator
from enum import Enum, Flag
from functools import wraps
from inspect import currentframe, getframeinfo
from pathlib import Path
from shlex import split
from time import time
from types import MethodType
from typing import NamedTuple

import numpy as np
from PyQt5.QtSql import QSqlQuery

import q
from lib.utils import ASPECT, aspectized

last_sql_access = 0

ILK = Enum("TaskType", "task habit tradition routine")  # * enum numbering starts with 1!
class EVERY(Enum):
    undetermined = -1
    minute = 1
    hour = 2
    day = 3
    week = 4
    month = 5
    year = 6

Every = namedtuple("Every", "every_ilk x_every per_ilk x_per")

def set_globals(c):
    global config
    config = c

def iter_over(query):
    if query.isValid():
        yield query.value
    while query.next():
        yield query.value

def cached(func):
    cache = {}  # (args[0] -> (last_called, result)
    
    def wrapper(*args, **kwargs):
        global last_sql_access
        nonlocal cache
        try:
            if cache[args[0]][0] <= last_sql_access:
                res = func.fget(*args, **kwargs)
                cache[args[0]] = time(), res
                return res
            return cache[args[0]][1]
        except KeyError:
            res = func.fget(*args, **kwargs)
            cache[args[0]] = time(), res
            return res
    return wrapper

def typed(row, idx, kind: type, default=..., debugging=False):
    if config.debugging:
        debugging = True
    filename, line_number, function_name, lines, index = getframeinfo(currentframe().f_back)
    filename = Path(filename).stem
    res = row(idx)
    if debugging:
        
        q(filename, line_number, function_name, idx, kind, default, res)
    if default is not ...:
        if res == "" or res is None:
            return default
        assert type(res) is kind or res is None, f"'{res}' ({type(res)}) is not {kind}! {filename, line_number, function_name}"
        return res
    else:
        assert type(res) is kind, f"'{res}' ({type(res)}) is not {kind}! {filename, line_number, function_name}"
    return res

def submit_sql(statement, debugging=False):
    if config.debugging:
        debugging = True
    query = QSqlQuery()
    (filename, line_number, function_name, lines, index) = getframeinfo(
            currentframe().f_back
        )
    if query.exec_(statement):
        if debugging:
            q("OK", statement)
    else:
        q(
            f"SQL failed {Path(filename).stem, line_number, function_name}: {statement}"
        )
        q(query.lastError().text())
    query.first()
    if not query.isValid() and debugging:
        q(
            f"SQL succeeded but Query is now invalid {Path(filename).stem, line_number, function_name}: {statement}"
        )
    global last_sql_access
    last_sql_access = time() -1
    return query


class Skill(NamedTuple):
    id: int

    @property
    def time_spent(self):
        query = submit_sql(
            f"""
SELECT time_spent, adjust_time_spent
FROM tasks
INNER JOIN task_trains_skill
ON tasks.id = task_trains_skill.task_id
WHERE skill_id = {self.id} AND NOT (deleted OR draft or inactive)
"""
        )
        return sum(typed(row, 0, int) + typed(row, 1, int) for row in iter_over(query))

@aspectized(cached, ASPECT.property_get)
class Task(NamedTuple):
    id: int

    @property
    def activity(self) -> str:
        if self.primary_activity_id is None:
            return ""
        else:
            query = submit_sql(
                f"""
            SELECT name FROM activities WHERE activity_id={self.primary_activity_id};
            """
            )
        return typed(query.value, 0, str, default="")

    @property
    def adjust_time_spent(self) -> int:
        query = submit_sql(
            f"""
        SELECT adjust_time_spent FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int)

    @adjust_time_spent.setter
    def adjust_time_spent(self, value) -> None:
        query = submit_sql(
            f"""
        UPDATE tasks SET adjust_time_spent={value} 
        WHERE id={self.id}
        """
        )

    @property
    def considered_open(self) -> bool:
        if self.is_deleted or self.is_draft or self.is_inactive or self.is_done:
            return False
        return not any(t.considered_open for t in self.requires)

    @property
    def constraints(self) -> np.ndarray:
        query = submit_sql(
            f"""
SELECT flags FROM constraints WHERE task_id = {self.id}
        """
        )
        if query.isValid():
            return np.fromiter((int(x) for x in typed(query.value, 0, str)), int).reshape(7,144)
        else:
            return None

    @property
    def do(self) -> str:
        query = submit_sql(
            f"""
        SELECT do FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, str)

    @property
    def difficulty(self) -> float:
        query = submit_sql(
            f"""
        SELECT difficulty FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, float)

    @property
    def deadline(self) -> float:
        query = submit_sql(
            f"""
        SELECT time_of_reference FROM deadlines WHERE task_id={self.id}
        """)
        if query.isValid():  #  # !WTF QSqlQuery::value: not positioned on a valid record ?!
        # the reason for aspectized and still couldn't figure out what makes this a special case
            own_deadline = typed(query.value, 0, float, default=float("inf")) 
        else:
            own_deadline = float("inf")
        query = submit_sql(
            f"""
        SELECT workload FROM tasks WHERE id={self.id}
        """
        )
        workload = typed(query.value, 0, int, default=0)
        return min([t.deadline for t in self.required_by] + [own_deadline]) - workload

    @property
    def embarassment(self) -> float:
        query = submit_sql(
            f"""
        SELECT embarassment FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, float)
    
    @property
    def fear(self) -> float:
        query = submit_sql(
            f"""
        SELECT fear FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, float)

    @property
    def ilk(self):
        query = submit_sql(f"""
SELECT ilk FROM tasks WHERE id={self.id}
                           """)
        return ILK(typed(query.value, 0, int))

    @property
    def is_draft(self) -> bool:
        query = submit_sql(
            f"""
        SELECT draft FROM tasks WHERE id={self.id}
        """
        )
        return bool(typed(query.value, 0, int))

    @property
    def is_inactive(self) -> bool:
        query = submit_sql(
            f"""
        SELECT inactive FROM tasks WHERE id={self.id}
        """
        )
        return bool(typed(query.value, 0, int))

    @property
    def is_deleted(self) -> bool:
        query = submit_sql(
            f"""
        SELECT deleted FROM tasks WHERE id={self.id}
        """
        )
        return bool(typed(query.value, 0, int))
    
    @property
    def is_done(self) -> bool:
        query = submit_sql(
            f"""
SELECT done FROM tasks where id={self.id}
        """
        )
        return typed(query.value, 0, int)

    @is_done.setter
    def is_done(self, value) -> None:
        query = submit_sql(
            f"""
UPDATE tasks
SET done={value} 
WHERE id={self.id}
        """
        )

    @property
    def level_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT level_id FROM tasks WHERE id={self.id};
        """
        )
        own_level = typed(query.value, 0, int)
        # recursion!
        return max([t.level_id for t in self.required_by] + [own_level])

    @property
    def last_checked(self) -> int:
        query = submit_sql(
            f"""
        SELECT last_checked FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int)

    @last_checked.setter
    def last_checked(self, value) -> None:
        submit_sql(
            f"""
        UPDATE tasks SET last_checked={int(value)} 
        WHERE id={self.id}
        """
        )
        return

    @property
    def last_finished(self) -> int:
        query = submit_sql(
            f"""
        SELECT stop
        FROM sessions
        WHERE task_id == {self.id} AND finished == TRUE
        ORDER BY
            stop DESC
        ;
        """
        )
        if not query.isValid():
            return 0
        return typed(query.value, 0, int, default=0)

    @property
    def level(self) -> str:
        query = submit_sql(
            f"""
        SELECT name FROM levels WHERE level_id={self.level_id};
        """
        )
        return typed(query.value, 0, str)

    @property
    def notes(self) -> str:
        query = submit_sql(
            f"""
        SELECT notes FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, str, default=None)

    @property
    def priority(self) -> float:
        query = submit_sql(
            f"""
        SELECT priority FROM tasks WHERE id={self.id}
        """
        )
        own_priority = typed(query.value, 0, float)
        parent_priorities = max((t.priority for t in self.required_by), default=0)

        return own_priority + parent_priorities

    @property
    def primary_activity_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT primary_activity_id FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int, default=None)

    @property
    def requires(self) -> list:
        query = submit_sql(
            f"""
        SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
        """
        )
        return [Task(typed(row, 0, int)) for row in iter_over(query)]

    @property
    def required_by(self):
        query = submit_sql(
            f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return [Task(typed(row, 0, int)) for row in iter_over(query)]

    @property
    def repeats(self):
        query = submit_sql(f"""
SELECT every_ilk, x_every, per_ilk, x_per  FROM repeats WHERE task_id={self.id}
                           """)
        if not query.isValid():
            return None
        else:
            return Every(EVERY(typed(query.value, 0, int,)),
                        typed(query.value, 1, int), 
                        EVERY(typed(query.value, 2, int)), 
                        typed(query.value, 3, int,),
                        )

    @property
    def resources(self) -> Generator[str]:
        query = submit_sql(
            f"""
SELECT resources.url, resources.resource_id
FROM resources
INNER JOIN task_uses_resource
ON resources.resource_id= task_uses_resource.resource_id
INNER JOIN tasks
ON task_uses_resource.task_id = tasks.id
WHERE tasks.id = {self.id}
        """
        )
        for row in iter_over(query):
            yield typed(row, 0, str), typed(row, 1, int)

    @property
    def secondary_activity(self) -> str:
        if not self.secondary_activity_id:
            return ""
        query = submit_sql(
            f"""
        SELECT name FROM activities WHERE activity_id={self.secondary_activity_id};
        """
        )
        return typed(query.value, 0, str, default=None)

    @property
    def space(self) -> str:
        query = submit_sql(
            f"""
        SELECT name FROM spaces WHERE space_id={self.space_id};
        """
        )
        return typed(query.value, 0, str, default=None)

    @property
    def skill_ids(self) -> list[int]:
        query = submit_sql(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id};
        """
        )
        return [typed(row, 0, int) for row in iter_over(query)]

    @property
    def space_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT space_id FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int, default=None)


    @property
    def secondary_activity_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT secondary_activity_id FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int, default=None)

    @property
    def skills(self) -> list[int]:
        query = submit_sql(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id}
        """
        )
        return [Skill(typed(row, 0, int)) for row in iter_over(query)]


    @property
    def space_priority(self) -> float:
        if self.space_id:
            query = submit_sql(
                f"""
            SELECT priority FROM spaces WHERE space_id={self.space_id};
            """
            )
            return typed(query.value, 0, float)
        else:
            return 0
        
    @property
    def subtasks(self) -> "list[Task]":
        query = submit_sql(f"""
SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
            """)
        return [Task(typed(row, 0, int)) for row in iter_over(query)]
    
    @property
    def supertasks(self) -> "list[Task]":
        query = submit_sql(f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """)
        return [Task(typed(row, 0, int)) for row in iter_over(query)]

    @property
    def time_spent(self) -> int:
        query = submit_sql(
            f"""
        SELECT time_spent FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int)

    @time_spent.setter
    def time_spent(self, value) -> None:
        submit_sql(
            f"""
        UPDATE tasks SET time_spent={int(value)} 
        WHERE id={self.id}
        """
        )

    @property
    def total_time_spent(self) -> int:
        return self.adjust_time_spent + self.time_spent

    @property
    def template(self):
        query = submit_sql(f"""
SELECT template FROM tasks WHERE id={self.id}
""")
        return typed(query.value(), 0, int, default=None)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def workload(self) -> int:
        query = submit_sql(
            f"""
        SELECT workload FROM tasks WHERE id={self.id}
        """
        )
        return typed(query.value, 0, int, default=None)
