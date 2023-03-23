"""The entry point for watnu.

Run with py main.py and watch the Magik happen!
"""
import ctypes
import sqlite3
import sys
from pathlib import Path
from random import seed
from time import time

import use
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtSql import QSqlDatabase

# ImportError: QtWebEngineWidgets must be imported or Qt.AA_ShareOpenGLContexts must be set before a QCoreApplication instance is created
from PyQt6.QtWebEngineWidgets import QWebEngineView

q = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/q/main/q.py"), modes=use.recklessness, import_as="q"
).Q()

use(
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
import config

__version__ = use.Version("0.2.2")
__author__ = "Anselm Kiefner"
q("Python:", sys.version)
q("Watnu Version:", __version__)

myappid = f"kiefnerit.watnu.{__version__}"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

_translate = QCoreApplication.translate


def breakpoint_():
    from PyQt6.QtCore import pyqtRemoveInputHook

    pyqtRemoveInputHook()
    sys.breakpointhook()


class TrayIcon(QtWidgets.QSystemTrayIcon):
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


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1]
    # touch, just in case user killed the config or first start
    (path / "config.stay").touch()
    # overwriting the module with the instance for convenience
    config = config.read(path / "config.stay")

    app = use(use.Path("ux/app.py"), initial_globals={"config": config}, import_as="ux.app").Application(
        sys.argv
    )
    app.icon = QIcon(config.icon)
    app.setWindowIcon(app.icon)

    seed((config.coin ^ config.lucky_num) * config.count)

    qdb = QSqlDatabase.addDatabase("QSQLITE")
    db = sqlite3.connect(config.db_path, factory=DB)

    initial_globals = {
        "config": config,
        "app": app,
        "__version__": __version__,
        "db": db,
    }
    use(use.Path("classes.py"), initial_globals=initial_globals, import_as="classes")

    if config.tutorial_active:
        landing = use(use.Path("ux/landing.py"), initial_globals={"app": app, "qdb": qdb})
        win_landing = landing.Landing()
        concluded = win_landing.exec()
        if concluded:
            config.tutorial_active = False
    qdb.setDatabaseName(config.db_path)

    if not qdb.open():
        q("Could not open DB!")

    if config.first_start:
        use(use.Path("first_run.py"), initial_globals=initial_globals).run()
        config.first_start = False
        config.write()

    if config.run_sql_stuff:
        # just in case..
        (path / f"{config.db_path}.bak").write_bytes((path / config.db_path).read_bytes())

        use("sql_stuff.py", initial_globals={"config": config})
        config.run_sql_stuff = False
        config.write()

    app.list_of_task_lists: list["task_list.TaskList"] = []
    "Multiple TaskLists can be open at the same time."
    app.list_of_editors: list["task_editor.Editor"] = []
    "Multiple Editors can be open at the same time."

    use(use.Path("ux/stuff.py"), initial_globals=initial_globals, import_as="ux.stuff")

    from ux import task_editor, task_list

    app.setUp(config)

    app.activity_color = {
        0: config.activity_color_body,
        1: config.activity_color_mind,
        2: config.activity_color_spirit,
    }

    if not qdb.tables():
        config.first_start = True
        config.write()
        QtWidgets.QMessageBox.critical(
            None,
            "Restart required",
            "Found an empty DB. Everything has been reset. Shutting down - please restart!",
        )
        app.tray.hide()
        sys.exit()

    app.win_main.show()

    app.tray = TrayIcon(app.icon, app.win_main)
    app.tray.show()

    sys.exit(app.exec())
