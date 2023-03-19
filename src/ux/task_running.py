import webbrowser
from collections import defaultdict
from datetime import datetime
from math import modf, sin
from random import choice, seed
from time import time

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QTimer
from PyQt6.QtSql import QSqlDatabase

import config
import q
import ui
from logic import (
    balance,
    check_task_conditions,
    constraints_met,
    filter_tasks,
    prioritize,
    schedule,
    skill_level,
)
from classes import EVERY, ILK, Every, Task, cached_and_invalidated, iter_over, submit_sql, typed
from config import Config
from ux import app, task_editor, task_finished, task_running

from .stuff import __version__, app, config, db


class Running(QtWidgets.QDialog, ui.task_running.Ui_Dialog):
    def __init__(self, task):
        if app.win_running is not None:
            app.win_running.show()
            app.win_running.raise_()
            return
        else:
            app.win_running = self

        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
        )
        app.win_main.hide()

        app.win_settings.hide()

        self.task: Task = task
        self.skill_levels = [(skill.id, int(skill_level(skill.time_spent))) for skill in task.skills]

        self.paused = False
        self.start_time = time()
        # ticks are easier to work with in the GUI, but start/stop is used for reference in the session
        # ticks is the time tracked during the session in seconds
        self.ticks = 0
        self.paused_ticks = 0
        self.session_adjust_time_spent = 0

        self.task.last_checked = self.start_time
        self.timer = QTimer()
        self.animation_timer = QTimer()
        self.animation_timer.start(15)

        doc = QtGui.QTextDocument(task.notes)
        self.notes.setDocument(doc)

        doc = QtGui.QTextDocument(task.do)
        self.desc.setDocument(doc)

        for task_list in app.list_of_task_lists:
            task_list.button5.setEnabled(False)

        if self.task.resources:
            self.open_resources.setEnabled(True)
            text = "; ".join(url for url, ID in self.task.resources)
            self.open_resources.setText(str(text))

        self.task_space.setText(task.space)

        self.show()
        self.start_task()
        self.timer.start(1000)

        @self.animation_timer.timeout.connect
        def animation_timer_timeout():
            if self.task is None:
                return
            T = time()
            self.frame.setStyleSheet(
                f"""
* {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
        stop:0 black, 
        stop:1 white);
background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
        stop:0 {app.activity_color.get(self.task.primary_activity_id, "black")},
        stop:{sin(T * 0.9) * 0.5 + 0.5} {app.activity_color.get(self.task.secondary_activity_id,
                                                            app.activity_color.get(self.task.primary_activity_id, "black"))},
        stop:1 white);
}}
"""
            )

        @self.open_resources.clicked.connect
        def _():
            for url, _ in self.task.resources:
                webbrowser.open(url)

        @self.notes.document().contentsChanged.connect
        def _():
            query = statement = f"""
            UPDATE tasks SET notes= {self.notes.document().toMarkdown()}
            WHERE id={self.task.id}
            """
            if not query.exec():
                q("SQL failed:\n" + statement)
                q(query.lastError().text())
            return

        @self.timer.timeout.connect
        # timeout happens every 1 sec
        def _():
            if self.paused:
                self.paused_ticks += 1
                return

            self.ticks += 1

            session_total = self.ticks + self.session_adjust_time_spent

            rst, days = modf(session_total / (24 * 60 * 60))
            rst, hours = modf(rst * 24)
            rst, minutes = modf(rst * 60)
            seconds = rst * 60
            self.LCD_days.setProperty("intValue", days)
            self.LCD_hours.setProperty("intValue", hours)
            self.LCD_minutes.setProperty("intValue", minutes)
            self.LCD_seconds.setProperty("intValue", seconds)

        @self.button1.clicked.connect
        def _():
            pass

        @self.button2.clicked.connect
        def paused():
            if not self.paused:
                self.button2.setText("Unpause")
                self.paused = True
            else:
                self.button2.setText("Pause")
                self.paused = False

        @self.button3.clicked.connect
        def reset_button():
            self.start_time = time()
            self.session_adjust_time_spent = 0
            self.ticks = 0
            self.paused_ticks = 0

        @self.button4.clicked.connect
        def _():
            pass

        @self.button5.clicked.connect
        def stop_for_now_button():
            stop_time = time()
            if self.timer.isActive():
                self.timer.stop()
            self.task.last_checked = stop_time
            self.task.adjust_time_spent = self.session_adjust_time_spent
            self.hide()
            app.write_session(
                self.task.id, self.start_time, stop_time, finished=False, pause_time=self.paused_ticks
            )
            app.win_main.show()

            if not app.win_what.isHidden():
                app.win_what.raise_()

        @self.button6.clicked.connect
        def _():
            self.paused = True
            win = task_editor.Editor(draft=True)
            win.exec()
            self.paused = False

        @self.button7.clicked.connect
        def minus5_button():
            if (self.session_adjust_time_spent + self.ticks) >= 5 * 60:
                self.session_adjust_time_spent -= 5 * 60
            else:
                self.session_adjust_time_spent = -self.ticks

        @self.button8.clicked.connect
        def finish_task_button():
            if timer_was_running := self.timer.isActive():
                self.timer.stop()
            win = task_finished.Task_Finished(self.task, start=self.start_time, pause_time=self.paused_ticks)
            if not win.exec():
                if timer_was_running:
                    self.timer.start()
                return
            self.hide()
            app.win_main.show()
            if not app.win_what.isHidden() and app.win_what:
                app.win_what.raise_()

        @self.button9.clicked.connect
        def plus5_button():
            self.session_adjust_time_spent += 5 * 60

    def cancel(self):
        """Hard cancel - no button for this, just Esc"""
        self.timer.stop()
        self.ticks = 0  #
        self.task.last_checked = time()
        self.task = None

        for win in app.list_of_task_lists:
            win.button5.setEnabled(True)
            win.timer.start(100)
            win.filter_timer.start(1000)

        if app.list_of_task_lists:
            for win in app.list_of_task_lists:
                win.show()
                win.raise_()
        else:
            app.win_what.show()
            app.win_what.raise_()

        super().reject()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel()
        event.accept()

    def start_task(self):
        # check if working conditions are optimal once a day
        query = submit_sql(
            """
        SELECT start 
        FROM sessions
        ORDER BY start DESC;
        """
        )

        last_started = query.value(0) if query.next() else 0
        now = datetime.now()
        then = datetime.fromtimestamp(last_started)

        if now.date() != then.date():
            QtWidgets.QMessageBox.information(
                self,
                "Checkliste",
                """
Checkliste für optimale Produktivität:
- Raumtemperatur bei 21°C?
- Ausleuchtung bei 1000 Lux?
- Relative Luftfeuchtigkeit bei ~50%?
- Kaffee/Tee & genug Wasser zur Hand?
- Ausgeruht? Geist fokusiert?
- Körper in Schwung?
- Das Richtige auf den Ohren?
""",
            )
        mantra = choice(config.mantras.read_text(encoding="utf8").splitlines())

        QtWidgets.QMessageBox.information(
            self,
            "Gesundheitshinweis",
            f"""
Alle ~25 Minuten kurz Stoßlüften & ausreichend Wasser trinken :)



{mantra or "Always look on the bright side of life!"}
""",
        )

    def finished(self):
        for win in app.list_of_task_lists:
            win.button5.setEnabled(True)
            win.timer.start(100)
            win.filter_timer.start(1000)
