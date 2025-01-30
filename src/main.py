# ruff: noqa: E402
"""The entry point for watnu.

Run with py main.py and watch the Magik happen!
"""

import contextlib
import ctypes
import os
import platform
import sys
from datetime import datetime

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon

from src import initialize_globals, path
from src.classes import retrieve_spaces, retrieve_tasks
from src.q import Q

q = Q()
from src import app, config, db
from src.startup_checks import (
    _check_for_cycles,
    _check_for_deadline_without_workload,
    _check_for_drafts,
    _check_for_incompletable_tasks,
    _check_for_overdue_tasks,
    _clean_up_empty_tasks,
)
from src.ux import tip_of_the_day
from src.version import __version__

q("Python:", sys.version)
q("Watnu Version:", __version__)


if platform.system() == "Windows":
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


app.icon = QIcon(str(config.base_path / "extra/feathericons/watnu1.png"))
app.setWindowIcon(app.icon)

# split tutorial from landing wizard, so the user can do the tutorial at any time
if config.first_start:
    from src.ux.landing import Landing

    win_landing = Landing()
    concluded = win_landing.exec()


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

initialize_globals(db, app, config)


app.setUp()

if config.run_sql_stuff:
    # just in case..
    (path / f"{config.db_path}.bak").write_bytes((path / config.db_path).read_bytes())

    from src import sql_stuff

    sql_stuff.run(initial_globals={"config": config})
    config.run_sql_stuff = False
    config.save()

app.win_main.show()

app.tray = TrayIcon(app.icon, app.win_main)
app.tray.show()


if config.autostart:
    if platform.system() == "Windows":
        import winreg

        import win32com.client

        # Hide the terminal if started via autostart
        if ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )

        with contextlib.suppress(FileNotFoundError):
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_ALL_ACCESS,
            )
            winreg.DeleteValue(key, "Watnu")
            winreg.CloseKey(key)

        startup_folder = os.path.join(
            os.getenv("APPDATA"),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
        )
        script_path = os.path.abspath(sys.argv[0])
        shortcut_path = os.path.join(startup_folder, "watnu.lnk")

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()

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
            f"{sys.executable} {script_path}",
        )
        winreg.CloseKey(key)

    elif platform.system() == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_entry = f"""
[Desktop Entry]
Type=Application
Exec={sys.executable} {os.path.abspath(sys.argv[0])} --no-terminal
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=Watnu
Name=Watnu
Comment=Start Watnu on login
"""
        with open(os.path.join(autostart_dir, "watnu.desktop"), "w") as f:
            f.write(desktop_entry)

# get all spaces from the db
app.spaces = {s.space_id: s for s in retrieve_spaces()}

# get all tasks from the db
app.tasks = {t.id: t for t in retrieve_tasks()}


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
_check_for_cycles(
    list(app.tasks.values())
)  # again, the user might have introduced cycles in previous checks

app.win_what.lets_check_whats_next()
app.win_main.unlock()

if config.show_totd:
    app.win_tip = tip_of_the_day.TipOfTheDay()
    app.win_tip.show()
    app.win_main.raise_()
    app.win_tip.raise_()

sys.exit(app.exec())
