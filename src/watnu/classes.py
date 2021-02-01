from collections.abc import Generator
from inspect import currentframe, getframeinfo
from pathlib import Path
from shlex import split
from typing import NamedTuple

import numpy as np
from PyQt5.QtSql import QSqlQuery


def set_globals(c, l):
    global config, logger
    config = c
    logger = l


def iter_over(query):
    while query.next():
        yield query.value


def submit_sql(statement, debugging=False):
    query = QSqlQuery()
    if query.exec_(statement):
        if debugging:
            print("OK", statement)
    else:
        (filename, line_number, function_name, lines, index) = getframeinfo(
            currentframe().f_back
        )
        logger.warning(
            f"SQL failed {Path(filename).stem, line_number, function_name}:" + statement
        )
        logger.warning(query.lastError().text())
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
        return sum(row(0) + row(1) for row in iter_over(query))


class Task(NamedTuple):
    id: int

    @property
    def do(self) -> str:
        query = submit_sql(
            f"""
        SELECT do FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def notes(self) -> str:
        query = submit_sql(
            f"""
        SELECT notes FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def space_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT space_id FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def draft(self) -> bool:
        query = submit_sql(
            f"""
        SELECT draft FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def inactive(self) -> bool:
        query = submit_sql(
            f"""
        SELECT inactive FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def deleted(self) -> bool:
        query = submit_sql(
            f"""
        SELECT deleted FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def workload(self) -> int:
        query = submit_sql(
            f"""
        SELECT workload FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def primary_activity_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT activity_id FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def difficulty(self) -> float:
        query = submit_sql(
            f"""
        SELECT difficulty FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def fear(self) -> float:
        query = submit_sql(
            f"""
        SELECT fear FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def embarassment(self) -> float:
        query = submit_sql(
            f"""
        SELECT embarassment FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def conditions(self) -> str:
        query = submit_sql(
            f"""
        SELECT conditions FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def secondary_activity_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT secondary_activity_id FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

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
            yield row(0), row(1)

    @property
    def habit(self) -> bool:
        query = submit_sql(
            f"""
        SELECT habit FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        return query.value(0)

    @property
    def skills(self) -> list[int]:
        query = submit_sql(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id}
        """
        )
        return [Skill(row(0)) for row in iter_over(query)]

    @property
    def deadline(self) -> int:
        query = submit_sql(
            f"""
        SELECT deadline, workload FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        own_deadline, workload = (
            float(query.value(0)),
            w if (w := query.value(1)) else 0,
        )

        return min([t.deadline for t in self.required_by] + [own_deadline]) - workload

    @property
    def level_id(self) -> int:
        query = submit_sql(
            f"""
        SELECT level_id FROM tasks WHERE id={self.id};
        """
        )
        if query.first():
            own_level = query.value(0)
        else:
            raise AssertionError
        # recursion!
        return max([t.level_id for t in self.required_by] + [own_level])

    @property
    def priority(self) -> float:
        query = submit_sql(
            f"""
        SELECT priority FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        own_priority = query.value(0)
        assert isinstance(own_priority, float), (own_priority, type(own_priority))
        parent_priorities = max((t.priority for t in self.required_by), default=0)

        return own_priority + parent_priorities

    @property
    def space_priority(self) -> float:
        if self.space_id:
            query = submit_sql(
                f"""
            SELECT priority FROM spaces WHERE space_id={self.space_id};
            """
            )
            if not query.next():
                space_priority = 0
                print("space_priority is giving troubles again!")
            else:
                return x if (x := query.value(0)) is not None else 0
        else:
            return 0

    @property
    def constraints(self) -> np.ndarray:
        query = submit_sql(
            f"""
SELECT flags FROM constraints WHERE task_id = {self.id}
        """
        )
        for row in iter_over(query):
            yield np.asarray(list(bool(int(x)) for x in row(0).split()))

    @property
    def last_checked(self) -> int:
        query = submit_sql(
            f"""
        SELECT last_checked FROM tasks WHERE id={self.id}
        """
        )
        query.first()
        x = query.value(0)
        return x

    @last_checked.setter
    def last_checked(self, value) -> None:
        value = int(value)
        submit_sql(
            f"""
        UPDATE tasks SET last_checked={value} 
        WHERE id={self.id}
        """
        )
        return

        return locals()

    @property
    def activity(self) -> str:
        query = submit_sql(
            f"""
        SELECT name FROM activities WHERE activity_id={ID if (ID := self.primary_activity_id) != "" else "NULL"};
        """
        )
        if query.next():
            res = query.value(0)
        else:
            res = ""
        return res

    @property
    def secondary_activity(self) -> str:
        if not self.secondary_activity_id:
            return ""
        query = submit_sql(
            f"""
        SELECT name FROM activities WHERE activity_id={self.secondary_activity_id};
        """
        )
        res = None
        if query.next():
            res = query.value(0)
        return res

    @property
    def space(self) -> str:
        query = submit_sql(
            f"""
        SELECT name FROM spaces WHERE space_id={self.space_id};
        """
        )
        query.next()
        res = query.value(0)
        return res

    @property
    def level(self) -> int:
        query = submit_sql(
            f"""
        SELECT name FROM levels WHERE level_id={self.level_id};
        """
        )
        query.next()
        res = query.value(0)
        return res

    def __time_spent():
        def fget(self) -> int:
            query = submit_sql(
                f"""
            SELECT time_spent FROM tasks WHERE id={self.id}
            """
            )
            query.first()
            x = query.value(0)
            return x

        def fset(self, value) -> None:
            submit_sql(
                f"""
            UPDATE tasks SET time_spent={int(value)} 
            WHERE id={self.id}
            """
            )
            return

        return locals()

    time_spent = property(**__time_spent())
    del __time_spent

    def __done():
        def fget(self) -> bool:
            query = submit_sql(
                f"""
            SELECT done FROM tasks WHERE id={self.id}
            """
            )
            query.first()
            x = query.value(0)
            return x

        def fset(self, value):
            query = submit_sql(
                f"""
            UPDATE tasks SET done={value} 
            WHERE id={self.id}
            """
            )
            return

        return locals()

    done = property(**__done())
    del __done

    @property
    def requires(self) -> list:
        query = submit_sql(
            f"""
        SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
        """
        )
        return [Task(row(0)) for row in iter_over(query)]

    @property
    def required_by(self):
        query = submit_sql(
            f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        )
        return [Task(row(0)) for row in iter_over(query)]

    def __adjust_time_spent():
        def fget(self) -> int:
            query = submit_sql(
                f"""
            SELECT adjust_time_spent FROM tasks WHERE id={self.id}
            """
            )
            query.first()
            return query.value(0)

        def fset(self, value) -> None:
            query = submit_sql(
                f"""
            UPDATE tasks SET adjust_time_spent={value} 
            WHERE id={self.id}
            """
            )
            return

        return locals()

    adjust_time_spent = property(**__adjust_time_spent())
    del __adjust_time_spent

    @property
    def considered_open(self) -> bool:
        if self.deleted or self.draft or self.inactive:
            return False
        return not any(t.considered_open for t in self.requires) and not self.done

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
        if query.next():
            return query.value(0)
        else:
            return 0

    @property
    def total_time_spent(self) -> int:
        return self.adjust_time_spent + self.time_spent

    @property
    def skill_ids(self) -> list[int]:
        query = submit_sql(
            f"""
        SELECT skill_id FROM task_trains_skill WHERE task_id={self.id};
        """
        )
        res = [row(0) for row in iter_over(query)]
        return res

    def __eq__(self, other):
        return self.id == other.id
