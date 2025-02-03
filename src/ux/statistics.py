from collections import Counter
from datetime import datetime, timedelta
from typing import NamedTuple

import numpy as np
from beartype import beartype
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QIcon

import src.ui as ui
from src import app, config, db
from src.classes import Task, cached_func_static, typed, typed_row

_translate = QCoreApplication.translate


def init_():
    global OK, NOK
    OK = QIcon(str(config.base_path / "extra/feathericons/check.svg"))
    NOK = QIcon(str(config.base_path / "extra/feathericons/x.svg"))


@beartype
class statistics(NamedTuple):
    total_added: int
    total_finished: int
    today_added: int
    today_finished: int
    yesterday_added: int
    yesterday_finished: int
    aggregated_data: np.ndarray


class Statistics(QtWidgets.QDialog, ui.statistics.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        init_()
        from src.ux.task_list import TaskList

        self.gui_timer = QtCore.QTimer()
        self.setup_tabs()

        self.gui_timer.timeout.connect(self.update_gui)

        def open_list_of_tasks(tasks: set[Task]):
            win = TaskList(selected_tasks=tasks)
            win.show()

        self.today_finished_button_label.clicked.connect(
            lambda: open_list_of_tasks(get_tasks_finished_today()())
        )
        self.yesterday_finished_button_label.clicked.connect(
            lambda: open_list_of_tasks(get_tasks_finished_yesterday())
        )
        self.today_added_label.hide()
        self.yesterday_added_label.hide()

    def show(self):
        super().show()
        self.gui_timer.start(100)

    def hide(self):
        super().hide()
        self.gui_timer.stop()

    def update_gui(self):
        stats = collect_statistics()
        self.today_finished_button_label.setEnabled(stats.today_finished > 0)
        self.yesterday_finished_button_label.setEnabled(stats.yesterday_finished > 0)
        self.total_num_tasks_outlabel.setText(str(stats.total_added))
        self.total_finished_outlabel.setText(str(stats.total_finished))
        self.yesterday_finished_outlabel.setText(str(stats.yesterday_finished))
        self.today_finished_outlabel.setText(str(stats.today_finished))

    def setup_tabs(self):
        res = db.execute("SELECT space_id, name FROM spaces")
        for i, (space_id, name) in enumerate(res.fetchall()):
            self.space_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, typed(space_id, int))
            self.space_stats.setItem(i, 0, item)

            inner_query = db.execute(
                f"""SELECT count(id) FROM tasks WHERE space_id == {space_id}
                AND done
                AND NOT deleted
                AND NOT inactive
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, default=0)))
            self.space_stats.setItem(i, 1, item)
            inner_query = db.execute(
                f"""SELECT count(id) FROM tasks WHERE space_id == {space_id}
                AND NOT done
                AND NOT deleted
                AND NOT inactive
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, default=0)))
            self.space_stats.setItem(i, 2, item)

            inner_query = db.execute(
                f"""SELECT count(id) FROM tasks WHERE space_id == {space_id}
                AND NOT deleted
                AND NOT inactive
                AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, default=0)))
            self.space_stats.setItem(i, 3, item)

        for i, (level_id, name) in enumerate((
            (-2, "MUST NOT"),
            (-1, "SHOULD NOT"),
            (0, "COULD"),
            (1, "SHOULD"),
            (2, "MUST"),
        )):
            self.level_stats.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, space_id)
            self.level_stats.setItem(i, 0, item)
            inner_query = db.execute(
                f"""SELECT count(id) FROM tasks WHERE level_id == {level_id}
                AND done AND NOT deleted AND NOT inactive AND NOT draft"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, default=0)))
            self.level_stats.setItem(i, 1, item)

            inner_query = db.execute(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND NOT done AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, default=0)))
            self.level_stats.setItem(i, 2, item)

            inner_query = db.execute(
                f"""
SELECT
    count(id)
FROM
    tasks
WHERE
    level_id == {level_id} AND NOT deleted AND NOT inactive AND NOT draft
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, default=0)))
            self.level_stats.setItem(i, 3, item)

        query = db.execute(
            """
SELECT
session_id, task_id, start, stop, finished, pause_time
FROM
sessions
"""
        )

        for i, (
            session_id,
            task_id,
            start,
            stop,
            finished,
            pause_time,
        ) in enumerate(
            (
                typed_row(row, 0, int),
                typed_row(row, 1, int),
                typed_row(row, 2, int),
                typed_row(row, 3, int),
                typed_row(row, 4, int),
                typed_row(row, 5, int),
            )
            for row in query.fetchall()
        ):
            inner_query = db.execute(
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
            item = QtWidgets.QTableWidgetItem(typed_row(row, 0, str, default="", debugging=True))
            item.setData(Qt.ItemDataRole.UserRole, session_id)
            self.session_stats.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(start)))
            self.session_stats.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(stop)))
            self.session_stats.setItem(i, 2, item)
            item = QtWidgets.QTableWidgetItem()
            item.setIcon(OK if finished else NOK)
            self.session_stats.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(f"{(stop - start) // 60:04}")
            self.session_stats.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(f"{pause_time // 60:04}")
            self.session_stats.setItem(i, 5, item)


@cached_func_static
def collect_statistics() -> statistics:
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_end - timedelta(days=1)

    total_added = typed_row(
        db.execute("SELECT count(*) from tasks WHERE not draft").fetchone(),
        0,
        int,
        default=0,
    )
    total_finished = typed_row(
        db.execute(
            "SELECT count(*) from tasks WHERE done AND not deleted AND not inactive AND not draft"
        ).fetchone(),
        0,
        int,
        default=0,
    )
    yesterday_added = 0
    today_added = 0
    yesterday_finished = db.execute(
        """SELECT count(*) from sessions WHERE ? < stop AND stop < ? AND finished""",
        (yesterday_start.timestamp(), yesterday_end.timestamp()),
    ).fetchone()[0]
    aggregate()

    return statistics(
        total_added=total_added,
        total_finished=total_finished,
        yesterday_added=yesterday_added,
        yesterday_finished=yesterday_finished,
        today_added=today_added,
        today_finished=get_today_finished(),
        aggregated_data=np.zeros((0, 0)),
    )


@cached_func_static
def aggregate():
    query = db.execute("SELECT task_id, stop FROM sessions WHERE finished")
    sessions = query.fetchall()
    oldest = min(sessions, key=lambda x: x[1])[1]
    days_ago = abs((datetime.fromtimestamp(oldest) - datetime.now()).days)
    task_counter = Counter()
    for task_id, stop in sessions:
        task_counter[datetime.fromtimestamp(stop).replace(hour=0, minute=0, second=0, microsecond=0)] += 1
    calendar_data = np.zeros((days_ago + 1,), dtype=int)
    for day, count in task_counter.items():
        calendar_data[abs((day - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days)] = (
            count
        )


def get_today_finished():
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return db.execute(
        """SELECT count(*) from sessions WHERE ? < stop AND finished""",
        (today_start.timestamp(),),
    ).fetchone()[0]


def get_tasks_finished_today() -> list[Task]:
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        app.tasks[typed_row(row, 0, int)]
        for row in db.execute(
            """SELECT task_id from sessions WHERE ? < stop AND finished""",
            (today_start.timestamp(),),
        ).fetchall()
    }


def get_tasks_finished_yesterday() -> list[Task]:
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_start - timedelta(seconds=1)
    return {
        app.tasks[typed_row(row, 0, int)]
        for row in db.execute(
            """SELECT task_id from sessions WHERE ? < stop AND stop < ? AND finished""",
            (yesterday_start.timestamp(), yesterday_end.timestamp()),
        ).fetchall()
    }
