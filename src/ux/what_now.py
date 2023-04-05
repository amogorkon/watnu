from collections import defaultdict
from math import modf, sin
from random import seed
from time import time

import use
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QTimer

import ui
from classes import typed, typed_row
from logic import balance, get_doable_tasks, prioritize, schedule
from stuff import app, config, db
from ux import task_editor, task_finished, task_running

_translate = QCoreApplication.translate


class What_Now(QtWidgets.QDialog, ui.what_now.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task_priority = None
        self.task_timing = None
        self.task_balanced = None
        self.shown = False
        "Reminder that this window was opened by the user and should be reopened."
        self.taskfont = self.task_desc_priority.property("font")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
        )
        self.sec_timer = QTimer()
        self.sec_timer.start(1000)
        self.animation_timer = QTimer()
        self.animation_timer.start(15)
        self.cancel.setShortcut(_translate("Dialog", "0"))

        self.balanced_tasks = None
        self.priority_tasks = None
        self.timing_tasks = None

        @self.edit_priority.clicked.connect
        def edit_priority():
            win = task_editor.Editor(self.task_priority)
            app.list_of_task_editors.append(win)
            if win.exec():
                self.lets_check_whats_next()

        @self.edit_timing.clicked.connect
        def edit_timing():
            win = task_editor.Editor(self.task_timing)
            app.list_of_task_editors.append(win)
            if win.exec():
                self.lets_check_whats_next()

        @self.edit_balanced.clicked.connect
        def edit_balanced():
            win = task_editor.Editor(self.task_balanced)
            app.list_of_task_editors.append(win)
            if win.exec():
                self.lets_check_whats_next()

        @self.sec_timer.timeout.connect
        def sec_timer_timeout():
            T: float
            # every full second
            if self.task_timing:
                T = time()
                diff = self.task_timing.deadline - T
                rst, weeks = modf(diff / (7 * 24 * 60 * 60))
                rst, days = modf(rst * 7)
                rst, hours = modf(rst * 24)
                rst, minutes = modf(rst * 60)
                rst, seconds = modf(rst * 60)

                self.deadline_weeks.setProperty("intValue", weeks)
                self.deadline_days.setProperty("intValue", days)
                self.deadline_hours.setProperty("intValue", hours)
                self.deadline_minutes.setProperty("intValue", minutes)
                self.deadline_seconds.setProperty("intValue", seconds)

        @self.animation_timer.timeout.connect
        def animation_timer_timeout():
            T = time()
            if self.task_timing:
                self.frame_timing.setStyleSheet(
                    f"""
        * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
                stop:0 black, 
                stop:1 white);
        background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
                stop:0 {app.activity_color.get(self.task_timing.primary_activity_id, "black")}, 
                stop:{sin(T * 0.1) * 0.5 + 0.5} {app.activity_color.get(self.task_timing.secondary_activity_id,
                                                                    app.activity_color.get(
                                                                        self.task_timing.primary_activity_id, "black"))},
                stop:1 white);
        }}
        """
                )
            else:
                self.frame_timing.setStyleSheet("color: grey")

            if self.task_priority:
                self.frame_priority.setStyleSheet(
                    f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
            stop:0 black, 
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
            stop:0 {app.activity_color.get(self.task_priority.primary_activity_id, "black")},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {app.activity_color.get(self.task_priority.secondary_activity_id,
                                                                app.activity_color.get(self.task_priority.primary_activity_id, "black"))},
            stop:1 white);
    }}
    """
                )
            else:
                self.frame_priority.setStyleSheet("color: grey")

            if self.task_balanced:
                self.frame_balanced.setStyleSheet(
                    f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
            stop:0 black, 
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
            stop:0 {app.activity_color.get(self.task_balanced.primary_activity_id, "black")},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {app.activity_color.get(self.task_balanced.secondary_activity_id,
                                                                app.activity_color.get(self.task_balanced.primary_activity_id, "black"))},
            stop:1 white);
    }}
    """
                )
            else:
                self.frame_balanced.setStyleSheet("color: grey")

        @self.go_priority.clicked.connect
        def go_priority_clicked():
            self.hide()
            app.win_running = task_running.Running(self.task_priority)

        @self.skip_priority.clicked.connect
        def skip_priority_clicked():
            old_task = self.task_priority
            self.priority_tasks.rotate(-1)
            self.task_priority.set_last_checked(time())
            self.task_priority = self.priority_tasks[0]
            self.task_desc_priority.setText(self.task_priority.do)
            self.task_desc_priority.adjustSize()
            self.task_space_priority.setText(self.task_priority.space)

            if old_task == self.task_priority:
                QtWidgets.QMessageBox.information(
                    self,
                    "Hmm..",
                    "Sorry, es scheint, es gibt keine andere, ähnlich wichtige Aufgabe im Moment.\nAuf gehts!",
                )

        @self.go_balanced.clicked.connect
        def go_balanced_clicked():
            self.hide()
            app.win_running = task_running.Running(self.task_balanced)

        @self.skip_balanced.clicked.connect
        def skip_balanced_clicked():
            self.task_balanced.set_last_checked(time())
            self.balanced_tasks.rotate(-1)
            self.task_balanced = self.balanced_tasks[0]
            self.task_desc_balanced.setText(self.task_balanced.do)
            self.task_desc_balanced.adjustSize()
            self.task_space_balanced.setText(self.task_balanced.space)

        @self.go_timing.clicked.connect
        def go_timing_clicked():
            self.hide()
            app.win_running = task_running.Running(self.task_timing)

        @self.skip_timing.clicked.connect
        def skip_timing_clicked():
            self.timing_tasks.rotate(-1)
            self.task_timing.set_last_checked(time())
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space)

        @self.cancel.clicked.connect
        def cancel_clicked_():
            self.hide()
            app.win_main.show()

        @self.done_priority.clicked.connect
        def done_priority_clicked():
            task_finished.Task_Finished(self.task_priority).exec()

        @self.done_balanced.clicked.connect
        def _done_balanced_clicked():
            task_finished.Task_Finished(self.task_balanced).exec()

        @self.done_timing.clicked.connect
        def done_timing_clicked():
            task_finished.Task_Finished(self.task_timing).exec()

    def lets_check_whats_next(self):
        seed((config.coin ^ config.lucky_num) * config.count)
        config.count += 1

        self.groups = defaultdict(lambda: [])

        self.tasks = get_doable_tasks(db)

        if not self.tasks:
            QtWidgets.QMessageBox.information(
                self, "Hmm..", "Es sind noch keine Aufgaben gestellt aus denen ausgewählt werden könnte."
            )
            self.hide()
            return False

        self.set_task_priority()
        self.set_task_balanced()
        self.set_timing_task()
        return True

    def reject(self):
        super().reject()
        self.shown = False
        app.win_main.show()
        app.win_main.statusBar.clearMessage()
        self.sec_timer.stop()
        self.animation_timer.stop()
        for L in app.list_of_task_lists:
            L.db_timer.start(100)
            L.filter_timer.start(1000)
            L.show()

    def set_task_priority(self):
        self.priority_tasks = prioritize(self.tasks)
        self.task_priority = self.priority_tasks[0]
        self.task_desc_priority.setText(self.task_priority.do)
        self.task_desc_priority.adjustSize()
        self.task_space_priority.setText(self.task_priority.space)

    def set_timing_task(self):
        try:
            self.timing_tasks = schedule(self.tasks)
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space)

        except IndexError:
            self.set_empty()
        else:
            self.set_timing_header(False, True)
        self.task_desc_timing.adjustSize()

    def set_timing_empty(self):
        self.task_desc_timing.setText("nix was präsiert")
        self.set_timing_header(True, False)
        self.task_timing = None
        self.deadline = None
        self.deadline_weeks.display("")
        self.deadline_days.display("")
        self.deadline_hours.display("")
        self.deadline_minutes.display("")
        self.deadline_seconds.display("")

    def set_timing_header(self, italic, enabled):
        self.taskfont.setItalic(italic)
        self.task_desc_timing.setFont(self.taskfont)
        self.timing.setEnabled(enabled)

    def set_task_balanced(self):
        activity_time_spent = defaultdict(lambda: 0)
        query = db.execute(
            """
SELECT
    activity_id,
    adjust_time_spent
FROM activities
WHERE activity_id not NULL
"""
        )
        for activity_id, adjust_time_spent in query.fetchall():
            activity_time_spent[typed(activity_id, int, default=None)] = typed(adjust_time_spent, int)

        query = db.execute(
            """
SELECT
    primary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    primary_activity_id;
"""
        )

        for row in query.fetchall():
            activity_time_spent[typed_row(row, 0, int, default=0)] += typed_row(row, 1, int)

        query = db.execute(
            """
SELECT
    secondary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    secondary_activity_id;
"""
        )
        for row in query.fetchall():
            activity_time_spent[typed_row(row, 0, int, default=0)] += int(
                typed_row(row, 1, int, default=0) * 0.382
            )
        activity_time_spent[None] = max(activity_time_spent.values())

        self.balanced_tasks = balance(self.tasks, activity_time_spent)

        self.task_balanced = self.balanced_tasks[0]
        self.task_desc_balanced.setText(self.task_balanced.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.task_balanced.space)

    def showEvent(self, event):
        for L in app.list_of_task_lists:
            L.db_timer.stop()
            L.filter_timer.stop()
            L.hide()
        super().showEvent(event)

    def close(
        self,
    ) -> None:
        self.shown = False
        self.sec_timer.stop()
        self.animation_timer.stop()
        super().close()

    def show(self):
        super().show()
        self.shown = True
