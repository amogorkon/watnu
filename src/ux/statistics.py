import sqlite3
from datetime import datetime
from inspect import currentframe, getframeinfo
from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QFont, QFontDatabase, QIcon

_translate = QCoreApplication.translate

import ui
from classes import Task, cached_and_invalidated, type_check_result

from .stuff import __version__, app, config, db

con = sqlite3.connect(config.db_path)

ok = QIcon("./extra/feathericons/check.svg")
nok = QIcon("./extra/feathericons/x.svg")


class Statistics(QtWidgets.QDialog, ui.statistics.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        res = con.execute("select max(id) from tasks")
        self.total_num_tasks.setText(str(type_check_result(res.fetchone(), 0, int, default=0)))

        res = con.execute("SELECT space_id, name FROM spaces")
        for i, (space_id, name) in enumerate(res.fetchall()):
            self.space_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, space_id)
            self.space_stats.setItem(i, 0, item)

            inner_query = con.execute(
                f"""SELECT count(id) FROM tasks WHERE space_id == {space_id} 
                AND done 
                AND NOT deleted 
                AND NOT inactive 
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(
                str(type_check_result(inner_query.fetchone(), 0, int, default=0))
            )
            self.space_stats.setItem(i, 1, item)
            inner_query = con.execute(
                f"""SELECT count(id) FROM tasks WHERE space_id == {space_id} 
                AND NOT done 
                AND NOT deleted 
                AND NOT inactive 
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(
                str(type_check_result(inner_query.fetchone(), 0, int, default=0))
            )
            self.space_stats.setItem(i, 2, item)

            inner_query = con.execute(
                f"""SELECT count(id) FROM tasks WHERE space_id == {space_id} 
                AND NOT deleted 
                AND NOT inactive 
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(
                str(type_check_result(inner_query.fetchone(), 0, int, default=0))
            )
            self.space_stats.setItem(i, 3, item)

        for i, (level_id, name) in enumerate(
            ((-2, "MUST NOT"), (-1, "SHOULD NOT"), (0, "COULD"), (1, "SHOULD"), (2, "MUST"))
        ):
            self.level_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, space_id)
            self.level_stats.setItem(i, 0, item)
            inner_query = con.execute(
                f"""SELECT count(id) FROM tasks WHERE level_id == {level_id} 
                AND done 
                AND NOT 
                deleted 
                AND NOT inactive 
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(
                str(type_check_result(inner_query.fetchone(), 0, int, default=0))
            )
            self.level_stats.setItem(i, 1, item)

            inner_query = con.execute(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND NOT done AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(
                str(type_check_result(inner_query.fetchone(), 0, int, default=0))
            )
            self.level_stats.setItem(i, 2, item)

            inner_query = con.execute(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(
                str(type_check_result(inner_query.fetchone(), 0, int, default=0))
            )
            self.level_stats.setItem(i, 3, item)

        query = con.execute(
            """
SELECT
session_id, task_id, start, stop, finished, pause_time
FROM
sessions                           
"""
        )

        for i, (session_id, task_id, start, stop, finished, pause_time) in enumerate(
            (
                type_check_result(row, 0, int),
                type_check_result(row, 1, int),
                type_check_result(row, 2, int),
                type_check_result(row, 3, int),
                type_check_result(row, 4, int),
                type_check_result(row, 5, int),
            )
            for row in query.fetchall()
        ):
            inner_query = con.execute(
                f"""
SELECT
    do
FROM
    tasks
WHERE
    id == {task_id}
"""
            )
            # sanitizing..
            row = inner_query.fetchone()
            if row is None:
                """
                DELETE FROM
                sessions  WHERE
                id == {task_id}"""
                continue
            self.session_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(type_check_result(row, 0, str, default="", debugging=True))
            item.setData(Qt.ItemDataRole.UserRole, session_id)
            self.session_stats.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(start)))
            self.session_stats.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(stop)))
            self.session_stats.setItem(i, 2, item)
            item = QtWidgets.QTableWidgetItem()
            item.setIcon(ok if finished else nok)
            self.session_stats.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(f"{(stop - start) // 60:04}")
            self.session_stats.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(f"{pause_time // 60:04}")
            self.session_stats.setItem(i, 5, item)
