import sqlite3
from bisect import bisect_right
from datetime import datetime

import q
from PyQt6 import QtWidgets

from config import Config

config: Config
db: sqlite3.Connection


class Application(QtWidgets.QApplication):
    """Main Application logic."""

    def __init__(self, argv):
        super().__init__(argv)
        self.db_last_modified = 0

    def setUp(self, conf: Config):
        global config
        config = conf

        self.last_edited_space: str = None
        from ux import (
            attributions,
            character,
            companions,
            inventory,
            main_window,
            settings,
            statistics,
            task_editor,
            task_list,
            what_now,
        )

        self.win_main = main_window.MainWindow()

        self.win_main.setWindowIcon(self.icon)
        self.win_main.statusBar.show()

        greet_time = [
            "N'Abend",
            "Guten Morgen",
            "Guten Tag",
            "Guten Nachmittag",
            "Guten Abend",
            "Guten Abend",
        ][bisect_right([6, 11, 14, 18, 21, 25], datetime.now().hour)]
        config.call_name = ""  # TODO converter in config.py?
        self.win_main.statusBar.showMessage(
            f"{greet_time}, willkommen zurück{f', {config.call_name}' if config.call_name else ''}!", 10000
        )
        self.win_what = what_now.What_Now()
        self.win_character = character.Character()
        self.win_settings = settings.Settings()
        self.win_running = None
        self.win_companions = companions.Companions()
        self.win_inventory = inventory.Inventory()
        self.win_statistics = statistics.Statistics()

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
        for i, row in enumerate(query.fetchall()):
            db.execute(
                f"""
    DELETE FROM resources
    WHERE resource_id = {row(0)}
    """
            )
        q(i + 1 if i is not None else "Nothing found, so no", "unused resources deleted.")
