import contextlib
import signal
import sys
import webbrowser
from collections import defaultdict
from pathlib import Path

import stay
import use
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QPushButton

import src.ui as ui
from src.logic import filter_filter_history
from src.stuff import app, config, db
from src.ux import (
    about,
    attributions,
    statistics,
    task_checklist,
    task_editor,
    task_list,
    task_organizer,
)

_translate = QCoreApplication.translate

dump = stay.Encoder()
load = stay.Decoder()

q = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/q/main/q.py"),
    modes=use.recklessness,
    import_as="q",
).Q()


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

    # def keyPressEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Control:
    #         print("control pressed")
    #     else:
    #         super().keyPressEvent(event)


class MainWindow(QtWidgets.QMainWindow, ui.main_window.Ui_MainWindow):
    def quit(self, num, frame):
        self.killed = True
        self.cleanup()
        self.close()
        sys.exit(0)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.gui_timer = QtCore.QTimer()
        self.statusBar.setSizeGripEnabled(False)
        self.num_buttons = [
            self.button1,
            self.button2,
            self.button3,
            self.button4,
            self.button5,
            self.button6,
            self.button7,
            self.button8,
            self.button9,
        ]

        self.set_statistics_icon()
        # self.set_icon(self.button1, "statistics.svg")
        set_icon(self.button3, "extra/organisation.svg")
        set_icon(self.button2, "extra/feathericons/inventory.svg")
        set_icon(self.button4, "extra/feathericons/list.svg")
        set_icon(self.button5, "extra/feathericons/play-circle.svg")
        set_icon(self.button6, "extra/feathericons/file-plus.svg")
        self.movie = QtGui.QMovie(str(config.base_path / "extra/600-cell-unscreen.gif"))
        # self.movie.frameChanged.connect(self.set_icon)
        self.movie.start()
        # set_icon(self.button7, "extra/600-cell.gif")
        self.button7.setIconSize(QtCore.QSize(30, 30))
        set_icon(self.button8, "extra/checklist.svg")
        set_icon(self.button9, "extra/superhero - attribute to Freepik.svg")

        self.killed = False

        # catch ctrl+c and register it as a quit
        signal.signal(signal.SIGINT, self.quit)

        self.gui_timer.start(100)

        @self.gui_timer.timeout.connect
        def _():
            self.button7.setIcon(QtGui.QIcon(self.movie.currentPixmap()))

        @self.about.triggered.connect
        def _():
            about.About().exec()

        @self.actionReadme.triggered.connect
        def _():
            webbrowser.open("https://github.com/amogorkon/watnu/blob/main/README.md")

        @self.attributions.triggered.connect
        def _():
            attributions.Attributions().exec()

        @self.button7.clicked.connect
        def tetraplex():
            # app.win_companions.show()
            # webbrowser.open("https://github.com/amogorkon/tetraplex")
            breakpoint()

        @self.button8.clicked.connect
        def checklist():
            win = task_checklist.CheckList()
            for win in app.list_of_task_checklists:
                win.show()

        @self.button9.clicked.connect
        def character():
            app.win_character.show()

        @self.button4.clicked.connect
        def list_tasks():
            """Task List."""
            win = task_list.TaskList()
            for win in app.list_of_task_lists:
                win.show()

        @self.button5.clicked.connect
        def whatnow():
            """Watnu?!"""
            self.statusBar.clearMessage()
            self.repaint()
            app.win_what.lets_check_whats_next()
            app.win_what.show()
            self.hide()

        @self.button6.clicked.connect
        def add_new_task():
            """Add new Task."""
            win = task_editor.Editor()
            for win in app.list_of_task_editors:
                win.show()

        @self.button1.clicked.connect
        def statistics():
            app.win_statistics.show()

        @self.button3.clicked.connect
        def organize():
            win = task_organizer.Organizer()
            for win in app.list_of_task_organizers:
                win.show()

        @self.button2.clicked.connect
        def inventory():
            app.win_inventory.show()

        @self.actionSupportMe.triggered.connect
        def actionSupportMe_triggered():
            webbrowser.open("paypal.me/amogorkon")

        @self.actionIssue_Tracker.triggered.connect
        def actionIssueTracker():
            webbrowser.open("https://github.com/amogorkon/watnu/issues")

        @self.actionContact.triggered.connect
        def actionContact():
            webbrowser.open("https://calendly.com/d/2fm-27w-njm/office-hours")

        @self.actionSettings.triggered.connect
        def actionSettings():
            app.win_settings.show()

        @self.actionExport.triggered.connect
        def actionExport():
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

        @self.actionImport.triggered.connect
        def actionImport():
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
                self.cleanup()

            case QtWidgets.QMessageBox.StandardButton.No:
                event.ignore()

    def cleanup(self):
        with contextlib.suppress(RuntimeError):  # ignore annoying last-minute exceptions
            app.tray.setVisible(False)
            app.tray.deleteLater()

        app.closeAllWindows()
        config.save()
        with open(config.base_path / "filter_history.stay", "w") as f:
            f.write("\n".join(filter_filter_history(app.filter_history)))

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
        for button in self.num_buttons:
            button.setEnabled(True)
            button.setEnabled(True)
