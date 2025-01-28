# ruff: noqa: E402
"""The entry point for watnu.

Run with py main.py and watch the Magik happen!
"""
import ctypes
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from time import time

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtSql import QSqlDatabase

# ImportError: QtWebEngineWidgets must be imported or Qt.AA_ShareOpenGLContexts
# must be set before a QCoreApplication instance is created
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon

import src.app as app
import numpy
import pyqtgraph
import beartype
import icontract
import src.configuration as configuration
from src.classes import retrieve_spaces, retrieve_tasks
from src.ux import tip_of_the_day
from src.startup_checks import (
    _check_for_cycles,
    _check_for_deadline_without_workload,
    _check_for_drafts,
    _check_for_incompletable_tasks,
    _check_for_overdue_tasks,
    _clean_up_empty_tasks,
)

app = app.Application(sys.argv)



load = stay.Decoder()
import src.configuration as configuration

__version__ = "0.2.2"
__author__ = "Anselm Kiefner"
q("Python:", sys.version)
q("Watnu Version:", __version__)

myappid = f"kiefnerit.watnu.{__version__}"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

_translate = QCoreApplication.translate


class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent):
        super().__init__(icon, parent)

        @self.activated.connect
        def activated():
            app.win_main.show()
            app.win_main.raise_()


class DB(sqlite3.Connection):
    def commit(self):
        super().commit()
        app.db_last_modified = time()

    def is_connected(self):
        try:
            self.cursor()
            return True
        except Exception:
            return False


import contextlib

path = Path(__file__).resolve().parent
# touch, just in case user killed the config or first start

config_path = path / "config.stay"
config_path.touch()
config = configuration.read(config_path)
config.config_path = config_path
print("using config:", config_path)
config.base_path = path

app.icon = QIcon(str(config.base_path / "extra/feathericons/watnu1.png"))
app.setWindowIcon(app.icon)

# split tutorial from landing wizard, so the user can do the tutorial at any time
if config.first_start:
    win_landing = use(
        use.Path("ux/landing.py"),
        initial_globals={"config": config},
        import_as="ux.landing",
    ).Landing()
    concluded = win_landing.exec()

db = sqlite3.connect(config.db_path, factory=DB)

# because we put LEVEL stuff etc. in the db, which is used as model in the editor...
qsql_db = QSqlDatabase.addDatabase("QSQLITE")
qsql_db.setDatabaseName(config.db_path)

if not db.is_connected():
    breakpoint()
    config.first_start = True
    config.save()
    QMessageBox.critical(
        None,
        "Restart required",
        "No viable DB found. Everything has been reset. Shutting down - please restart!",
    )
    app.tray.hide()
    sys.exit()

if config.debugging:
    db.set_trace_callback(q)


initial_globals = {
    "config": config,
    "app": app,
    "__version__": __version__,
    "db": db,
}

from src.stuff import *  # Assuming src.stuff contains necessary imports

app.setUp(config, db)
from src.ux import tip_of_the_day

if config.run_sql_stuff:
    # just in case..
    (path / f"{config.db_path}.bak").write_bytes((path / config.db_path).read_bytes())

    use("sql_stuff.py", initial_globals={"config": config})
    config.run_sql_stuff = False
    config.save()

app.win_main.show()

app.tray = TrayIcon(app.icon, app.win_main)
app.tray.show()

# windows autostart
if config.autostart:
    import winreg

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_ALL_ACCESS,
    )
    winreg.SetValueEx(
        key,
        "Watnu",
        0,
        winreg.REG_SZ,
        f"{sys.executable} {config.base_path / 'watnu.py'}",
    )
    winreg.CloseKey(key)
else:
    with contextlib.suppress(FileNotFoundError):
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS,
        )
        winreg.DeleteValue(key, "Watnu")
        winreg.CloseKey(key)


# get all spaces from the db
app.spaces = {s.space_id: s for s in retrieve_spaces()}

# get all tasks from the db
app.tasks = {t.id: t for t in retrieve_tasks()}

from src.startup_checks import (
    _check_for_cycles,
    _check_for_deadline_without_workload,
    _check_for_drafts,
    _check_for_incompletable_tasks,
    _check_for_overdue_tasks,
    _clean_up_empty_tasks,
)

now = datetime.now()

# just passing app.tasks.values would cause RuntimeError: dictionary changed size during iteration
# and a single tasks = list(app.tasks.values()) on top wouldn't work either because of tasks
# being deleted or created at each step
_clean_up_empty_tasks(list(app.tasks.values()))
_check_for_drafts(list(app.tasks.values()))
_check_for_cycles(list(app.tasks.values()))
_check_for_deadline_without_workload(list(app.tasks.values()))
_check_for_overdue_tasks(list(app.tasks.values()), now)
_check_for_incompletable_tasks(list(app.tasks.values()), now)
_check_for_cycles(list(app.tasks.values()))  # again, the user might have introduced cycles in previous checks

app.win_what.lets_check_whats_next()
app.win_main.unlock()

if config.show_totd:
    app.win_tip = tip_of_the_day.TipOfTheDay()
    app.win_tip.show()
    app.win_main.raise_()
    app.win_tip.raise_()

sys.exit(app.exec())
