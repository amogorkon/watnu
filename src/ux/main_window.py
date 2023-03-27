import webbrowser
from collections import defaultdict
from pathlib import Path

import q
import stay
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication

import ui
from stuff import __version__, app, config, db
from ux import about, attributions, task_editor, task_list

_translate = QCoreApplication.translate

load = stay.Decoder()


class MainWindow(QtWidgets.QMainWindow, ui.main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

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
        def _():
            pass

        @self.button8.clicked.connect
        def companions():
            app.win_companions.show()

        @self.button9.clicked.connect
        def community():
            """Community."""
            webbrowser.open("https://watnu.slack.com/archives/C01HKH7R4AC")

        @self.button4.clicked.connect
        def list_tasks():
            """Task List."""
            win = task_list.TaskList()
            win.show()
            app.list_of_task_lists.append(win)

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
            win.show()
            app.list_of_editors.append(win)

        @self.button1.clicked.connect
        def statistics():
            app.win_statistics.show()

        @self.button2.clicked.connect
        def character():
            app.win_character.show()

        @self.button3.clicked.connect
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
            q("Not Implemented.")
            return

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
        app.tray.setVisible(False)
        app.win_what.close()
        app.win_settings.close()
        app.win_character.close()
        app.win_companions.close()
        app.win_inventory.close()
        app.win_statistics.close()
        for win in app.list_of_task_lists:
            win.close()
        for win in app.list_of_editors:
            win.close()
        config.save()
