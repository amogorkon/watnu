"""The entry point for watnu.

Run with python main.py and watch the magik happen!
"""

import logging
import sys
print("python:", sys.version)

import webbrowser

from shlex import split

import attr

from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from enum import Enum
from itertools import count
from math import isinf
from math import modf
from pathlib import Path
from pprint import pprint
from random import choice
from random import randint
from random import random
from random import seed
from time import time
from time import time_ns
from typing import List
from typing import NamedTuple
from typing import Optional
from uuid import UUID
from uuid import uuid4

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QTime
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimedia import QMediaPlaylist
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWinExtras import QWinTaskbarButton
from PyQt5.QtWinExtras import QWinTaskbarProgress


from ui import main_window
from ui import running_task
from ui import settings
from ui import statistics
from ui import task_finished
from ui import task_list
from ui import task_new
from ui import what_now

from algo import balance
from algo import check_task_conditions
from algo import filter_tasks
from algo import prioritize
from algo import schedule
from lib.fluxx import StateMachine
from lib.stay import Decoder
from telegram import tell_telegram

import config

from pathlib import Path

__version__ = (0, 0, 7)

_translate = QtCore.QCoreApplication.translate

load = Decoder()

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.CRITICAL)
logger = logging.getLogger(__name__)

ACTIVITY = Enum("ACTIVITY", "body mind spirit")
LEVEL = Enum("LEVEL", "MUST SHOULD MAY SHOULD_NOT MUST_NOT")
S = Enum("STATE", "init main editing running final")

# TODO: with attr?
class Task(NamedTuple):
    id: int
    do: str
    notes: str=""
    url: str=""
    attachments: str=None
    space_id: int=None
    draft: bool=False
    inactive: bool=False
    deleted: bool=False
    #priority: float = 0

    # deadline: float="inf"
    workload: int=None

    activity_id: int=None
    difficulty: float=5
    fear: float=5
    embarassment: float=5

    conditions: str=""
    secondary_activity_id: int=None

    @property
    def deadline(self):
        statement = f"""
        SELECT deadline, workload FROM tasks WHERE id={self.id}
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
        query.first()
        own_deadline, workload = float(query.value(0)), w if (w := query.value(1)) else 0

        return (min([t.deadline for t in self.required_by] + [own_deadline]) 
                - workload)

    @property
    def level_id(self):
        statement = f"""
        SELECT level_id FROM tasks WHERE id={self.id};
        """
        if not query.exec_(statement):
            logger.warning("SQL failed", statement)
            logger.warning(query.lastError().text())
        
        if query.first():
            own_level = query.value(0)
        else:
            raise AssertionError
        # recursion!
        return max([t.level_id for t in self.required_by] + [own_level])

    @property
    def priority(self):
        statement = f"""
        SELECT priority FROM tasks WHERE id={self.id}
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
        query.first()
        own_priority = query.value(0)
        assert isinstance(own_priority, float), (own_priority, type(own_priority))
        parent_priorities = max((t.priority for t in self.required_by), default=0)

        return own_priority + parent_priorities

    @property
    def space_priority(self):
        if self.space_id:
            statement = f"""
            SELECT priority FROM spaces WHERE space_id={self.space_id};
            """
            if not query.exec_(statement):
                logger.warning("SQL failed", statement)
                logger.warning(query.lastError().text())
            if not query.next():
                space_priority = 0
                print("space_priority is giving troubles again!")
            else:
                return x if (x := query.value(0)) is not None else 0
        else:
            return 0        

    def __last_checked():
        def fget(self):
            statement = f"""
            SELECT last_checked FROM tasks WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            query.first()
            x = query.value(0)
            return x

        def fset(self, value):
            value = int(value)
            statement = f"""
            UPDATE tasks SET last_checked={value} 
            WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            return
        return locals()
    last_checked = property(**__last_checked())
    del __last_checked

    @property
    def activity(self):

        # TODO: how the hell can activity_id be ""?
        statement = f"""
        SELECT name FROM activities WHERE activity_id={ID if (ID := self.activity_id) != "" else "NULL"};
        """
        if not query.exec_(statement):
            logger.warning("SQL failed", statement)
            logger.warning(query.lastError().text())
            res = ""
        if query.next():
            res = query.value(0)
        else:
            res = ""
        return res

    @property
    def secondary_activity(self):
        statement = f"""
        SELECT name FROM activities WHERE activity_id={self.secondary_activity_id};
        """
        if not query.exec_(statement):
            logger.warning("SQL failed", statement)
            logger.warning(query.lastError().text())
        if query.next():
            res = query.value(0)
        else:
            res = ""
        return res

    @property
    def space(self):
        statement = f"""
        SELECT name FROM spaces WHERE space_id={self.space_id};
        """
        if not query.exec_(statement):
            logger.warning("SQL failed", statement)
            logger.warning(query.lastError().text())
            res = ""
        query.next()
        res = query.value(0)
        return res

    @property
    def level(self):
        statement = f"""
        SELECT name FROM levels WHERE level_id={self.level_id};
        """
        if not query.exec_(statement):
            logger.warning("SQL failed", statement)
            logger.warning(query.lastError().text())
            res = ""
        query.next()
        res = query.value(0)
        return res

    def __time_spent():
        def fget(self):
            statement = f"""
            SELECT time_spent FROM tasks WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            query.first()
            x = query.value(0)
            return x

        def fset(self, value):
            value = int(value)
            statement = f"""
            UPDATE tasks SET time_spent={value} 
            WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            return
        return locals()
    time_spent = property(**__time_spent())
    del __time_spent

    def __done():
        def fget(self):
            statement = f"""
            SELECT done FROM tasks WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            query.first()
            x = query.value(0)
            return x

        def fset(self, value):
            statement = f"""
            UPDATE tasks SET done={value} 
            WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            return
        return locals()
    done = property(**__done())
    del __done

    @property
    def requires(self):
        statement = f"""
        SELECT required_task FROM task_requires_task WHERE task_of_concern={self.id}
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
        return [construct_task_by_id(row(0)) for row in iter_over(query)]

    @property
    def required_by(self):
        statement = f"""
        SELECT task_of_concern FROM task_requires_task WHERE required_task={self.id}
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
        return [construct_task_by_id(row(0)) for row in iter_over(query)]

    def __adjust_time_spent():
        def fget(self):
            statement = f"""
            SELECT adjust_time_spent FROM tasks WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            query.first()
            x = query.value(0)
            return x

        def fset(self, value):
            statement = f"""
            UPDATE tasks SET adjust_time_spent={value} 
            WHERE id={self.id}
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            return
        return locals()
    adjust_time_spent = property(**__adjust_time_spent())
    del __adjust_time_spent

    @property
    def considered_open(self):
        if self.deleted or self.draft or self.inactive:
            return False

        return (not any(t.considered_open for t in self.requires) 
                and not self.done)
    
    @property
    def last_finished(self):
        statement = f"""
        SELECT stop
        FROM sessions
        WHERE task_id == {self.id} AND finished == TRUE
        ORDER BY
            stop DESC
        ;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())

        if query.next():
            return query.value(0)
        else:
            return  0

    @property
    def groups(self):
        return [p for p in split(t.do) if p.startswith("#")]

    def __eq__(self, other):
        return self.id == other.id

def construct_task_by_id(task_id):
    statement = f"""
    SELECT id, do, notes, url, attachments, space_id, draft, inactive, deleted, 
    workload, activity_id, difficulty,
    fear, embarassment, conditions, secondary_activity_id
    FROM tasks WHERE id={task_id};
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement)
        logger.warning(query.lastError().text())
    query.next()
    return Task(*[query.value(index) 
            for index in range(query.record().count())])

def write_session(task_id, start, stop, finished):
    statement = f"""
        INSERT INTO sessions (task_id, start, stop, finished)
        VALUES ('{task_id}', {int(start)}, {int(stop)}, {finished})
        """

    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement)
        logger.warning(query.lastError().text())


def iter_over(query):
    while query.next():
        yield query.value

class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        @self.about.triggered.connect
        def _():
            webbrowser.open("https://github.com/amogorkon/watnu/blob/main/README.md")

        @self.button7.clicked.connect
        def _():
            pass

        @self.button8.clicked.connect
        def _():
            pass

        @self.button9.clicked.connect
        def _():
            """Community."""
            webbrowser.open("https://watnu.slack.com/archives/C01HKH7R4AC")

        @self.button4.clicked.connect
        def _():
            """Task List."""
            win_list.show()
            win_list.exec_()

        @self.button5.clicked.connect
        def _():
            """Watnu?!"""
            if win_what.lets_check_whats_next():
                win_what.show()

        @self.button6.clicked.connect
        def foo():
            """Add new Task."""
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText(
"Es wird schon ein Task bearbeitet."
                )
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return
            win = New_Task()
            win.activateWindow()
            win.show()
     
        @self.button1.clicked.connect
        def _():
            Statistics()

        @self.button2.clicked.connect
        def _():
            pass

        @self.button3.clicked.connect
        def _():
            pass

        @self.actionSupportMe.triggered.connect
        def _():
            webbrowser.open("paypal.me/amogorkon")

        @self.actionIssue_Tracker.triggered.connect
        def _():
            webbrowser.open("https://github.com/users/amogorkon/projects/1")

        @self.actionContact.triggered.connect
        def _():
            webbrowser.open("https://twitter.com/amogorkon")


        @self.actionSettings.triggered.connect
        def _():
            win_settings.show()
            win_settings.exec_()

        @self.actionExport.triggered.connect
        def actionExport():
            raise NotImplementedError
            with open("f{space}.stay", "w") as f:
                tasks
                f.write(dumps(tasks))

        @self.actionImport.triggered.connect
        def actionImport():
            state.flux_to(S.editing)
            win = QtWidgets.QDialog()
            options = QtWidgets.QFileDialog.Options()
            # options |= QtWidgets.QFileDialog.DontUseNativeDialog
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
                            logger.warning(
                                f"Tried to load a task with nothing to 'do': {d.items()}."
                            )
                            continue

                        statement = f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{d["space"]}')
"""
                        if query.exec_(statement):
                            print("OK", statement)
                        else:
                            logger.warning("SQL failed:" + statement)
                            logger.warning(query.lastError().text())
                        
                        statement = f"""
INSERT INTO tasks (do, space_id, done)
VALUES ('{d["do"]}',
(SELECT space_id from spaces WHERE name='{d["space"]}'),
{int(bool(d["done"]))} 
)
"""
                        if query.exec_(statement):
                            print("OK", statement)
                        else:
                            logger.warning("SQL failed:" + statement)
                            logger.warning(query.lastError().text())
            state.flux_to(S.main)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            print(config.count, bin(config.coin))
            config.write()
            state.flux_to(S.final)
            event.accept()
        else:
            event.ignore()


class What_Now(QtWidgets.QDialog, what_now.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.priority_task = None
        self.timing_task = None
        self.balanced_task = None
        self.taskfont = self.task_desc_priority.property("font")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |Qt.CustomizeWindowHint )
        self.timer = QTimer()
        self.timer.start(1000)
        self.cancel.setShortcut(_translate("Dialog", "0"))

        
        self.balanced_tasks = None
        self.priority_tasks = None
        self.timing_tasks = None

        @self.timer.timeout.connect
        def _():
            if not self.timing_task:
                return

            diff = self.timing_task.deadline - time()
            rst, weeks = modf(diff / (7*24*60*60))
            rst, days = modf(rst*7)
            rst, hours = modf(rst*24)
            rst, minutes = modf(rst*60)
            rst, seconds = modf(rst*60)
            
            self.deadline_weeks.setProperty("intValue", weeks)
            self.deadline_days.setProperty("intValue", days)
            self.deadline_hours.setProperty("intValue", hours)
            self.deadline_minutes.setProperty("intValue", minutes)
            self.deadline_seconds.setProperty("intValue", seconds)

        @self.go_priority.clicked.connect
        def _():
            self.hide()
            win_running = Running(self.priority_task)
            win_running.exec_()
            self.show()

        @self.skip_priority.clicked.connect
        def _():
            old_task = self.priority_task
            self.priority_tasks.rotate(-1)
            self.priority_task.last_checked = time()
            self.priority_task = self.priority_tasks[0]
            self.task_desc_priority.setText(self.priority_task.do)
            self.task_desc_priority.adjustSize()
            self.task_space_priority.setText(self.priority_task.space)
            self.activity_priority.setText(self.priority_task.activity)


            if old_task == self.priority_task:
                mb = QtWidgets.QMessageBox()
                mb.setText(
                    "Sorry, es scheint, es gibt keine andere, ähnlich wichtige Aufgabe im Moment.\nAuf gehts!"
                )
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/fast-forward.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()

        @self.go_balanced.clicked.connect
        def _():
            self.hide()
            win_running = Running(self.balanced_task)


        @self.skip_balanced.clicked.connect
        def _():
            now = time()
            self.balanced_task.last_checked = now
            self.balanced_tasks.rotate(-1)
            self.balanced_task = self.balanced_tasks[0]
            self.task_desc_balanced.setText(self.balanced_task.do)
            self.task_desc_balanced.adjustSize()
            self.task_space_balanced.setText(self.balanced_task.space)
            self.activity_balanced.setText(self.balanced_task.activity)


        @self.go_timing.clicked.connect
        def _():
            self.hide()
            win_running = Running(self.timing_task)
 

        @self.skip_timing.clicked.connect
        def _():
            self.timing_tasks.rotate(-1)
            self.timing_task.last_checked = time()
            self.timing_task = self.timing_tasks[0]
            self.task_desc_timing.setText(self.timing_task.do)
            self.task_space_timing.setText(self.timing_task.space)
            self.activity_timing.setText(self.timing_task.activity)


        @self.cancel.clicked.connect
        def _():
            self.hide()

        @self.done_priority.clicked.connect
        def _():
            Task_Finished(self.priority_task)

        @self.done_balanced.clicked.connect
        def _():
            Task_Finished(self.balanced_task)

        @self.done_timing.clicked.connect
        def _():
            Task_Finished(self.timing_task)

    def lets_check_whats_next(self):
        global config, last_check
        foo = (config.coin^config.lucky_num) * config.count
        seed(foo)
        config.count += 1

        self.timer.start(1000)

        statement = f"""
        SELECT id FROM tasks
        WHERE deleted != TRUE AND draft != TRUE AND inactive != TRUE
        ;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
        
        self.groups = defaultdict(lambda: list())

        X = [row(0) for row in iter_over(query)]
        all_tasks = [construct_task_by_id(x) for x in X]

        for t in all_tasks:
            check_task_conditions(t, now=datetime.now())

        self.tasks = list(filter(lambda t: t.considered_open, all_tasks))

        last_check = time()

        if not self.tasks:
            mb = QtWidgets.QMessageBox()
            mb.setText(
                "Es sind noch keine Aufgaben gestellt aus denen ausgewählt werden könnte."
            )
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()
            self.hide()
            return False

        self.set_priority_task()
        self.set_balanced_task()
        self.set_timing_task()
        return True

    def set_priority_task(self):
        self.priority_tasks = prioritize(self.tasks)
        self.priority_task = self.priority_tasks[0]
        self.task_desc_priority.setText(self.priority_task.do)
        self.task_desc_priority.adjustSize()
        self.task_space_priority.setText(self.priority_task.space)
        self.activity_priority.setText(self.priority_task.activity)

    def set_timing_task(self):
        try:
            self.timing_tasks = schedule(self.tasks)
            self.timing_task = self.timing_tasks[0]
            self.task_desc_timing.setText(self.timing_task.do)
            self.task_space_timing.setText(self.timing_task.space)
            self.activity_timing.setText(self.timing_task.activity)
        except IndexError:
            self.task_desc_timing.setText("nix was präsiert")
            self.taskfont.setItalic(True)
            self.task_desc_timing.setFont(self.taskfont)
            self.timing.setEnabled(False)
            self.timing_task = None
            self.deadline = None
        else:
            self.taskfont.setItalic(False)
            self.task_desc_timing.setFont(self.taskfont)
            self.timing.setEnabled(True)

        self.task_desc_timing.adjustSize()

    def set_balanced_task(self):
        activity_time_spent = defaultdict(lambda: 0)
        statement = f"""
        SELECT
            activity_id,
            adjust_time_spent
        FROM activities;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())

        for row in iter_over(query):
            activity_time_spent[row(0)] = row(1)

        statement = f"""
        SELECT
            activity_id,
            SUM(time_spent)
        FROM
            tasks
        GROUP BY
            activity_id;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())


        for row in iter_over(query):
            activity_time_spent[row(0)] += row(1)

        print(activity_time_spent.items())
        self.balanced_tasks = balance(self.tasks, activity_time_spent)
        
        self.balanced_task = self.balanced_tasks[0]
        self.task_desc_balanced.setText(self.balanced_task.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.balanced_task.space)
        self.activity_balanced.setText(self.balanced_task.activity)
        print(self.balanced_task.activity)

class Task_List(QtWidgets.QDialog, task_list.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task_list.setStyleSheet("alternate-background-color: #bfffbf; background-color: #deffde;");
        header = self.task_list.horizontalHeader()
        self.tasks = []

        toolbar = QtWidgets.QToolBar()
        menu = QtWidgets.QMenu()
        clone_as_is = menu.addAction("genau so", self.clone_as_is)
        clone_as_sub = menu.addAction("als Subtask", self.clone_as_sub)
        clone_as_sup = menu.addAction("als Supertask", self.clone_as_sup)
        self.clone_task.setMenu(menu)

        self.build_task_list()
        self.update()

        @self.toss_coin.clicked.connect
        def _():
            # vonNeumann!
            for i in count():
                # least significant bit of high-res time *should* give enough entropy
                first = (time_ns()// 100) & 1
                second = (time_ns()// 100) & 1
                if first != second:
                    break
            # 'threw 31688 pairs!' - so much for "should"
            print("threw", i, "pairs!")

            # bitshift to the left
            config.coin <<= 1
            # then set the bit - 
            config.coin |= first
            seed((config.coin^config.lucky_num) * config.count)

            x = choice(['Kopf', 'Zahl'])
            if x == "Kopf":
                mb = QtWidgets.QMessageBox()
                mb.setText(f"Du hast Kopf geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-heads.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
            else:
                mb = QtWidgets.QMessageBox()
                mb.setText(f"Du hast Zahl geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-tails.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()

        @self.start_task.clicked.connect
        def _():
            if state() is S.running:
                win_running.show()
                win_running.activateWindow()
                win_running.raise_()
                return

            try:
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return

            task = construct_task_by_id(
                    self.task_list.item(x, 0).data(Qt.UserRole))
            win_running = Running(task)
            win_running.exec_()
            self.show()

        @self.create_task.clicked.connect
        def _():
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return
            
            win = New_Task()
            win.show()

        @self.edit_task.clicked.connect
        def _():
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            try: 
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return
            
            task = construct_task_by_id(
                        self.task_list.item(x,0).data(Qt.UserRole))
            win = New_Task(task)
            win.show()

        @self.status.buttonClicked.connect
        def _():
            self.build_task_list()

        @self.button7.clicked.connect
        def _():
            try:
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            # undelete
            if self.status_deleted.isChecked():
                statement = f"""
    UPDATE tasks
    SET deleted = FALSE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            # delete
            else:
                statement = f"""
    UPDATE tasks
    SET deleted = TRUE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            self.task_list.removeRow(x)
            self.update()

        @self.button2.clicked.connect
        def _():
            try:
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            # undo
            if self.status_done.isChecked():
                statement = f"""
    UPDATE tasks
    SET done = FALSE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            # done
            else:
                statement = f"""
    UPDATE tasks
    SET done = TRUE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            self.task_list.removeRow(x)
            self.update()

        @self.button3.clicked.connect
        def _():
            try:
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            # set active
            if self.status_inactive.isChecked():
                statement = f"""
    UPDATE tasks
    SET inactive = FALSE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            # inactive
            else:
                statement = f"""
    UPDATE tasks
    SET inactive = TRUE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            self.task_list.removeRow(x)
            self.update()

        @self.button1.clicked.connect
        def _():
            try:
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            # set not as draft
            if self.status_draft.isChecked():
                statement = f"""
    UPDATE tasks
    SET draft = FALSE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            # inactive
            else:
                statement = f"""
    UPDATE tasks
    SET draft = TRUE
    WHERE id == {self.task_list.item(x, 0).data(Qt.UserRole)}
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

            self.task_list.removeRow(x)
            self.update()

        @self.field_filter.textChanged.connect
        def _():
            self.arrange_list(filter_tasks(self.tasks, 
                                self.field_filter.text().casefold()))
            self.update()

    def clone_as_is(self):
        if state() is S.editing:
            mb = QtWidgets.QMessageBox()
            mb.setText("Es wird schon ein Task bearbeitet.")
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()
            return

        try: 
            x = self.task_list.selectedItems()[0].row()
        except IndexError:
            return
        
        task = construct_task_by_id(
                    self.task_list.item(x,0).data(Qt.UserRole))
        win = New_Task(task, cloning=True, as_sup=0)
        win.show()

    def clone_as_sub(self):
        if state() is S.editing:
            mb = QtWidgets.QMessageBox()
            mb.setText("Es wird schon ein Task bearbeitet.")
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()
            return

        try: 
            x = self.task_list.selectedItems()[0].row()
        except IndexError:
            return
        
        task = construct_task_by_id(
                    self.task_list.item(x,0).data(Qt.UserRole))
        win = New_Task(task, cloning=True, as_sup=-1)
        win.show()


    def clone_as_sup(self):
        if state() is S.editing:
            mb = QtWidgets.QMessageBox()
            mb.setText("Es wird schon ein Task bearbeitet.")
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()
            return

        try: 
            x = self.task_list.selectedItems()[0].row()
        except IndexError:
            return
        
        task = construct_task_by_id(
                    self.task_list.item(x,0).data(Qt.UserRole))
        win = New_Task(task, cloning=True, as_sup=1)
        win.show()

    def build_task_list(self):
        print("building list")
        if self.status_draft.isChecked():
            self.button1.setText("set ready")
        else:
            self.button1.setText("set as draft")

        if self.status_done.isChecked():
            self.button2.setText("set undone")
        else:
            self.button2.setText("set done")

        if self.status_inactive.isChecked():
            self.button3.setText("set active")
        else:
            self.button3.setText("set inactive")

        if self.status_deleted.isChecked():
            self.button7.setText("undelete")
        else:
            self.button7.setText("delete")

        # ready == NOT ANY of the below
        statement = f"""
        SELECT id FROM tasks 
        WHERE 
        done == {self.status_done.isChecked()} AND
        deleted == {self.status_deleted.isChecked()} AND 
        draft == {self.status_draft.isChecked()} AND
        inactive == {self.status_inactive.isChecked()};
        """
        if query.exec_(statement):
            print("OK", statement)
        else:
            logger.warning("SQL failed:" + statement)
            logger.warning(query.lastError().text())

        # recycling query might be a bad idea afterall..
        idxs = [row(0) for row in iter_over(query)]
        self.tasks  = [construct_task_by_id(x) for x in idxs]
        filter_text = self.field_filter.text().casefold()
        self.arrange_list(filter_tasks(self.tasks, filter_text))
        self.update()

    def arrange_list(self, tasks):
        """Needs to be extra, otherwise filtering would hit the DB repeatedly."""
        print("arranging list", len(tasks), "tasks")
        self.task_list.setSortingEnabled(False)

        ok = QIcon("./extra/feathericons/check.svg")
        nok = QIcon("./extra/feathericons/x.svg")

        for i, t in enumerate(tasks):
            self.task_list.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem(t.do)
            self.task_list.setItem(i, 0, item)
            item.setData(Qt.UserRole, t.id)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item = QtWidgets.QTableWidgetItem(t.url)
            self.task_list.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(t.notes)
            self.task_list.setItem(i, 2, item)
            item = QtWidgets.QTableWidgetItem(str(t.priority))
            self.task_list.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(t.space)
            self.task_list.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(t.level)
            self.task_list.setItem(i, 5, item)
            item = QtWidgets.QTableWidgetItem(t.activity)
            self.task_list.setItem(i, 6, item)
            item = QtWidgets.QTableWidgetItem(
                datetime.fromtimestamp(t.deadline).isoformat() 
                    if not isinf(t.deadline) else
                "---")
            self.task_list.setItem(i, 7, item)
            item = QtWidgets.QTableWidgetItem(str(t.conditions))
            self.task_list.setItem(i, 8, item)
        
        if not tasks:
            self.task_list.clearContents()
            self.task_list.setRowCount(0)
        self.task_list.setSortingEnabled(True)
        self.task_list.resizeColumnsToContents()


class New_Task(QtWidgets.QWizard, task_new.Ui_Wizard):
    def __init__(self, task=None, cloning=False, as_sup=0):
        super().__init__()
        self.activateWindow()
        self.setupUi(self)

        if cloning:
            self.setWindowTitle(_translate("Wizard", "Bearbeite Klon"))
        self.setOption(QtWidgets.QWizard.HaveFinishButtonOnEarlyPages, True)
        self.task = task
        self.cloning = cloning
        self.as_sup = as_sup
        if cloning:
            self.dependency.setEnabled(False)
        state.flux_to(S.editing)
        self.page_basics.registerField(
            "task*", self.desc, "plainText", changedSignal=self.desc.textChanged
        )
        model = QSqlTableModel()
        model.setTable("levels")
        model.setSort(0, Qt.DescendingOrder)
        model.select()
        self.level.setModel(model)
        self.level.setModelColumn(1)
        self.level.setCurrentIndex(2)

        model = QSqlTableModel()
        model.setTable("activities")
        model.setSort(0, Qt.DescendingOrder)
        model.select()

        statement = f"""
        SELECT activity_id, name FROM activities;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
            return

        for i, row in enumerate(iter_over(query)):
            self.activity.addItem(row(1), QVariant(row(0)))
            self.secondary_activity.addItem(row(1), QVariant(row(0)))

        model = QSqlTableModel()
        model.setTable("spaces")
        model.setSort(1, Qt.AscendingOrder)
        model.select()
        self.space.setModel(model)
        self.space.setModelColumn(1)

        # a new task - task dependency table contains all possible tasks
        if not self.task:
            statement = f"""
            SELECT id FROM tasks 
            WHERE deleted != TRUE;
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
                return
            idx = list(row(0) for row in iter_over(query))
            tasks = [construct_task_by_id(x) for x in idx]

            for i, t in enumerate(tasks):
                self.task_dependency_table.setRowCount(i+1)
                item = QtWidgets.QTableWidgetItem(t.do)
                self.task_dependency_table.setItem(i, 0, item)
                item.setData(Qt.UserRole, t.id)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item = QtWidgets.QTableWidgetItem(t.space)
                self.task_dependency_table.setItem(i, 1, item)
                item = QtWidgets.QTableWidgetItem(t.level)
                self.task_dependency_table.setItem(i, 2, item)
                item = QtWidgets.QTableWidgetItem(t.activity)
                self.task_dependency_table.setItem(i, 3, item)
                item = QtWidgets.QTableWidgetItem(
                    datetime.fromtimestamp(t.deadline).isoformat() 
                    if not isinf(t.deadline) else
                "---")
                self.task_dependency_table.setItem(i, 4, item)

        # editing a task - need to set all values accordingly
        else:
            self.desc.document().setPlainText(task.do)
            self.url.setText(self.task.url)
            self.notes.document().setPlainText(task.notes)
            self.space.setCurrentIndex(self.space.findText(self.task.space))
            self.level.setCurrentIndex(self.level.findText(self.task.level))
            self.activity.setCurrentIndex(self.activity.findText(self.task.activity))
            print(self.task.secondary_activity, self.task.secondary_activity_id, type(self.task.secondary_activity_id))
            self.secondary_activity.setCurrentIndex(self.secondary_activity.findText(self.task.secondary_activity))
            self.is_depending_on.click()
            if not isinf(self.task.deadline):
                self.deadline.setEnabled(True)
                self.deadline_active.setChecked(True)
                dt = QDateTime.fromSecsSinceEpoch(int(self.task.deadline))
                self.deadline.setDate(dt.date())
                self.deadline.setTime(dt.time())

            statement = f"""
            SELECT id FROM tasks 
            WHERE deleted != TRUE AND id != {self.task.id};
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
                return
            idx = list(row(0) for row in iter_over(query))
            tasks = [construct_task_by_id(x) for x in idx]
            tasks = filter(lambda t: self.task.id in [t.id for t in t.requires], tasks)
            # TODO: hmm.. is that right?

            for i, t in enumerate(tasks):
                self.task_dependency_table.setRowCount(i+1)
                item = QtWidgets.QTableWidgetItem(t.do)
                self.task_dependency_table.setItem(i, 0, item)
                item.setData(Qt.UserRole, t.id)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item = QtWidgets.QTableWidgetItem(t.space)
                self.task_dependency_table.setItem(i, 1, item)
                item = QtWidgets.QTableWidgetItem(t.level)
                self.task_dependency_table.setItem(i, 2, item)
                item = QtWidgets.QTableWidgetItem(t.activity)
                self.task_dependency_table.setItem(i, 3, item)
                item = QtWidgets.QTableWidgetItem(
                    datetime.fromtimestamp(t.deadline).isoformat() 
                    if not isinstance(t.deadline, str) else
                "---")
                self.task_dependency_table.setItem(i, 4, item)


        @self.deadline_active.stateChanged.connect
        def _():
            if self.deadline_active.isChecked():
                self.deadline.setEnabled(True)
            else:
                self.deadline.setEnabled(False)


    def accept(self):
        super().accept()

        do = self.desc.toPlainText()
        if self.deadline_active.isChecked():
            deadline = self.deadline.dateTime().toSecsSinceEpoch()
        else:
            deadline = "Infinity"

        priority = self.priority.value()
        space_id = self.space.model().data(self.space.model().index(self.space.currentIndex(), 0))
        activity_id = x if (x:=self.activity.currentData()) is not None else 'NULL'
        secondary_activity_id = x if (x:=self.secondary_activity.currentData()) is not None else 'NULL'
        level_id = self.level.model().data(self.level.model().index(self.level.currentIndex(), 0))
        url = self.url.text()

        # it really is a new task
        if not self.task or self.cloning:
            statement = f"""
INSERT INTO tasks 
(do, 
space_id, 
deadline, 
activity_id,
secondary_activity_id,
url
)

VALUES 
('{do}', 
{space_id},
'{deadline}',
{activity_id},
{secondary_activity_id},
'{url}'
);
"""
            if query.exec_(statement):
                print("OK", statement)
                win_main.statusBar.showMessage("Neuen Task erstellt.", 3000)
            else:
                logger.warning("SQL failed:" + statement)
                logger.warning(query.lastError().text())                
        
            new_task_id = query.lastInsertId()
            
            task_ids = [self.task_dependency_table.item(x.row(), 0).data(Qt.UserRole) 
                            for x in self.task_dependency_table.selectionModel().selectedRows(0)]
                
            for idx in task_ids:
                task_of_concern = new_task_id
                required_task = idx

                if self.is_subtask_of.isChecked():
                    task_of_concern, required_task = required_task, task_of_concern
                statement = f"""
INSERT OR IGNORE INTO task_requires_task
    (task_of_concern, required_task)
    VALUES (
    {task_of_concern}, {required_task}
    );
"""
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())                

            # as-is -> 0, as-sub -> -1 as-sup -> 1
            if self.as_sup == -1:
                #subtask
                task_of_concern, required_task = self.task.id, new_task_id                
                print("subtask", task_of_concern, required_task)

            if self.as_sup == 1:
                task_of_concern, required_task = new_task_id, self.task.id
                print("supertask", task_of_concern, required_task)

            if self.as_sup:
                statement = f"""
    INSERT OR IGNORE INTO task_requires_task
        (task_of_concern, required_task)
        VALUES (
        {task_of_concern}, {required_task}
        );
    """
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())                

        # we're editing a task
        else:
            statement = f"""
UPDATE tasks 
SET do = '{do}',
    priority = {priority},
    level_id = {level_id},
    deadline = '{deadline}',
    activity_id = {activity_id},
    secondary_activity_id = {secondary_activity_id},
    space_id = {space_id},
    url = '{url}'
WHERE id={self.task.id}
"""
            if query.exec_(statement):
                print("OK", statement)
                win_main.statusBar.showMessage("Aufgabe aktualisiert.", 10000)
            else:
                logger.warning("SQL failed:" + statement)
                logger.warning(query.lastError().text())
        
            # need to clean up first

            statement = f"""
DELETE FROM task_requires_task WHERE task_of_concern == {self.task.id}
"""
            if query.exec_(statement):
                print("OK", statement)
            else:
                logger.warning("SQL failed:" + statement)
                logger.warning(query.lastError().text())

            # now, enter fresh

            task_ids = [self.task_dependency_table.item(x.row(), 0).data(Qt.UserRole) 
                        for x in self.task_dependency_table.selectionModel().selectedRows(0)]
            
            for idx in task_ids:
                statement = f"""
INSERT OR IGNORE INTO task_requires_task
    (task_of_concern, required_task)
    VALUES (
    {self.task.id}, {idx}
    );
"""
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())    


        win_list.build_task_list()
        state.flux_to(S.main)

    def reject(self):
        super().reject()
        state.flux_to(S.main)

class Running(QtWidgets.QDialog, running_task.Ui_Dialog):
    def __init__(self, task):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |Qt.CustomizeWindowHint )
        win_main.hide()
        if win_new:
            win_new.hide()
        win_settings.hide()

        self.task = task
        self.start_time = time()
        self.task.last_checked = self.start_time
        self.timer = QTimer()
        self.player = QMediaPlayer()

        url = QUrl.fromLocalFile(r"./extra/kuckuck alarm einmal.wav")
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(70)
        self.player.play()

        self.ticks = 0  # time tracked in this session
        self.time_spent = 0  # the time previously tracked by machine
        self.adjust_time_spent = 0  # user estimates time spent with this task untracked 
        self.time_spent = self.task.time_spent

        self.adjust_time_spent = self.task.adjust_time_spent
        state.flux_to(S.running)
        self.pomodoro = -35 *60
        doc = QtGui.QTextDocument(task.notes)
        self.notes.setDocument(doc)

        doc = QtGui.QTextDocument(task.do)
        self.desc.setDocument(doc)

        progress.show()
        if self.task.url:
            self.visit_url.setEnabled(True)
            self.visit_url.setText(str(self.task.url))   

        url = QUrl.fromLocalFile(r"./extra/kuckuck (1).wav")
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(config.tictoc_volume)
        self.player.play()

        self.task_space.setText(task.space)

        activity_color = {0: config.activity_color_body,
                        1: config.activity_color_mind,
                        2: config.activity_color_spirit,
                        }

        self.frame.setStyleSheet(f"""
* {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
        stop:0 black, 
        stop:1 white);
background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
        stop:0 {activity_color.get(self.task.activity_id, "black")},
        stop:0.5 {activity_color.get(self.task.secondary_activity_id, 
                  activity_color.get(self.task.activity_id, "black"))},
        stop:1 white);
}}
""")
        self.show()
        self.start_task()
        self.timer.start(1000)



        @self.visit_url.clicked.connect
        def _():
            webbrowser.open(self.task.url)

        @self.notes.document().contentsChanged.connect
        def _():
            statement = f"""
            UPDATE tasks SET notes= :notes 
            WHERE id=:id
            """
            query.prepare(statement)
            query.bindValue(":notes", self.notes.document().toMarkdown())
            query.bindValue(":id", task.id)
            if not query.exec_():
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
            return

        @self.timer.timeout.connect
        # timeout happens every 1 sec
        def _():
            self.ticks += 1
            self.pomodoro += 1

            total = (x if 
                (x:=(self.time_spent + self.adjust_time_spent + self.ticks)) > 0
                    else 0)
            
            rst, days = modf(total / (24*60*60))
            rst, hours = modf(rst*24)
            rst, minutes = modf(rst*60)
            seconds = rst * 60
            self.LCD_days.setProperty("intValue", days)
            self.LCD_hours.setProperty("intValue", hours)
            self.LCD_minutes.setProperty("intValue", minutes)
            self.LCD_seconds.setProperty("intValue", seconds)

            if self.pomodoro < 0:
                pomodoro_percent = int((1 - (-self.pomodoro / (35*60)))*100)
                self.pomodoro_bar.setProperty("value", pomodoro_percent)
                progress.setValue(pomodoro_percent)

            if self.pomodoro == 0:
                tell_telegram("pomodoro done! pause!", config)
                url = QUrl.fromLocalFile(r"./extra/kuckuck alarm zweimal.wav")
                self.player.setMedia(QMediaContent(url))
                self.player.setVolume(70)
                self.player.play()
                progress.setValue(0)
                self.pause = True
                self.pomodoro_bar.reset()

            if 0 < self.pomodoro <= 5 * 60:
                pass

            if self.pomodoro > 5 * 60:
                self.pomodoro = - 35 * 60
                tell_telegram(f"Pause vorbei! Weiter gehts mit: {self.task.do}", config)
                url = QUrl.fromLocalFile(r"./extra/kuckuck alarm einmal.wav")
                self.player.setMedia(QMediaContent(url))
                self.player.setVolume(70)
                self.player.play()

        @self.plus5.clicked.connect
        def _():
            self.adjust_time_spent += 5 * 60

        @self.minus5.clicked.connect
        def _():
            if (self.adjust_time_spent + self.time_spent + self.ticks) >= 5*60:
                self.adjust_time_spent -= 5 * 60

        @self.done_for_now.clicked.connect
        def _():
            stop_time = time()
            self.player.stop()
            if self.timer.isActive():
                self.timer.stop()
            self.task.last_checked = stop_time
            self.task.time_spent = self.time_spent + self.ticks
            self.task.adjust_time_spent = self.adjust_time_spent
            self.hide()
            write_session(self.task.id, self.start_time,
                    stop_time, True)
            win_main.show()
            if not win_list.isHidden():
                win_list.raise_()
            if not win_what.isHidden() and win_what:
                win_what.raise_()

            progress.setValue(0)
            
            state.flux_to(S.main)

        @self.finished.clicked.connect
        def _():
            if (timer_was_running := self.timer.isActive()):
                self.timer.stop()
                self.player.pause()
            if not Task_Finished(self.task, ticks=self.ticks, start=self.start_time).result():
                if timer_was_running:
                    self.timer.start()
                    self.player.play()
                return
            self.hide()

            win_main.show()
            if not win_list.isHidden():
                win_list.raise_()
            if not win_what.isHidden() and win_what:
                win_what.raise_()
            
            progress.setValue(0)
            state.flux_to(S.main)

        @self.reset.clicked.connect
        def _():
            self.start_time = time()
            self.time_spent = self.task.time_spent
            self.adjust_time_spent = self.task.adjust_time_spent
            self.ticks = 0

        @self.pause.clicked.connect
        def _():
            if self.timer.isActive():
                stop_time = time()
                write_session(self.task.id, self.start_time,
                    stop_time, False)
                progress.pause()
                self.timer.stop()
                self.player.stop()
                self.task.last_checked = time()
                self.ticks += stop_time - self.start_time
            else:
                progress.resume()
                self.player.play()
                self.timer.start(1000)
                self.start_time = time()

        @self.clock_audio.clicked.connect
        def _():
            if self.player.state() == 1:
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(
                    ":/feather/extra/feathericons/volume-2.svg"), 
                    QtGui.QIcon.Normal, 
                    QtGui.QIcon.Off)
                self.clock_audio.setIcon(icon)
                self.player.pause()
            else:
                self.player.play()
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(
                    ":/feather/extra/feathericons/volume-x.svg"), 
                    QtGui.QIcon.Normal, 
                    QtGui.QIcon.Off)
                self.clock_audio.setIcon(icon)

    def cancel(self):
        """Hard cancel - no button for this, just Esc"""
        self.timer.stop()
        self.player.stop()
        self.ticks = 0
        self.task.last_checked = time()
        self.task = None
        self.hide()
        
        win_main.show()
        if not win_list.isHidden():
            win_list.raise_()
        if not win_what.isHidden():
            win_what.raise_()
        state.flux_to(S.main)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.cancel()
        event.accept()

    def start_task(self):
        # check if working conditions are optimal once a day
        statement = f"""
        SELECT start 
        FROM sessions
        ORDER BY start DESC;
        """
        
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())

        if not query.next():
            last_started = 0
        else:
            last_started = query.value(0)

        now = datetime.now()
        then = datetime.fromtimestamp(last_started)

        if not now.date() == then.date():
            mb = QtWidgets.QMessageBox()
            mb.setText("""
Checkliste für optimale Produktivität:
- Raumtemperatur bei 21°C?
- Ausleuchtung bei 1000 Lux?
- Relative Luftfeuchtigkeit bei ~50%?
- Kaffee/Tee & genug Wasser zur Hand?
- Ausgeruht? Geist fokusiert?
- Körper in Schwung?
- Das Richtige auf den Ohren?
"""
            )
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()

        td = now - then

        if td.days == 0 and (60*25 <= td.seconds <= 60*120) or True:
            mb = QtWidgets.QMessageBox()
            mb.setText("""
Gesundheitshinweis:
Alle ~25 Minuten kurz Stoßlüften & einen Schluck Wasser trinken :)
"""
)
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()


class Task_Finished(QtWidgets.QDialog, task_finished.Ui_Dialog):
    def __init__(self, task, ticks=0, start=None):
        super().__init__()
        self.setupUi(self)

        self.task = task
        self.start = time() if not start else start

        self.task_desc.setText(task.do)
        total = task.time_spent + task.adjust_time_spent + ticks
        rst, hours = modf(total/(60*60))
        rst, minutes = modf(rst*60)
        self.hours.setValue(int(hours))
        self.minutes.setValue(int(minutes))
        self.exec_()

    def accept(self):
        super().accept()
        total = self.hours.value() * 60*60 + self.minutes.value() * 60

        statement = f"""
    UPDATE tasks 
    SET adjust_time_spent = {total - self.task.time_spent},     
        done=TRUE
    WHERE id={self.task.id};
    """
        if query.exec_(statement):
            print("OK", statement)
            win_main.statusBar.showMessage("Aufgabe erledigt.", 10000)
        else:
            logger.warning("SQL failed:" + statement)
            logger.warning(query.lastError().text())


        write_session(self.task.id, self.start, time(), True)
        win_list.build_task_list()
        win_what.lets_check_whats_next()
        return True

    def reject(self):
        super().reject()
        return False

class Settings(QtWidgets.QDialog, settings.Ui_Dialog):
    def __init__(self):
        super().__init__() 
        self.setupUi(self) 
        
        self.build_spaces_table()
        
        self.skills_table.horizontalHeader().setVisible(True)
        self.skills_table.setColumnHidden(0, True)
        self.skills_table.sortByColumn(1, Qt.AscendingOrder)
        self.build_skill_table()

        @self.create_skill.clicked.connect
        def _():
            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                    "Neue Aktivität",
                    "Name der neuen Aktivität", QtWidgets.QLineEdit.Normal, "")
            if okPressed and text != '':
                statement = f"""
INSERT OR IGNORE INTO activities (name)
VALUES ('{text}')
"""
                if query.exec_(statement):
                    print("OK", statement)
                    self.build_skill_table()
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

        @self.rename_skill.clicked.connect
        def _():
            try:
                x = self.activities_table.selectedItems()[0].row()
            except IndexError:
                return
            
            skill_id = self.activities_table.item(x, 1).data(Qt.UserRole)
            name = self.activities_table.item(x, 1).text()

            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                "Aktivität umbenennen",
                f"Wie soll die Aktivität '{name}' umbenannt werden?", 
                QtWidgets.QLineEdit.Normal, "")

            if okPressed and text != '':
                statement = f"""
UPDATE activities 
SET name = '{text}'
WHERE skill_id == {skill_id};
"""
                if query.exec_(statement):
                    print("OK", statement)
                    self.build_skill_table()
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

        @self.clear_all_deleted.clicked.connect
        def _():
            statement = f"""
DELETE FROM tasks WHERE deleted == TRUE;
"""
            if query.exec_(statement):
                print("OK", statement)
            else:
                logger.warning("SQL failed:" + statement)
                logger.warning(query.lastError().text())

        @self.delete_skill.clicked.connect
        def _():
            try:
                x = self.activities_table.selectedItems()[0].row()
            except IndexError:
                return

            skill_id = self.activities_table.item(x, 1).data(Qt.UserRole)
            name = self.activities_table.item(x, 1).text()

            mb = QMessageBox()
            mb.setText(f"Wirklich Aktivität '{name}' löschen?")
            mb.setInformativeText("Bitte bestätigen!")
            mb.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            mb.setDefaultButton(QMessageBox.No)

            if mb.exec_() == QMessageBox.Yes:
                statement = f"""
DELETE FROM activities WHERE skill_id == {skill_id};
"""
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())
                self.activities_table.removeRow(x)
                self.update()

        @self.rename_space.clicked.connect
        def _():
            try:
                x = self.spaces_table.selectedItems()[0].row()
            except IndexError:
                return
        
            space_id = self.spaces_table.item(x, 0).data(Qt.UserRole)
            name = self.spaces_table.item(x, 0).text()

            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                "Space umbenennen",
                f"Wie soll der Space '{name}' umbenannt werden?", 
                QtWidgets.QLineEdit.Normal, "")

            if okPressed and text != '':
                statement = f"""
UPDATE spaces 
SET name = '{text}'
WHERE space_id == {space_id};
"""
                if query.exec_(statement):
                    print("OK", statement)
                    self.build_spaces_table()
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

        @self.create_space.clicked.connect
        def _():
            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                    "Neuer Space",
                    "Name des neuen Space", QtWidgets.QLineEdit.Normal, "")
            if okPressed and text != '':
                statement = f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                if query.exec_(statement):
                    print("OK", statement)
                    self.build_spaces_table()
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

        @self.delete_space.clicked.connect
        def _():
            try:
                x = self.spaces_table.selectedItems()[0].row()
            except IndexError:
                return
            
            space_id = self.spaces_table.item(x, 0).data(Qt.UserRole)
            name = self.spaces_table.item(x, 0).text()

            mb = QMessageBox()
            mb.setText(f"Wirklich Space '{name}' löschen?")
            mb.setInformativeText("Bitte bestätigen!")
            mb.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            mb.setDefaultButton(QMessageBox.No)

            if mb.exec_() == QMessageBox.Yes:
                statement = f"""
DELETE FROM spaces WHERE space_id == {space_id};
"""
                if query.exec_(statement):
                    print("OK", statement)
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())
                self.spaces_table.removeRow(x)
                self.update()


    def build_skill_table(self):
        statement = f"""
        SELECT skill_id, name FROM skills;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
            return

        self.skills_table.setSortingEnabled(False)

        for i, row in enumerate(iter_over(query)):
            self.activities_table.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem()
            self.skills_table.setItem(i, 1, item)
            item.setText(row(1))
            # skill_id
            item.setData(Qt.UserRole, row(0))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.skills_table.setSortingEnabled(True)
        self.update()


    def build_spaces_table(self):
        statement = f"""
        SELECT space_id, name, priority FROM spaces;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
            return

        self.spaces_table.setSortingEnabled(False)

        for i, row in enumerate(iter_over(query)):
            self.spaces_table.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem(row(1))
            self.spaces_table.setItem(i, 0, item)
            item.setData(Qt.UserRole, row(0))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item = QtWidgets.QTableWidgetItem(str(row(2)))
            self.spaces_table.setItem(i, 1, item)

        for i in range(self.spaces_table.rowCount()):
            space_id = self.spaces_table.item(i, 0).data(Qt.UserRole)
            statement = f"""
SELECT COUNT(*) FROM tasks WHERE space_id == {space_id};
"""
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())
                return
            text = "0" if not query.next() else str(query.value(0))
            item = QtWidgets.QTableWidgetItem(text)
            self.spaces_table.setItem(i, 2, item)


        self.spaces_table.setSortingEnabled(True)
        self.update()


class Statistics(QtWidgets.QDialog, statistics.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        statement = f"""
SELECT
    activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    activity_id;
"""
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())

        activities = {row(0): row(1) for row in iter_over(query)}
        print(activities.items())

        statement = f"""
SELECT
    activity_id, name, adjust_time_spent
FROM
    activities
"""
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())

        for row in iter_over(query):
            activities[row(0)] += row(2)
            print(row(1), activities[row(0)])


def change_global_font(qobject, event):
    if event.type() == Qt.QEvent.Wheel:
        font = app.font()
        font.setPointSize(font.pointSize() + 1)
        app.setFont(font)

        # if QtGui.QApplication.keyboardModifiers() == Qt.ControlModifier:
        #     font = app.font()
        #     font.setPointSize(font.pointSize() + 1)
        #     app.setFont(font)

if __name__ == "__main__":
    path = Path(sys.argv[0])
    try:
        # overwriting the module with the instance for convenience
       config = config.read("config.stay")
    except FileNotFoundError:
        p1 = path.parents[0] / "default-config.stay"
        p2 = path.parents[0] / "config.stay"

        from shutil import copyfileobj
        with open(p1, "r") as f1, open(p2, "w+") as f2:
           copyfileobj(f1, f2)
        config = config.read(p2)

    seed((config.coin^config.lucky_num) * config.count)
    last_check = config.time_program_quit_last

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(config.database)
    query = QSqlQuery()

    if not db.open():
        logger.critical("Could not open DB!")

    if config.first_start:
        import first_start
        first_start.run(db, query, config, logger)
        config.first_start = False
        config.write()

    app = QtWidgets.QApplication(sys.argv) 
    win_main = MainWindow()
    win_main.statusBar.show()
    win_main.statusBar.showMessage("Willkommen zurück! Lass uns was schaffen!", 10000)
    win_list = Task_List()
    win_what = What_Now()
    win_what.lets_check_whats_next()
    win_new = None
    win_settings = Settings()
    win_running = None


    state = StateMachine(initial=S.init, name="Application State",
        states={S.init:{S.main},
                S.main:{S.final, S.running, S.editing},
                S.running: {S.main},
                S.editing: {S.main, S.final, S.editing}},
                
        enters={S.final:app.quit}
        )

    state.flux_to(S.main)

    if not db.tables():
        logger.critical("Empty DB - config.first_start has now been set to True, please restart!")
        config.first_start = True
        config.write()
        state.flux_to(S.final)
        sys.exit()

    win_main.show()
    button = QWinTaskbarButton()
    button.setWindow(win_main.windowHandle())
    button.setOverlayIcon(QIcon("./extra/feathericons/aperture.svg"))
    progress = button.progress()
    progress.setRange(0,100)

    sys.exit(app.exec_())