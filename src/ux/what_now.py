from collections import Counter, defaultdict
from itertools import count
from math import modf, sin
from random import choice, seed
from time import time, time_ns

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QTimer

import src.ui as ui
from src.classes import ACTIVITY
from src.functions import cached_getter
from src.logic import balance, get_doable_tasks, prioritize, schedule
from src.stuff import app, config
from src.ux import task_editor, task_finished, task_running

_translate = QCoreApplication.translate


class What_Now(QtWidgets.QDialog, ui.what_now.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task_priority = None
        self.task_timing = None
        self.task_balanced = None
        "Reminder that this window was opened by the user and should be reopened."
        self.taskfont = self.task_desc_priority.property("font")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
        )

        self.sec_timer = QTimer()
        "This timer is used to update the time remaining."
        self.animation_timer = QTimer()
        "This timer is used to animate the bars."
        self.gui_timer = QTimer()
        "This timer is used to update the GUI."

        self.balanced_tasks = None
        self.priority_tasks = None
        self.timing_tasks = None

        # @self.edit_priority.clicked.connect
        def edit_priority():
            win = task_editor.Editor(self.task_priority)
            app.list_of_task_editors.append(win)
            app.list_of_windows.append(win)
            if win.exec():
                self.lets_check_whats_next()

        # @self.edit_timing.clicked.connect
        def edit_timing():
            win = task_editor.Editor(self.task_timing)
            app.list_of_task_editors.append(win)
            app.list_of_windows.append(win)
            if win.exec():
                self.lets_check_whats_next()

        # @self.edit_balanced.clicked.connect
        def edit_balanced():
            win = task_editor.Editor(self.task_balanced)
            app.list_of_task_editors.append(win)
            app.list_of_windows.append(win)
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
                stop:0 {self.task_timing.primary_color}, 
                stop:{sin(T * 0.1) * 0.5 + 0.5} {self.task_timing.secondary_color},
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
            stop:0 {self.task_priority.primary_color},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {self.task_priority.secondary_color},
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
            stop:0 {self.task_balanced.primary_color},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {self.task_balanced.secondary_color},
            stop:1 white);
    }}
    """
                )
            else:
                self.frame_balanced.setStyleSheet("color: grey")

        @self.gui_timer.timeout.connect
        def gui_timer_timeout():
            # update the task descriptions
            if self.task_timing:
                self.task_desc_timing.setText(self.task_timing.do)
                self.task_desc_timing.adjustSize()
                self.task_space_timing.setText(self.task_timing.space.name)
            else:
                self.task_desc_timing.setText("Keine Aufgabe")
                self.task_space_timing.setText("")
            if self.task_priority:
                self.task_desc_priority.setText(self.task_priority.do)
                self.task_desc_priority.adjustSize()
                self.task_space_priority.setText(self.task_priority.space.name)
            else:
                self.task_desc_priority.setText("Keine Aufgabe")
                self.task_space_priority.setText("")
            if self.task_balanced:
                self.task_desc_balanced.setText(self.task_balanced.do)
                self.task_desc_balanced.adjustSize()
                self.task_space_balanced.setText(self.task_balanced.space.name)
            else:
                self.task_desc_balanced.setText("Keine Aufgabe")
                self.task_space_balanced.setText("")

        # @self.button4.clicked.connect
        def go_priority_clicked():
            self.hide()
            app.win_running = task_running.Running(self.task_priority)

        # @self.button1.clicked.connect
        def skip_priority_clicked():
            old_task = self.task_priority
            self.priority_tasks.rotate(-1)
            self.task_priority.set_last_checked(time())
            self.task_priority = self.priority_tasks[0]
            self.task_desc_priority.setText(self.task_priority.do)
            self.task_desc_priority.adjustSize()
            self.task_space_priority.setText(self.task_priority.space.name)

            if old_task == self.task_priority:
                QtWidgets.QMessageBox.information(
                    self,
                    "Hmm..",
                    """Es scheint, es gibt keine andere, ähnlich wichtige Aufgabe im Moment.
Auf gehts!""",
                )

        # @self.button6.clicked.connect
        def go_balanced_clicked():
            self.hide()
            app.win_running = task_running.Running(self.task_balanced)

        # @self.button3.clicked.connect
        def skip_balanced_clicked():
            self.task_balanced.set_last_checked(time())
            self.balanced_tasks.rotate(-1)
            self.task_balanced = self.balanced_tasks[0]
            self.task_desc_balanced.setText(self.task_balanced.do)
            self.task_desc_balanced.adjustSize()
            self.task_space_balanced.setText(self.task_balanced.space.name)

        def go_timing_clicked():
            self.hide()
            app.win_running = task_running.Running(self.task_timing)

        # @self.button2.clicked.connect
        def skip_timing_clicked():
            self.timing_tasks.rotate(-1)
            self.task_timing.set_last_checked(time())
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space.name)

        # @self.button7.clicked.connect
        def done_priority_clicked():
            if task_finished.Finisher(self.task_priority).exec():
                self.lets_check_whats_next()

        # @self.button9.clicked.connect
        def done_balanced_clicked():
            if task_finished.Finisher(self.task_balanced).exec():
                self.lets_check_whats_next()

        @self.button5.clicked.connect
        def throw_coins():
            # vonNeumann!
            i = 0
            first = 0
            for i in count():
                # least significant bit of high-res time *should* give enough entropy
                first = (time_ns() // 100) & 1
                second = (time_ns() // 100) & 1
                if first != second:
                    break
            # 'threw 31688 pairs!' - so much for "should"
            # bitshift to the left
            config.coin <<= 1
            # then set the bit -
            config.coin |= first
            seed((config.coin ^ config.lucky_num) * config.count)
            config.count += 1

            x = choice(["Kopf", "Zahl"])
            mb = QtWidgets.QMessageBox()
            mb.setWindowTitle("Hmm..")
            if x == "Kopf":
                mb.setText("Du hast Kopf geworfen!")
                mb.setIconPixmap(QtGui.QPixmap(str(config.base_path / "extra/feathericons/coin-heads.svg")))
            else:
                mb.setText("Du hast Zahl geworfen!")
                mb.setIconPixmap(QtGui.QPixmap(str(config.base_path / "extra/feathericons/coin-tails.svg")))
            mb.exec()

    @cached_getter
    def lets_check_whats_next(self):
        seed((config.coin ^ config.lucky_num) * config.count)
        config.count += 1

        self.groups = defaultdict(lambda: [])

        self.tasks = get_doable_tasks(app.tasks.values())

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
        self.hide()
        app.win_main.show()
        app.win_main.statusBar.clearMessage()
        self.sec_timer.stop()
        self.animation_timer.stop()
        for win in app.list_of_task_lists:
            win.gui_timer.start(100)
            win.show()

    def set_task_priority(self):
        self.priority_tasks = prioritize(self.tasks)
        self.task_priority = self.priority_tasks[0]
        self.task_desc_priority.setText(self.task_priority.do)
        self.task_desc_priority.adjustSize()
        self.task_space_priority.setText(self.task_priority.space.name)

    def set_timing_task(self):
        try:
            self.timing_tasks = schedule(self.tasks)
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space.name)

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
        activity_time_spent = Counter()

        for task in app.tasks.values():
            if task.primary_activity != ACTIVITY.unspecified:
                activity_time_spent[task.primary_activity.value] += task.total_time_spent
            if task.secondary_activity != ACTIVITY.unspecified:
                activity_time_spent[task.secondary_activity.value] += task.total_time_spent * 0.382

        activity_time_spent[None] = max(activity_time_spent.values())

        self.balanced_tasks = balance(self.tasks, activity_time_spent)
        if not self.balanced_tasks:
            return
        self.task_balanced = self.balanced_tasks[0]
        self.task_desc_balanced.setText(self.task_balanced.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.task_balanced.space.name)

    def showEvent(self, event):
        for win in app.list_of_task_lists:
            win.gui_timer.stop()
            win.hide()
        for win in app.list_of_task_organizers:
            win.gui_timer.stop()
            win.hide()
        super().showEvent(event)

    def close(
        self,
    ) -> None:
        self.sec_timer.stop()
        self.animation_timer.stop()
        super().close()

    def hide(self):
        self.sec_timer.stop()
        self.animation_timer.stop()
        self.gui_timer.stop()
        super().hide()

    def show(self):
        self.lets_check_whats_next()
        self.sec_timer.start(1000)
        self.animation_timer.start(15)
        self.gui_timer.start(1000)
        super().show()
