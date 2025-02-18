import signal
import webbrowser
from collections import defaultdict
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QPushButton
from yaml import dump, load

import src.ui as ui
from src import app, config, db
from src.q import q
from src.ux import (
    about,
    attributions,
    statistics,
    task_checklist,
    task_editor,
    task_list,
    task_organizer,
)


def set_icon(button, icon_path):
    icon = QtGui.QIcon()

    icon.addPixmap(
        QtGui.QPixmap(str(config.base_path / icon_path)),
        QtGui.QIcon.Mode.Normal,
        QtGui.QIcon.State.Off,
    )
    button.setIcon(icon)
    button.setIconSize(QtCore.QSize(30, 30))


class MyButton(QPushButton):
    def __init__(self):
        super().__init__()


class MainWindow(QtWidgets.QMainWindow, ui.main_window.Ui_MainWindow):
    def quit(self, num, frame):
        self.killed = True
        app.shutdown()

    def __init__(
        self,
    ):
        super().__init__()
        self.setupUi(self)

        self._init_defaults()
        self._init_ui_elements()
        self._init_signals()

    def _init_defaults(self):
        self.killed = False

        self.gui_timer = QtCore.QTimer()
        self.gui_timer.start(100)

    def _init_ui_elements(self):
        self.set_statistics_icon()  # self.set_icon(self.button1, "statistics.svg")
        set_icon(self.button2, "extra/feathericons/inventory.svg")
        set_icon(self.button3, "extra/organisation.svg")
        set_icon(self.button4, "extra/feathericons/list.svg")
        set_icon(self.button5, "extra/feathericons/play-circle.svg")
        set_icon(self.button6, "extra/feathericons/file-plus.svg")
        # set_icon(self.button7, "extra/600-cell.gif")
        self.movie = QtGui.QMovie(str(config.base_path / "extra/600-cell-unscreen.gif"))
        self.movie.start()
        self.button7.setIconSize(QtCore.QSize(30, 30))
        set_icon(self.button8, "extra/checklist.svg")
        set_icon(self.button9, "extra/superhero - attribute to Freepik.svg")

        self.statusBar.setSizeGripEnabled(False)

    def _init_signals(self):
        # catch ctrl+c and register it as a quit
        signal.signal(signal.SIGINT, self.quit)

        self.gui_timer.timeout.connect(lambda: self.button7.setIcon(QtGui.QIcon(self.movie.currentPixmap())))

        self.about.triggered.connect(lambda: about.About().exec())
        self.actionReadme.triggered.connect(
            lambda: webbrowser.open("https://github.com/amogorkon/watnu/blob/main/README.md")
        )

        self.attributions.triggered.connect(lambda: attributions.Attributions().exec())

        self.button1.clicked.connect(lambda: app.win_statistics.show())
        self.button2.clicked.connect(lambda: app.win_inventory.show())
        self.button3.clicked.connect(lambda: task_organizer.make_new_and_show_all())
        self.button4.clicked.connect(lambda: task_list.make_new_and_show_all())
        self.button6.clicked.connect(lambda: task_editor.make_new_and_show_all())
        self.button7.clicked.connect(lambda: webbrowser.open("https://chat.deepseek.com/"))
        self.button8.clicked.connect(lambda: task_checklist.make_new_and_show_all())
        self.button9.clicked.connect(lambda: app.win_character.show())

        @self.button5.clicked.connect
        def whatnow():
            self.statusBar.clearMessage()
            self.repaint()
            app.win_what.lets_check_whats_next()
            app.win_what.show()
            self.hide()

        self.actionSupportMe.triggered.connect(lambda: webbrowser.open("paypal.me/amogorkon"))

        self.actionIssue_Tracker.triggered.connect(
            lambda: webbrowser.open("https://github.com/amogorkon/watnu/issues")
        )

        self.actionContact.triggered.connect(
            lambda: webbrowser.open("https://calendly.com/tetraplex/pomodoro")
        )

        self.actionSettings.triggered.connect(lambda: app.win_settings.show())
        self.actionExport.triggered.connect(lambda: self._action_export())
        self.actionImport.triggered.connect(lambda: self._action_import())

    def _action_export(self):
        win = QtWidgets.QDialog()
        options = QtWidgets.QFileDialog().options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            win,
            "Bitte wähle eine .todo Datei zum Exportieren",
            "",
            "Todo Files (*.todo);;All Files (*)",
            options=options,
        )
        if filename:
            path = Path(filename)
            with open(path, "w") as f:
                f.writelines(dump(dict(task) for task in app.tasks.values()))

    def _action_import(self):
        win = QtWidgets.QDialog()
        options = QtWidgets.QFileDialog().options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            win,
            "Bitte wähle eine .todo Datei zum Importieren",
            "",
            "Todo Files (*.todo);;All Files (*)",
            options=options,
        )
        if filename:
            path = Path(filename)
            with open(path) as f:
                for d in load(f):
                    d = defaultdict(lambda: None, **d)
                    d["space"] = path.stem
                    if not d["do"]:
                        q(f"Tried to load a task with nothing to 'do': {d.items()}.")
                        continue

                    db.execute(
                        f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{d["space"]}')
"""
                    )

                    db.execute(
                        f"""
INSERT INTO tasks (do, space_id, done)
VALUES ('{d["do"]}',
(SELECT space_id from spaces WHERE name='{d["space"]}'),
{int(bool(d["done"]))}
)
"""
                    )
                    db.commit()

    def closeEvent(self, event):
        if self.killed:
            event.accept()
            return
        if app.win_running:
            app.win_running.show()
            app.win_running.raise_()
            return

        match QtWidgets.QMessageBox.question(
            self,
            "Watnu beenden?",
            "Bist du sicher, dass du Watnu beenden willst?",
        ):
            case QtWidgets.QMessageBox.StandardButton.Yes:
                event.accept()
                app.shutdown()

            case QtWidgets.QMessageBox.StandardButton.No:
                event.ignore()

    def set_statistics_icon(self):
        match statistics.get_today_finished():
            case 0:
                set_icon(self.button1, "extra/trending-up.svg")
            case 1:
                set_icon(self.button1, "extra/trending-up-1.svg")
            case 2:
                set_icon(self.button1, "extra/trending-up-2.svg")
            case 3:
                set_icon(self.button1, "extra/trending-up-3.svg")
            case 4:
                set_icon(self.button1, "extra/trending-up-4.svg")
            case 5:
                set_icon(self.button1, "extra/trending-up-5.svg")
            case 6:
                set_icon(self.button1, "extra/trending-up-6.svg")
            case 7:
                set_icon(self.button1, "extra/trending-up-7.svg")
            case 8:
                set_icon(self.button1, "extra/trending-up-8.svg")
            case 9:
                set_icon(self.button1, "extra/trending-up-9.svg")
            case _:
                set_icon(self.button1, "extra/trending-up-more.svg")

    def unlock(self):
        for button in [
            self.button1,
            self.button2,
            self.button3,
            self.button4,
            self.button5,
            self.button6,
            self.button7,
            self.button8,
            self.button9,
        ]:
            button.setEnabled(True)
