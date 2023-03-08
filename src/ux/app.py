from PyQt6 import QtWidgets

import q
import ui
from classes import EVERY, ILK, Every, Task, cached_and_invalidated, iter_over, submit_sql, typed


class Application(QtWidgets.QApplication):
    """Main Application logic."""
    def __init__(self, argv):
        super().__init__(argv)

    def mouseMoveEvent(self, event):
        event.ignore()
        return False

    @cached_and_invalidated
    def considered_tasks(self) -> list[Task]:
        query = submit_sql(
            """
    SELECT id FROM tasks
    WHERE deleted != TRUE AND draft != TRUE AND inactive != TRUE
    ;
    """
        )
        return [Task(row(0)) for row in iter_over(query)]

    def write_session(self, task_id, start, stop, finished=False, pause_time=0):
        query = submit_sql(
            f"""
            INSERT INTO sessions (task_id, start, stop, pause_time, finished)
            VALUES ('{task_id}', {int(start)}, {int(stop)}, {pause_time}, {finished})
            """
        )

    def sanitize_db(self):
        query = submit_sql(
            """
    SELECT r.resource_id
    FROM resources r
    LEFT JOIN task_uses_resource
    ON task_uses_resource.resource_id = r.resource_id
    WHERE task_uses_resource.task_id is NULL
    """
        )
        i = None
        for i, row in enumerate(iter_over(query)):
            submit_sql(
                f"""
    DELETE FROM resources
    WHERE resource_id = {row(0)}
    """
            )
        q(i + 1 if i is not None else "Nothing found, so no", "unused resources deleted.")
