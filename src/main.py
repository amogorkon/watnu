"""The entry point for watnu.

Run with py main.py and watch the Magik happen!
"""
import ctypes
import sqlite3
import sys
from pathlib import Path
from time import time

import use
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QTimer, QVariant
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QKeySequence, QShortcut
from PyQt6.QtSql import QSqlDatabase

# ImportError: QtWebEngineWidgets must be imported or Qt.AA_ShareOpenGLContexts must be set before a QCoreApplication instance is created
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

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
import app
import configuration

__version__ = use.Version("0.2.2")
__author__ = "Anselm Kiefner"
q("Python:", sys.version)
q("Watnu Version:", __version__)

myappid = f"kiefnerit.watnu.{__version__}"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

_translate = QCoreApplication.translate


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
    config_path = path / "config.stay"
    config_path.touch()
    config = configuration.read(config_path)
    print("using config:", config_path)
    config.base_path = path
    app = app.Application(sys.argv, config)
    app.icon = QIcon(config.icon)
    app.setWindowIcon(app.icon)

    # split tutorial from landing wizard, so the user can do the tutorial at any time
    if config.first_start:
        win_landing = use(
            use.Path("ux/landing.py"), initial_globals={"config": config}, import_as="ux.landing"
        ).Landing()
        concluded = win_landing.exec()

    db = sqlite3.connect(config.db_path, factory=DB)
    if config.debugging:
        db.set_trace_callback(q)

    qdb = QSqlDatabase.addDatabase("QSQLITE")

    initial_globals = {
        "config": config,
        "app": app,
        "__version__": __version__,
        "db": db,
    }

    # push all the globals into 'stuff' so we can import them properly and getting all the perks of IDE autocompletion
    use(use.Path("stuff.py"), initial_globals=initial_globals, import_as="stuff")

    from classes import Task, retrieve_tasks

    app.setUp(db)
    from ux import landing, task_editor

    qdb.setDatabaseName(config.db_path)
    if not qdb.open() or not qdb.tables():
        config.first_start = True
        config.save()
        QtWidgets.QMessageBox.critical(
            None,
            "Restart required",
            "No viable DB found. Everything has been reset. Shutting down - please restart!",
        )
        app.tray.hide()
        sys.exit()

    if config.run_sql_stuff:
        # just in case..
        (path / f"{config.db_path}.bak").write_bytes((path / config.db_path).read_bytes())

        use("sql_stuff.py", initial_globals={"config": config})
        config.run_sql_stuff = False
        config.save()

    app.activity_color = {
        0: config.activity_color_body,
        1: config.activity_color_mind,
        2: config.activity_color_spirit,
    }

    app.win_main.show()

    app.tray = TrayIcon(app.icon, app.win_main)
    app.tray.show()

    tasks: list[Task] = retrieve_tasks(db)
    # first, let's clean up empty ones
    for task in tasks:
        if task.do == "" and task.notes in ("", None):
            task.really_delete()
    tasks = retrieve_tasks(db)
    if drafts := [t for t in tasks if t.draft]:
        match QtWidgets.QMessageBox.question(
            app.win_main,
            "Jetzt bearbeiten?",
            f"Es gibt {f'{len(drafts)} Entwürfe' if len(drafts) > 1 else 'einen Entwurf'} - jetzt bearbeiten?",
        ):
            case QtWidgets.QMessageBox.StandardButton.Yes:
                for task in drafts:
                    editor = task_editor.Editor(task)
                    editor.show()
                    editor.raise_()
                    app.list_of_task_editors.append(editor)

    sys.exit(app.exec())
