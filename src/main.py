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

app = app.Application(sys.argv)

import use

# new_tips = use("https://raw.githubusercontent.com/amogorkon/watnu/main/tips.py")

q = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/q/main/q.py"), modes=use.recklessness, import_as="q"
).Q()


# FIX: won't work with justuse :(
# use(
#     "cryptography",
#     version="40.0.2",
#     modes=use.auto_install,
#     hash_algo=use.Hash.sha256,
#     hashes={
#         "S䅅䢒呹㞙叆鲟懕䘃嗷˱㸸蔐䞬鯯㧬㿐禳",  # pp39-win_amd64
#         "Z巃猔ȣ㣀㱟䢖忢菠沆奿橗遬閶熌㗐鮥Ɛ",  # None-None
#     },
# )

use(
    "numpy",
    version="1.24.1",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "i㹄臲嬁㯁㜇䕀蓴卄闳䘟菽掸䢋䦼亱弿椊",  # cp311-win_amd64
    },
    import_as="numpy",
)

use(
    "pyqtgraph",
    version="0.13.3",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "l䦘顳䑅葃弤㷗萧䃱翟僅㤏冈湞䤸茑胛啙",  # py3-any
    },
    import_as="pyqtgraph",
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


load = stay.Decoder()
import src.configuration as configuration

__version__ = use.Version("0.2.2")
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
        use.Path("ux/landing.py"), initial_globals={"config": config}, import_as="ux.landing"
    ).Landing()
    concluded = win_landing.exec()


# # Load the key
# with open("filekey.key", "rb") as filekey:
#     key = filekey.read()

# # Create a Fernet object
# fernet = Fernet(key)

# # Open the file to encrypt
# with open("file_to_encrypt.txt", "rb") as file:
#     original = file.read()

# # Encrypt the file
# encrypted = fernet.encrypt(original)

# # Write the encrypted data to a new file
# with open("encrypted_file.txt", "wb") as encrypted_file:
#     encrypted_file.write(encrypted)

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

# push all the globals into 'src.stuff' so we can import them properly
# and getting all the perks of IDE autocompletion
use(use.Path("stuff.py"), initial_globals=initial_globals, import_as="src.stuff")
from src.classes import retrieve_spaces, retrieve_tasks

app.setUp(config, db)
from src.ux import tip_of_the_day

qdb.setDatabaseName(config.db_path)
if not qdb.open() or not qdb.tables():
    config.first_start = True
    config.save()
    QMessageBox.critical(
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
    winreg.SetValueEx(key, "Watnu", 0, winreg.REG_SZ, f"{sys.executable} {config.base_path / 'watnu.py'}")
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
    check_for_cycles,
    check_for_deadline_without_workload,
    check_for_drafts,
    check_for_incompleatable_tasks,
    check_for_overdue_tasks,
    clean_up_empty_tasks,
)

now = datetime.now()

# just passing app.tasks.values would cause RuntimeError: dictionary changed size during iteration
# and a single tasks = list(app.tasks.values()) on top wouldn't work either because of tasks
# being deleted or created at each step
clean_up_empty_tasks(list(app.tasks.values()))
check_for_drafts(list(app.tasks.values()))
check_for_cycles(list(app.tasks.values()))
check_for_deadline_without_workload(list(app.tasks.values()))
check_for_overdue_tasks(list(app.tasks.values()), now)
check_for_incompleatable_tasks(list(app.tasks.values()), now)
check_for_cycles(list(app.tasks.values()))  # again, the user might have introduced cycles in previous checks

app.win_what.lets_check_whats_next()
app.win_main.unlock()

if config.show_totd:
    app.win_tip = tip_of_the_day.TipOfTheDay()
    app.win_tip.show()
    app.win_main.raise_()
    app.win_tip.raise_()

sys.exit(app.exec())
