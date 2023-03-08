"""The entry point for watnu.

Run with py main.py and watch the Magik happen!
"""
import sys
import webbrowser
from bisect import bisect_right
from collections import defaultdict, namedtuple
from datetime import datetime
from enum import Enum
from functools import partial
from itertools import count
from math import isinf, modf, sin
from pathlib import Path
from random import choice, seed
from time import time, time_ns

import use
from dateutil.relativedelta import relativedelta
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication, QDate, QDateTime, QItemSelectionModel, Qt, QTimer, QUrl, QVariant
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QKeySequence, QShortcut
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMessageBox

np = use(
    "numpy",
    version="1.24.1",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "i㹄臲嬁㯁㜇䕀蓴卄闳䘟菽掸䢋䦼亱弿椊",  # cp311-win_amd64
    },
)
use(
    "beartype",
    version="0.12.0",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "M㻇睧㳱懁㖯糄巿蚩熆鲣㦶烺㒈䵒犝㞍覦",  # py3-any
    },
)

stay = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/stay/master/src/stay/stay.py"),
    hash_algo=use.Hash.sha256,
    hash_value="47e11e8de6b07f24c95233fba1e7281c385b049f771f74c5647a837b51bd7ff4",
    import_as="stay",
)


flux = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/flux/master/flux/flux.py"),
    hash_algo=use.Hash.sha256,
    hash_value="d1361e4925b74fa864f0b218977ee34dd6b2d86e2e681dda7cae8cfcd46eff1a",
)


load = stay.Decoder()

import classes
import config
import q
import ui
from algo import (
    balance,
    check_task_conditions,
    constraints_met,
    filter_tasks,
    prioritize,
    schedule,
    skill_level,
)
from classes import EVERY, ILK, Every, Task, cached_and_invalidated, iter_over, submit_sql, typed

__version__ = (0, 2, 2)
__author__ = "Anselm Kiefner"
q("Python:", sys.version)
q("Watnu Version:", __version__)

_translate = QCoreApplication.translate


def breakpoint_():
    from PyQt6.QtCore import pyqtRemoveInputHook

    pyqtRemoveInputHook()
    sys.breakpointhook()


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent):
        super().__init__(icon, parent)
        menu = QtWidgets.QMenu()
        self.setContextMenu(menu)
        menu.triggered.connect(self.liste)

    def liste(self):
        win = task_list.TaskList()
        app.list_of_task_lists.append(win)
        win.show()


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1]
    # touch, just in case user killed the config or first start
    (path / "config.stay").touch()
    # overwriting the module with the instance for convenience
    config = config.read(path / "config.stay")
    from ux import app

    app = app.Application(sys.argv)
    app.icon = QIcon(config.icon)

    seed((config.coin ^ config.lucky_num) * config.count)
    classes.set_globals(config)

    db = QSqlDatabase.addDatabase("QSQLITE")

    initial_globals = {
        "config": config,
        "db": db,
        "app": app,
        "__version__": __version__,
    }

    if config.tutorial_active:
        landing = use(use.Path("ux/landing.py"), initial_globals={"app": app, "db": db})
        win_landing = landing.Landing()
        concluded = win_landing.exec()
        if concluded:
            config.tutorial_active = False
    db.setDatabaseName(config.database)

    if not db.open():
        q("Could not open DB!")

    if config.first_start:
        import first_start

        first_start.run(db, config)
        config.first_start = False
        config.write()

    if config.run_sql_stuff:
        config.run_sql_stuff = False
        config.write()
        # just in case..
        dbpath = path / config.database
        backup = path / f"{config.database}.bak"
        backup.write_bytes(dbpath.read_bytes())  # nice way to copy a file
        import sql_stuff

    app.list_of_task_lists: list["task_list.TaskList"] = []
    "Multiple TaskLists can be open at the same time."
    app.list_of_editors: list["task_editor.Editor"] = []
    "Multiple Editors can be open at the same time."
    all_tasks = []
    "All tasks from the DB loaded here."

    use(use.Path("ux/stuff.py"), initial_globals=initial_globals, import_as="ux.stuff")

    from ux import (
        attributions,
        character,
        companions,
        inventory,
        main_window,
        settings,
        task_editor,
        task_list,
        what_now,
    )

    app.win_main = main_window.MainWindow()
    app.win_main.setWindowIcon(app.icon)
    app.win_main.statusBar.show()

    greet_time = ["N'Abend", "Guten Morgen", "Guten Tag", "Guten Nachmittag", "Guten Abend", "Guten Abend"][
        bisect_right([6, 11, 14, 18, 21, 25], datetime.now().hour)
    ]
    config.call_name = ""  # TODO converter in config.py?
    app.win_main.statusBar.showMessage(
        f"{greet_time}, willkommen zurück{f', {config.call_name}' if config.call_name else ''}!", 10000
    )
    app.win_what = what_now.What_Now()
    app.win_character = character.Character()
    app.win_settings = settings.Settings()
    app.win_running = None
    app.win_attributions = attributions.Attributions()
    app.win_companions = companions.Companions()
    app.win_inventory = inventory.Inventory()

    app.last_edited_space: str = None

    app.activity_color = {
        0: config.activity_color_body,
        1: config.activity_color_mind,
        2: config.activity_color_spirit,
    }

    if not db.tables():
        config.first_start = True
        config.write()
        mb = QtWidgets.QMessageBox()
        mb.setText("Found an empty DB. Everything has been reset. Shutting down - please restart!")
        mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
        mb.setWindowTitle("Hmm..")
        mb.exec()
        app.tray.hide()
        sys.exit()

    app.win_main.show()

    app.tray = TrayIcon(app.icon, app.win_main)
    app.tray.show()

    sys.exit(app.exec())
