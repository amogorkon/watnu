from bisect import bisect_right
from collections import defaultdict, deque
from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, QEvent, QLocale, QSettings, Qt, QTimer

# import startup


class Application(QtWidgets.QApplication):
    """Main Application logic."""

    def __init__(self, argv):
        super().__init__(argv)
        self.startup_time = datetime.now().timestamp()
        # self.startup_win = startup.Startup()

    def setUp(self, config_, db_):
        self.db_last_modified = 0
        global config, db
        config = config_
        db = db_

        # Task requires app, so we would end up going in circles if we imported it at the top.
        from src.classes import Task, Space

        self.activity_color = {
            1: config.activity_color_mind,  # darkblue
            2: config.activity_color_body,  # darkred
            3: config.activity_color_soul,  # indigo
        }

        class TaskDict(dict):
            def __missing__(self, key):
                value = Task.from_id(key)
                self[key] = value
                return value

        class SpaceDict(dict):
            def __missing__(self, key):
                value = Task.from_id(key)
                self[key] = value
                return value

        config = config_
        db = db_
        path = config.base_path / "filter_history.stay"
        path.touch()
        with open(path, "r") as f:
            self.filter_history = deque(f.readlines(), maxlen=100)

        import src.ux as ux

        self.list_of_task_lists: list[ux.task_table.TaskList] = []
        "Multiple TaskLists can be open at the same time."
        self.list_of_task_editors: list[ux.task_editor.Editor] = []
        "Multiple Editors can be open at the same time."
        self.list_of_task_organizers: list[ux.task_organizer.Organizer] = []
        "Multiple Organizers can be open at the same time."
        self.last_edited_space: str = None
        self.win_main = ux.main_window.MainWindow()

        self.list_of_windows: list[QtWidgets.QMainWindow | QtWidgets.QDialog] = [self.win_main]

        self.win_main.setWindowIcon(self.icon)
        self.win_main.statusBar.show()

        self.tasks: dict[int, Task] = TaskDict()
        self.spaces: dict[int, Space] = SpaceDict()

        self.app_timer = QTimer()
        # start the timer on the clock of the next minute in msec
        QTimer.singleShot(int((60 - datetime.now().timestamp() % 60) * 1000), self.app_timer.start)
        self.app_timer.start(60_000)

        @self.app_timer.timeout.connect
        def task_timer_timeout():
            self.win_main.set_statistics_icon()

        greet_time = [
            "N'Abend",
            "Guten Morgen",
            "Guten Tag",
            "Guten Nachmittag",
            "Guten Abend",
            "Guten Abend",
        ][bisect_right([6, 11, 14, 18, 21, 25], datetime.now().hour)]
        self.win_main.statusBar.showMessage(
            f"{greet_time}, {f'{config.call_name}' if config.call_name else 'willkommen zurück'}!", 10000
        )
        self.win_what = ux.what_now.What_Now()
        self.win_character = ux.character.Character()
        self.win_settings = ux.settings.Settings()
        self.win_running = None
        self.win_companions = ux.companions.Companions()
        self.win_inventory = ux.inventory.Inventory()
        self.win_statistics = ux.statistics.Statistics()

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

        q(i + 1 if i is not None else "Nothing found, so no", "unused resources deleted.")
