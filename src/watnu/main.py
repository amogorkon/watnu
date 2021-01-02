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
from math import modf
from pathlib import Path
from pprint import pprint
from random import choice
from random import randint
from random import random
from random import seed
from time import time
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


from ui import import_tasks
from ui import main_window
from ui import running_task
from ui import settings
from ui import statistics
from ui import task_list
from ui import task_new
from ui import what_now

from algo import balance
from algo import check_task_conditions
from algo import prioritize
from algo import schedule
from lib.fluxx import StateMachine
from lib.stay import Decoder

import config

from pathlib import Path

__version__ = (0, 0, 7)



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
    active: bool=True
    deleted: bool=False

    priority: float = 0
    level_id: int = 0

    deadline: float="inf"
    workload: int=None

    activity_id: int=None
    difficulty: float=5
    fear: float=5
    embarassment: float=5

    requires: str=""
    conditions: str=""

    @property
    def total_priority(self):
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
                space_priority = x if (x := query.value(0)) is not None else 0
        else:
            space_priority = 0
        return self.priority + space_priority

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
        statement = f"""
        SELECT name FROM activities WHERE activity_id={self.activity_id};
        """
        if not self.activity_id:
            return ""
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

def construct_task_by_id(task_id):
    statement = f"""
    SELECT id, do, notes, url, attachments, space_id, draft, active, deleted, 
    priority, level_id, deadline, workload, activity_id, difficulty,
    fear, embarassment, requires, conditions
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
        yield query

class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        @self.pushButton_11.clicked.connect
        def _():
            pass

        @self.pushButton_12.clicked.connect
        def _():
            pass

        @self.pushButton_13.clicked.connect
        def _():
            """Community."""
            webbrowser.open("https://watnu.slack.com/archives/C01HKH7R4AC")

        @self.pushButton_21.clicked.connect
        def _():
            """Task List."""
            win_list.show()
            win_list.exec_()

        @self.pushButton_22.clicked.connect
        def _():
            """Watnu?!"""
            if win_what.lets_check_whats_next():
                win_what.show()

        @self.pushButton_23.clicked.connect
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
     
        @self.pushButton_31.clicked.connect
        def _():
            pass

        @self.pushButton_32.clicked.connect
        def _():
            pass

        @self.pushButton_33.clicked.connect
        def _():
            pass

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
            win_running.start_task(self.priority_task)
            win_running.exec_()
            self.show()

        @self.skip_priority.clicked.connect
        def _():
            old_task = self.priority_task
            self.priority_tasks.rotate(-1)
            self.priority_task.last_checked = time()
            self.priority_task = self.priority_tasks[0]

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
            win_running.start_task(self.balanced_task)
            self.hide()

        @self.skip_balanced.clicked.connect
        def _():
            now = time()
            self.balanced_task.last_checked = now
            self.balanced_tasks.rotate(-1)
            self.balanced_task = self.balanced_tasks[0]
            self.task_desc_balanced.setText(self.balanced_task.do)
            self.task_desc_balanced.adjustSize()

        @self.go_timing.clicked.connect
        def _():
            win_running.start_task(self.timing_task)
            self.hide()

        @self.skip_timing.clicked.connect
        def _():
            self.timing_tasks.rotate(-1)
            self.timing_task.last_checked = time()
            self.timing_task = self.timing_tasks[0]
            self.task_desc_timing.setText(self.timing_task.do)
            
        @self.cancel.clicked.connect
        def _():
            self.hide()

    def lets_check_whats_next(self):
        global config, last_check
        foo = (config.coin^config.lucky_num) * config.count
        seed(foo)
        config.count += 1

        self.timer.start(1000)

        statement = f"""
        SELECT id, do, notes, url, attachments, space_id, 
            draft, active, deleted, 
            priority, level_id, 
            deadline, workload, 
            activity_id, difficulty,
            fear, embarassment, requires, conditions
        FROM tasks
        WHERE deleted != TRUE AND draft != TRUE
        ;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
        
        self.tasks = []
        self.groups = defaultdict(lambda: list())

        all_tasks = []

        for row in iter_over(query):
            t = Task(*[row.value(index) 
                        for index in range(query.record().count())])
            #must be done in two loops because t.done reuses query
            all_tasks.append(t)

        for t in all_tasks:
            statement = f"""
            SELECT stop
            FROM sessions
            WHERE task_id == {t.id} AND finished == TRUE
            ORDER BY
                stop DESC
            ;
            """
            if not query.exec_(statement):
                logger.warning("SQL failed:\n" + statement)
                logger.warning(query.lastError().text())

            if query.next():
                last_finished = query.value(0)
            else:
                last_finished = 0

            # TODO: t.active
            t.done, active = check_task_conditions(
                cond=t.conditions,
                done=t.done, 
                active=t.active,
                last_finished=last_finished,
                now=datetime.now()
                )

            G = [p for p in split(t.do) if p.startswith("#")]
            for g in G:
                self.groups[g].append(t.id)
            if not t.done:
                self.tasks.append(t)

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

    def set_timing_task(self):
        try:
            self.timing_tasks = schedule(self.tasks)
            self.timing_task = self.timing_tasks[0]
            self.task_desc_timing.setText(self.timing_task.do)
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
        FROM
            activities
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())

        for row in iter_over(query):
            activity_time_spent[row.value(0)] = row.value(1)

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
            activity_time_spent[row.value(0)] += row.value(1)

        self.balanced_tasks = balance(self.tasks, activity_time_spent)
        
        self.balanced_task = self.balanced_tasks[0]
        self.task_desc_balanced.setText(self.balanced_task.do)
        self.task_desc_balanced.adjustSize()


class Task_List(QtWidgets.QDialog, task_list.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.build_task_list()
        self.task_list.setStyleSheet("alternate-background-color: #bfffbf; background-color: #deffde;");
        self.task_list.setColumnWidth(0, 200)
        self.task_list.setColumnWidth(3, 50)
        self.task_list.setColumnWidth(4, 50)
        self.task_list.setColumnWidth(5, 50)

        @self.throw_heads.clicked.connect
        def _():
            global config
            # bitshift to the left
            config.coin <<= 1
            # then set the bit
            config.coin |= 1

        @self.throw_tails.clicked.connect
        def _():
            global config
            config.coin <<= 1
            config.coin |= 0

        @self.toss_coin.clicked.connect
        def _():
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
            win_running.start_task(task)
            win_running.exec_()
            self.show()

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

        @self.delete_task.clicked.connect
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


    def build_task_list(self):
        statement = f"""
        SELECT id FROM tasks 
        WHERE deleted != TRUE AND draft != TRUE 
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
            return

        # recycling query might be a bad idea afterall..
        idxs = [x.value(0) for x in iter_over(query)]
        tasks = [construct_task_by_id(x) for x in idxs]
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
            item = QtWidgets.QTableWidgetItem(ok if t.done else nok, "")
            self.task_list.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(ok if t.draft else nok, "")
            self.task_list.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(ok if t.active else nok, "")
            self.task_list.setItem(i, 5, item)
            item = QtWidgets.QTableWidgetItem(str(t.priority))
            self.task_list.setItem(i, 6, item)
            item = QtWidgets.QTableWidgetItem(t.space)
            self.task_list.setItem(i, 7, item)
            item = QtWidgets.QTableWidgetItem(
                datetime.fromtimestamp(t.deadline).isoformat() 
                    if not isinstance(t.deadline, str) else
                "---")
            self.task_list.setItem(i, 8, item)
            item = QtWidgets.QTableWidgetItem(
                    datetime.fromtimestamp(t.last_checked).isoformat())
            self.task_list.setItem(i, 9, item)
            item = QtWidgets.QTableWidgetItem(str(t.time_spent))
            self.task_list.setItem(i, 10, item)

        self.task_list.setSortingEnabled(True)
        self.update()

class New_Task(QtWidgets.QWizard, task_new.Ui_Wizard):
    def __init__(self, task=None):
        super().__init__()
        self.activateWindow()
        self.setupUi(self)
        self.setOption(QtWidgets.QWizard.HaveFinishButtonOnEarlyPages, True)
        self.task = task
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
            self.activity.addItem(row.value(1), QVariant(row.value(0)))

        model = QSqlTableModel()
        model.setTable("spaces")
        model.setSort(1, Qt.AscendingOrder)
        model.select()
        self.space.setModel(model)
        self.space.setModelColumn(1)

        # editing a task - need to set all values accordingly
        if self.task:
            self.desc.document().setPlainText(task.do)
            self.url.setText(self.task.url)
            self.notes.document().setPlainText(task.notes)
            self.space.setCurrentIndex(self.space.findText(self.task.space))
            self.level.setCurrentIndex(self.level.findText(self.task.level))
            self.activity.setCurrentIndex(self.activity.findText(self.task.activity))
            if self.task.deadline != "Infinity":
                self.deadline.setEnabled(True)
                self.deadline_active.setChecked(True)
                dt = QDateTime.fromSecsSinceEpoch(int(self.task.deadline))
                self.deadline.setDate(dt.date())
                self.deadline.setTime(dt.time())


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
        print(29, space_id)
        activity_id = x if (x:=self.activity.currentData()) is not None else 'NULL'
        level_id = self.level.model().data(self.level.model().index(self.level.currentIndex(), 0))

        # it really is a new task
        if not self.task:
            statement = f"""
INSERT INTO tasks 
(do, 
space_id, 
deadline, 
activity_id
)

VALUES 
('{do}', 
{space_id},
'{deadline}',
{activity_id}
)
"""
            if query.exec_(statement):
                print("OK", statement)
                win_main.statusBar.showMessage("Neuen Task erstellt.", 3000)
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
    space_id = {space_id}
WHERE id={self.task.id}
"""
            if query.exec_(statement):
                print("OK", statement)
                win_main.statusBar.showMessage("Aufgabe aktualisiert.", 10000)
            else:
                logger.warning("SQL failed:" + statement)
                logger.warning(query.lastError().text())
        win_list.build_task_list()
        state.flux_to(S.main)

    def reject(self):
        super().reject()
        state.flux_to(S.main)

class Running(QtWidgets.QDialog, running_task.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task = None
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |Qt.CustomizeWindowHint )
        self.timer = QTimer()
        self.ticks = 0
        self.player = QMediaPlayer()

        @self.timer.timeout.connect
        # timeout happens every 1 sec
        def _():
            self.ticks_hours_label.setProperty("intValue", 
                self.ticks // (60*60))
            self.ticks_minutes_label.setProperty("intValue", 
                self.ticks // 60)
            self.ticks_seconds_label.setProperty("intValue", 
                self.ticks % 60)

            self.ticks += 1
            self.pomodoro_bar.setProperty("value", self.ticks // 60)
            progress.setValue(int(self.ticks // 60))
            if self.ticks >= 35*60:
                self.timer.stop()
                url = QUrl.fromLocalFile(r"./extra/kuckuck alarm zweimal.wav")
                self.player.setMedia(QMediaContent(url))
                self.player.setVolume(70)
                self.player.play()


        @self.cancel.clicked.connect
        def _():
            self.timer.stop()
            self.player.stop()
            self.running = False
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

        @self.finished.clicked.connect
        def _():
            stop_time = time()
            self.player.stop()
            if self.running:
                self.task.time_spent += self.ticks
                self.timer.stop()
            self.task.last_checked = stop_time
            self.task.done = True
            self.hide()
            write_session(self.task.id, self.start_time,
                    stop_time, True)
            win_main.show()
            if not win_list.isHidden():
                win_list.raise_()
            if not win_what.isHidden() and win_what:
                win_what.raise_()
            
            state.flux_to(S.main)

        @self.reset.clicked.connect
        def _():
            self.start_time = time()
            self.ticks = self.task.time_spent

        @self.pause.clicked.connect
        def _():
            if self.running:
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
                self.timer.start()
                self.timer.start(1000)
                self.start_time = time()
            self.running ^= True

        @self.clock_audio.clicked.connect
        def _():
            if self.player.state() == 1:
                self.player.pause()
            else:
                self.player.play()

    def start_task(self, task):
        state.flux_to(S.running)
        url = QUrl.fromLocalFile(r"./extra/kuckuck (1).wav")
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(50)
        self.player.play()
        progress.show()

        self.task = task
        self.ticks = task.time_spent

        self.show()
        self.task_space.setText(task.space)
        self.task_desc.setText(task.do)
        self.task_notes.setText(task.notes)
        win_main.hide()
        if win_new:
            win_new.hide()
        win_settings.hide()
        self.start_time = time()
        task.last_checked = self.start_time
        self.running = True


class Settings(QtWidgets.QDialog, settings.Ui_Dialog):
    def __init__(self):
        super().__init__() 
        self.setupUi(self) 
        
        self.build_spaces_table()
        
        self.activities_table.horizontalHeader().setVisible(True)
        self.activities_table.setColumnHidden(0, True)
        self.activities_table.sortByColumn(1, Qt.AscendingOrder)
        self.build_activity_table()

        @self.create_activity.clicked.connect
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
                    self.build_activity_table()
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

        @self.rename_activity.clicked.connect
        def _():
            try:
                x = self.activities_table.selectedItems()[0].row()
            except IndexError:
                return
            
            activity_id = self.activities_table.item(x, 1).data(Qt.UserRole)
            name = self.activities_table.item(x, 1).text()

            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                "Aktivität umbenennen",
                f"Wie soll die Aktivität '{name}' umbenannt werden?", 
                QtWidgets.QLineEdit.Normal, "")

            if okPressed and text != '':
                statement = f"""
UPDATE activities 
SET name = '{text}'
WHERE activity_id == {activity_id};
"""
                if query.exec_(statement):
                    print("OK", statement)
                    self.build_activity_table()
                else:
                    logger.warning("SQL failed:" + statement)
                    logger.warning(query.lastError().text())

        @self.delete_activity.clicked.connect
        def _():
            try:
                x = self.activities_table.selectedItems()[0].row()
            except IndexError:
                return

            activity_id = self.activities_table.item(x, 1).data(Qt.UserRole)
            name = self.activities_table.item(x, 1).text()

            mb = QMessageBox()
            mb.setText(f"Wirklich Aktivität '{name}' löschen?")
            mb.setInformativeText("Bitte bestätigen!")
            mb.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            mb.setDefaultButton(QMessageBox.No)

            if mb.exec_() == QMessageBox.Yes:
                statement = f"""
DELETE FROM activities WHERE activity_id == {activity_id};
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


    def build_activity_table(self):
        statement = f"""
        SELECT activity_id, name FROM activities;
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)
            logger.warning(query.lastError().text())
            return

        self.activities_table.setSortingEnabled(False)

        for i, row in enumerate(iter_over(query)):
            self.activities_table.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem()
            self.activities_table.setItem(i, 1, item)
            item.setText(row.value(1))
            # activity_id
            item.setData(Qt.UserRole, row.value(0))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.activities_table.setSortingEnabled(True)
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
            item = QtWidgets.QTableWidgetItem(row.value(1))
            self.spaces_table.setItem(i, 0, item)
            item.setData(Qt.UserRole, row.value(0))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item = QtWidgets.QTableWidgetItem(str(row.value(2)))
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


        self.activities_table.setSortingEnabled(True)
        self.update()

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
    win_running = Running()


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
    progress.setRange(0,35)

    sys.exit(app.exec_())