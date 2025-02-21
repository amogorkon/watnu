import contextlib
import sys
from bisect import bisect_right
from collections import deque
from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QFontDatabase

# import startup
# ImportError: QtWebEngineWidgets must be imported or Qt.AA_ShareOpenGLContexts
# must be set before a QCoreApplication instance is created
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401


class Application(QtWidgets.QApplication):
    """Main Application logic."""

    def __init__(self, argv):
        super().__init__(argv)
        self.startup_time = datetime.now().timestamp()
        # TODO: Implement startup window
        # self.startup_win = startup.Startup()

    def setUp(
        self,
    ):
        global config, db
        from src import config, db

        self.db_last_modified = 0

        # Task requires app, so we would end up going in circles if we imported it at the top.
        from src.classes import Skill, SkillDict, Space, SpaceDict, Task, TaskDict

        path = config.config_path.parent / "filter_history.txt"
        path.touch()
        with open(path, "r") as f:
            self.history = deque(f.readlines(), maxlen=100)

        from src.ux import (
            character,
            companions,
            inventory,
            main_window,
            settings,
            statistics,
            task_checklist,
            task_editor,
            task_list,
            task_organizer,
            what_now,
        )

        self.list_of_task_lists: list[task_list.TaskList] = []
        "Multiple TaskLists can be open at the same time."
        self.list_of_task_editors: list[task_editor.TaskEditor] = []
        "Multiple Editors can be open at the same time."
        self.list_of_task_organizers: list[task_organizer.Organizer] = []
        "Multiple Organizers can be open at the same time."
        self.list_of_task_checklists: list[task_checklist.CheckList] = []
        self.last_edited_space: str | None = None
        self.win_main = main_window.MainWindow()

        self.list_of_windows: list[QtWidgets.QMainWindow | QtWidgets.QDialog] = [self.win_main]

        self.win_main.setWindowIcon(self.icon)
        self.win_main.statusBar.show()

        self.tasks: TaskDict[int, Task] = TaskDict()
        self.spaces: SpaceDict[int, Space] = SpaceDict()
        self.skills: SkillDict[int, Skill] = SkillDict()

        self.app_timer = QTimer()
        # start the timer on the clock of the next minute in msec
        QTimer.singleShot(
            int((60 - datetime.now().timestamp() % 60) * 1000),
            self.app_timer.start,
        )
        self.app_timer.start(60_000)

        self.app_timer.timeout.connect(self.win_main.set_statistics_icon)

        greet_time = [
            "N'Abend",
            "Guten Morgen",
            "Guten Tag",
            "Guten Nachmittag",
            "Guten Abend",
            "Guten Abend",
        ][bisect_right([6, 11, 14, 18, 21, 25], datetime.now().hour)]
        self.win_main.statusBar.showMessage(
            f"{greet_time}, {f'{config.call_name}' if config.call_name else 'willkommen zurück'}!",
            10000,
        )
        self.win_what = what_now.WhatNow()
        self.win_character = character.Character()
        self.win_settings = settings.Settings()
        self.win_running = None
        self.win_companions = companions.Companions()
        self.win_inventory = inventory.Inventory()
        self.win_statistics = statistics.Statistics()

        ID = QFontDatabase.addApplicationFont(
            str(config.base_path / "./extra/Fira_Sans/FiraSans-Regular.ttf")
        )
        family = QFontDatabase.applicationFontFamilies(ID)
        self.fira_font = QFont(family)

    def mouseMoveEvent(self, event):
        event.ignore()
        return False

    def write_session(self, task_id, start, stop, finished=False, pause_time=0):
        db.execute(
            f"""
            INSERT INTO sessions (task_id, start, stop, pause_time, finished)
            VALUES ('{task_id}', {int(start)}, {int(stop)}, {pause_time}, {finished})
            """
        )
        db.commit()

    def sanitize_db(self):
        """
        Deletes all resources that are not used by any task from the database.
        """
        query = db.execute(
            """
        SELECT r.resource_id
        FROM resources r
        LEFT JOIN task_uses_resource
        ON task_uses_resource.resource_id = r.resource_id
        WHERE task_uses_resource.task_id is NULL
        """
        )
        i = None
        for i, resource_id in enumerate(query.fetchall()):
            db.execute(
                f"""
        DELETE FROM resources
        WHERE resource_id = {resource_id}
        """
            )

        import q

        q(
            i + 1 if i is not None else "Nothing found, so no",
            "unused resources deleted.",
        )

    def shutdown(self):
        with contextlib.suppress(RuntimeError):  # ignore annoying last-minute exceptions
            self.tray.hide()
            self.tray.deleteLater()

        self.closeAllWindows()
        config.db_write_count += 1
        config.save()
        from src.logic import filter_history

        with open(config.config_path.parent / "filter_history.txt", "w") as f:
            f.writelines(filter_history(self.history))

        sys.exit(0)
