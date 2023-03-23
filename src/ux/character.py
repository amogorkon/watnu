import sqlite3
from collections import defaultdict

import use
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

import ui
from classes import Task2, cached_and_invalidated, typed
from logic import retrieve_task_by_id

from .stuff import app, db


class Character(QtWidgets.QDialog, ui.character.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.skills_table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.build_skill_table()

    @cached_and_invalidated
    def build_skill_table(self):
        query = db.execute(
            """
        SELECT skill_id, task_id FROM task_trains_skill;
        """
        )

        self.skills_table.setSortingEnabled(False)

        skills_trained_by = defaultdict(lambda: [])

        for skill_id, task_id in query.fetchall():
            # cleanup while we're at it
            # TODO correct cascade delete
            db.execute(
                f"""
DELETE FROM task_trains_skill WHERE skill_id=={skill_id} AND {task_id} NOT IN (SELECT id FROM tasks);
                """
            )
            check = db.execute("""SELECT * FROM tasks WHERE id==?;""", (task_id,)).fetchone()
            if check is None:
                continue

            skills_trained_by[skill_id].append(task_id)

        for i, skill in enumerate(skills_trained_by):
            query = db.execute(
                f"""
            SELECT name FROM skills WHERE skill_id=={skill};
            """
            )

            self.skills_table.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(query.fetchone()[0])
            self.skills_table.setItem(i, 0, item)
            item.setData(Qt.ItemDataRole.UserRole, skill)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item = QtWidgets.QTableWidgetItem(str(len(skills_trained_by[skill])))
            self.skills_table.setItem(i, 1, item)

            item = QtWidgets.QTableWidgetItem(
                str(
                    sum(retrieve_task_by_id(db, x).get_total_time_spent() for x in skills_trained_by[skill])
                    // (60 * 60)
                )
            )
            self.skills_table.setItem(i, 2, item)

        self.skills_table.setSortingEnabled(True)
        self.update()
