from bisect import bisect_right
from datetime import datetime

import q
from PyQt6 import QtWidgets


class Application(QtWidgets.QApplication):
    """Main Application logic."""

    def __init__(self, argv, config_, db_):
        super().__init__(argv)
        self.db_last_modified = 0
        global config, db
        config = config_
        db = db_

    def setUp(self):
        import ux

        self.list_of_task_lists: list[ux.task_list.TaskList] = []
        "Multiple TaskLists can be open at the same time."
        self.list_of_editors: list[ux.task_editor.Editor] = []
        "Multiple Editors can be open at the same time."
        self.last_edited_space: str = None
        self.win_main = ux.main_window.MainWindow()

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
        q(i + 1 if i is not None else "Nothing found, so no", "unused resources deleted.")
