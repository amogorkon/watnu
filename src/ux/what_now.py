from __future__ import annotations

import webbrowser
from collections import Counter, defaultdict
from enum import Enum
from itertools import count
from math import modf, sin
from random import choice, seed
from time import time, time_ns
from typing import Deque

from beartype import beartype
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QKeyEvent, QKeySequence, QPainter, QPixmap, QShortcut, QShowEvent
from PyQt6.QtWidgets import QButtonGroup, QDialog, QMenu, QMessageBox

from src import app, config, db, ui
from src.classes import ACTIVITY, Task
from src.helpers import cached_getter
from src.logic import balance, get_doable_tasks, prioritize, schedule

from . import task_editor, task_finished, task_running
from .helpers import tasks_to_json, to_clipboard

SELECT = Enum("SELECT", "BALANCE PRIORITY TIMING")

STYLE_SELECTED = """
    border: 1px solid rgba(0, 0, 0, 0.3);
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 255, 255, 255),
        stop:0.5 rgba(200, 200, 200, 255),
        stop:1 rgba(255, 255, 255, 255)
    );
    color: black;
"""
GREY = "color: grey;"
NO_TASK = "Keine Aufgabe"


class CustomMenu(QMenu):
    def keyPressEvent(self, event):
        text = event.text()
        if text == "1":
            self.actions()[0].trigger()
            self.close()
        elif text == "2":
            self.actions()[1].trigger()
            self.close()
        elif text == "3":
            self.actions()[2].trigger()
            self.close()
        else:
            super().keyPressEvent(event)


@beartype
class WhatNow(QDialog, ui.what_now.Ui_Dialog):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self._init_defaults()
        self._init_ui_elements()
        self._init_signals()

    def _init_defaults(self) -> None:
        self.timing_tasks: Deque[Task] | None = None
        self.balance_tasks: Deque[Task] | None = None
        self.priority_tasks: Deque[Task] | None = None
        self.priority_task: Task | None = None
        self.timing_task: Task | None = None
        self.balance_task: Task | None = None

        self.selected: SELECT | None = None

        self.sec_timer = QTimer()
        "This timer is used to update the time remaining."
        self.animation_timer = QTimer()
        "This timer is used to animate the bars."
        self.gui_timer = QTimer()
        "This timer is used to update the GUI."

    def _init_ui_elements(self) -> None:
        self.taskfont = self.task_desc_priority.property("font")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
        )
        self.menu3 = CustomMenu(self)
        self.action1 = QAction("DeepSeek", self)
        self.action2 = QAction("Gemini", self)
        self.action3 = QAction("Copilot", self)
        self.action1.triggered.connect(lambda: self._open_ai("deepseek"))
        self.action2.triggered.connect(lambda: self._open_ai("gemini"))
        self.action3.triggered.connect(lambda: self._open_ai("copilot"))
        self.action1.setShortcut(QKeySequence("1"))
        self.action2.setShortcut(QKeySequence("2"))
        self.action3.setShortcut(QKeySequence("3"))

        self.menu3.addAction(self.action1)
        self.menu3.addAction(self.action2)
        self.menu3.addAction(self.action3)

        self.task_selection_button_group = QButtonGroup(self)
        self.task_selection_button_group.addButton(self.button7)
        self.task_selection_button_group.addButton(self.button8)
        self.task_selection_button_group.addButton(self.button9)
        self.task_selection_button_group.setExclusive(True)

        self.button7.setVisible(False)
        self.button8.setVisible(False)
        self.button9.setVisible(False)

        self.setFocus()  # Q.Key.Space doesn't work without this!

    def _menu3_open(self):
        self.menu3.exec(self.button3.mapToGlobal(self.button3.rect().bottomLeft()))

    def _init_signals(self) -> None:
        shortcut_open_menu = QShortcut(QKeySequence("3"), self)
        shortcut_open_menu.activated.connect(self._menu3_open)

        def _select_priority(event):
            if self.priority_task:
                _unselect_all()
                if self.selected is SELECT.PRIORITY:
                    self.selected = None
                else:
                    self.selected = SELECT.PRIORITY
                    self.priority.setStyleSheet(STYLE_SELECTED)

        def _select_timing(event):
            if self.timing_task:
                _unselect_all()
                if self.selected is SELECT.TIMING:
                    self.selected = None
                else:
                    self.selected = SELECT.TIMING
                    self.timing.setStyleSheet(STYLE_SELECTED)

        def _select_balance(event):
            if self.balance_task:
                _unselect_all()
                if self.selected is SELECT.BALANCE:
                    self.selected = None
                else:
                    self.selected = SELECT.BALANCE
                    self.balance.setStyleSheet(STYLE_SELECTED)

        def _unselect_all():
            self.priority.setStyleSheet(None)
            self.timing.setStyleSheet(None)
            self.balance.setStyleSheet(None)

        self.priority.mousePressEvent = _select_priority
        self.timing.mousePressEvent = _select_timing
        self.balance.mousePressEvent = _select_balance

        self.sec_timer.timeout.connect(self._sec_timer_timeout)
        self.animation_timer.timeout.connect(self._animation_timer_timeout)
        self.gui_timer.timeout.connect(self._gui_timer_timeout)

        self.button1.clicked.connect(lambda: throw_coins())
        self.button2.clicked.connect(self._task_done)
        self.button3.clicked.connect(self._menu3_open)
        self.button4.clicked.connect(self._edit_task)
        self.button5.clicked.connect(self._run_task)
        self.button6.clicked.connect(self._new_task)
        self.button7.installEventFilter(self)
        self.button8.installEventFilter(self)
        self.button9.installEventFilter(self)

    def _open_ai(self, kind: str):
        text = "Welche Aufgabe soll ich als nächstes machen?\n\n" + tasks_to_json([
            self.priority_task,
            self.timing_task,
            self.balance_task,
        ])
        to_clipboard(text)

        if config.show_whatnow_ai_clipboard_info:
            QMessageBox.information(
                self,
                "Information",
                "Aufgaben wurden als Text kopiert. Bitte in das Chat-Feld der KI einfügen.",
            )

        match kind:
            case "deepseek":
                webbrowser.open_new_tab("https://chat.deepseek.com/")
            case "gemini":
                webbrowser.open_new_tab("https://gemini.google.com/app")
            case "copilot":
                webbrowser.open_new_tab("https://copilot.microsoft.com/chats")

    def _skip_task(self):
        match self.selected:
            case SELECT.PRIORITY:
                self.skip_priority()
            case SELECT.TIMING:
                self.skip_timing()
            case SELECT.BALANCE:
                self.skip_balance()
            case _:
                self.skip_timing()
                self.skip_balance()
                self.skip_priority()
        self.setFocus()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        match event.key():
            case Qt.Key.Key_7 if self.priority_task:
                self.priority.mousePressEvent(None)
            case Qt.Key.Key_8 if self.timing_task:
                self.timing.mousePressEvent(None)
            case Qt.Key.Key_9 if self.balance_task:
                self.balance.mousePressEvent(None)
            case Qt.Key.Key_Space:
                print("Space pressed", time())
                self._skip_task()
            case Qt.Key.Key_Enter | Qt.Key.Key_Return:
                self._edit_task()
            case _:
                super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.hasFocus():
            painter.setPen(QColor("red"))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    @cached_getter
    def lets_check_whats_next(self) -> bool:
        """
        This method selects the next task to be done based on the current state.
        It sets the task priority, balance, and timing, and returns True if there are tasks to be done,
        False if there are no tasks.
        """
        seed((config.coin ^ config.lucky_num) * config.count)
        config.count += 1

        self.groups = defaultdict(lambda: [])

        self.tasks = get_doable_tasks(app.tasks.values(), db=db)

        if not self.tasks:
            QMessageBox.information(
                self,
                "Hmm..",
                "Es sind noch keine Aufgaben gestellt aus denen ausgewählt werden könnte.",
            )
            self.hide()
            return False

        self.set_task_priority()
        self.set_task_balanced()
        self.set_timing_task()
        return True

    def _sec_timer_timeout(self):
        T: float
        # every full second
        if self.timing_task:
            T = time()
            diff = self.timing_task.deadline - T
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

    def _animation_timer_timeout(self):
        T = time()
        if self.timing_task:
            self.frame_timing.setStyleSheet(
                f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0,
            stop:0 black,
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0,
            stop:0 {self.timing_task.primary_color},
            stop:{sin(T * 0.1) * 0.5 + 0.5} {self.timing_task.secondary_color},
            stop:1 white);
    }}
    """
            )
        else:
            self.frame_timing.setStyleSheet(GREY)

        if self.priority_task:
            self.frame_priority.setStyleSheet(
                f"""
* {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0,
        stop:0 black,
        stop:1 white);
background: qlineargradient(x1:0 y1:0, x2:1 y2:0,
        stop:0 {self.priority_task.primary_color},
        stop:{sin(T * 0.1) * 0.5 + 0.5} {self.priority_task.secondary_color},
        stop:1 white);
}}
"""
            )
        else:
            self.frame_priority.setStyleSheet(GREY)

        if self.balance_task:
            self.frame_balanced.setStyleSheet(
                f"""
* {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0,
        stop:0 black,
        stop:1 white);
background: qlineargradient(x1:0 y1:0, x2:1 y2:0,
        stop:0 {self.balance_task.primary_color},
        stop:{sin(T * 0.1) * 0.5 + 0.5} {self.balance_task.secondary_color},
        stop:1 white);
}}
"""
            )
        else:
            self.frame_balanced.setStyleSheet(GREY)

    def _gui_timer_timeout(self):
        # update the task descriptions
        if self.timing_task:
            self.task_desc_timing.setText(self.timing_task.do)
            self.task_desc_timing.adjustSize()
            self.task_space_timing.setText(self.timing_task.space.name)
        else:
            self.task_desc_timing.setText(NO_TASK)
            self.task_space_timing.setText("")
        if self.priority_task:
            self.task_desc_priority.setText(self.priority_task.do)
            self.task_desc_priority.adjustSize()
            self.task_space_priority.setText(self.priority_task.space.name)
        else:
            self.task_desc_priority.setText(NO_TASK)
            self.task_space_priority.setText("")
        if self.balance_task:
            self.task_desc_balanced.setText(self.balance_task.do)
            self.task_desc_balanced.adjustSize()
            self.task_space_balanced.setText(self.balance_task.space.name)
        else:
            self.task_desc_balanced.setText(NO_TASK)
            self.task_space_balanced.setText("")

    def reject(self) -> None:
        super().reject()
        self.hide()
        app.win_main.show()
        app.win_main.statusBar.clearMessage()
        self.sec_timer.stop()
        self.animation_timer.stop()
        for win in app.list_of_task_lists:
            win.gui_timer.start(100)
            win.show()

    def _task_done(self, event=None) -> None:
        if not self.selected:
            return
        match self.selected:
            case SELECT.PRIORITY:
                done = task_finished.Finisher(self.priority_task).exec()
            case SELECT.TIMING:
                done = task_finished.Finisher(self.timing_task).exec()
            case SELECT.BALANCE:
                done = task_finished.Finisher(self.balance_task).exec()
        if done:
            self.lets_check_whats_next()

    def _edit_task(self):
        if not self.selected:
            return
        match self.selected:
            case SELECT.PRIORITY:
                win = task_editor.TaskEditor(self.priority_task)
            case SELECT.TIMING:
                win = task_editor.TaskEditor(self.timing_task)
            case SELECT.BALANCE:
                win = task_editor.TaskEditor(self.balance_task)

        if win.exec():
            self.lets_check_whats_next()

    def _run_task(self):
        if not self.selected:
            return
        self.hide()
        match self.selected:
            case SELECT.PRIORITY:
                app.win_running = task_running.Running(self.priority_task)
            case SELECT.TIMING:
                app.win_running = task_running.Running(self.timing_task)
            case SELECT.BALANCE:
                app.win_running = task_running.Running(self.balance_task)

    def _new_task(self):
        win = task_editor.TaskEditor()
        if win.exec():
            self.lets_check_whats_next()

    def skip_priority(self) -> None:
        old_task = self.priority_task
        self.priority_tasks.rotate(-1)
        self.priority_task.set_last_checked(time())
        self.priority_task = self.priority_tasks[0]
        self.task_desc_priority.setText(self.priority_task.do)
        self.task_desc_priority.adjustSize()
        self.task_space_priority.setText(self.priority_task.space.name)

        if old_task == self.priority_task:
            QMessageBox.information(
                self,
                "Hmm..",
                """Es scheint, es gibt keine andere, ähnlich wichtige Aufgabe im Moment.
Auf gehts!""",
            )

    def skip_timing(self) -> None:
        if not self.timing_task:
            return
        self.timing_tasks.rotate(-1)
        self.timing_task.set_last_checked(time())
        self.timing_task = self.timing_tasks[0]
        self.task_desc_timing.setText(self.timing_task.do)
        self.task_space_timing.setText(self.timing_task.space.name)

    def skip_balance(self) -> None:
        self.balance_task.set_last_checked(time())
        self.balance_tasks.rotate(-1)
        self.balance_task = self.balance_tasks[0]
        self.task_desc_balanced.setText(self.balance_task.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.balance_task.space.name)

    def set_task_priority(self) -> None:
        self.priority_tasks = prioritize(self.tasks)
        self.priority_task = self.priority_tasks[0]
        self.task_desc_priority.setText(self.priority_task.do)
        self.task_desc_priority.adjustSize()
        self.task_space_priority.setText(self.priority_task.space.name)

    def set_timing_task(self) -> None:
        try:
            self.timing_tasks = schedule(self.tasks)
            self.timing_task = self.timing_tasks[0]
            self.task_desc_timing.setText(self.timing_task.do)
            self.task_space_timing.setText(self.timing_task.space.name)

        except IndexError:
            self.set_timing_empty()
        else:
            self.set_timing_header(False, True)
        self.task_desc_timing.adjustSize()

    def set_timing_empty(self) -> None:
        self.task_desc_timing.setText("nix was präsiert")
        self.set_timing_header(True, False)
        self.timing_task = None
        self.deadline = None
        self.deadline_weeks.display("")
        self.deadline_days.display("")
        self.deadline_hours.display("")
        self.deadline_minutes.display("")
        self.deadline_seconds.display("")

    def set_timing_header(self, italic: bool, enabled: bool) -> None:
        self.taskfont.setItalic(italic)
        self.task_desc_timing.setFont(self.taskfont)
        self.timing.setEnabled(enabled)

    def set_task_balanced(self) -> None:
        activity_time_spent = Counter()

        for task in app.tasks.values():
            if task.primary_activity != ACTIVITY.unspecified:
                activity_time_spent[task.primary_activity.value] += task.total_time_spent
            if task.secondary_activity != ACTIVITY.unspecified:
                activity_time_spent[task.secondary_activity.value] += task.total_time_spent * 0.382

        activity_time_spent[None] = max(activity_time_spent.values())

        self.balance_tasks = balance(self.tasks, activity_time_spent)
        if not self.balance_tasks:
            return
        self.balance_task = self.balance_tasks[0]
        self.task_desc_balanced.setText(self.balance_task.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.balance_task.space.name)

    def showEvent(self, event: QShowEvent) -> None:
        for win in app.list_of_task_lists:
            win.gui_timer.stop()
            win.hide()
        for win in app.list_of_task_organizers:
            win.gui_timer.stop()
            win.hide()
        super().showEvent(event)

    def close(self) -> None:
        self.sec_timer.stop()
        self.animation_timer.stop()
        super().close()

    def hide(self) -> None:
        self.sec_timer.stop()
        self.animation_timer.stop()
        self.gui_timer.stop()
        super().hide()

    def show(self) -> None:
        self.lets_check_whats_next()
        self.sec_timer.start(1000)
        self.animation_timer.start(15)
        self.gui_timer.start(1000)
        super().show()


def throw_coins() -> None:
    """
    Simulates a coin toss by using the least significant bit of high-resolution time as entropy source.


    The function then displays a message box with the result of the coin toss.
    """
    first = 0
    for _ in count():
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
    mb = QMessageBox()
    mb.setWindowTitle("Hmm..")
    if x == "Kopf":
        mb.setText("Du hast Kopf geworfen!")
        mb.setIconPixmap(QPixmap(str(config.base_path / "extra/feathericons/coin-heads.svg")))
    else:
        mb.setText("Du hast Zahl geworfen!")
        mb.setIconPixmap(QPixmap(str(config.base_path / "extra/feathericons/coin-tails.svg")))
    mb.exec()
