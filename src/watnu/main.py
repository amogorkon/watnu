"""The entry point for watnu.

Run with python main.py and watch the Magik happen!
"""
import sys
import webbrowser
from collections import Counter, defaultdict, namedtuple
from datetime import datetime, timedelta
from enum import Enum
from itertools import count
from math import cos, isinf, modf, sin
from pathlib import Path
from random import choice, randint, random, seed
from time import time, time_ns
from typing import NamedTuple

import numpy as np
from dateutil.relativedelta import relativedelta
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QDate, QDateTime, QEvent, QModelIndex, Qt, QTime,
                          QTimer, QUrl, QVariant)
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWinExtras import QWinTaskbarButton, QWinTaskbarProgress

import classes
import config
import q
from algo import (balance, check_task_conditions, constraints_met,
                  filter_tasks, prioritize, schedule, skill_level)
from classes import EVERY, ILK, Every, Task, iter_over, submit_sql, typed
from lib.fluxx import StateMachine
from lib.stay import Decoder
from telegram import tell_telegram
from ui import (attributions, character, choose_constraints, choose_deadline,
                choose_repeats, choose_skills, companions, inventory, landing,
                main_window, running_task, settings, statistics, task_editor,
                task_finished, task_list, what_now)

__version__ = (0, 1, 2)
__author__ = 'Anselm Kiefner'
q("Python:", sys.version)
q("Watnu Version:", __version__)
q("Numpy:", np.__version__)

_translate = QtCore.QCoreApplication.translate

load = Decoder()

ACTIVITY = Enum("ACTIVITY", "body mind spirit")
LEVEL = Enum("LEVEL", "MUST SHOULD MAY SHOULD_NOT MUST_NOT")
S = Enum("STATE", "init main editing running final")


def sanitize_db():
    query = submit_sql(f"""
SELECT r.resource_id
FROM resources r
LEFT JOIN task_uses_resource
ON task_uses_resource.resource_id = r.resource_id
WHERE task_uses_resource.task_id is NULL
""")
    i = None
    for i, row in enumerate(iter_over(query)):
        submit_sql(f"""
DELETE FROM resources
WHERE resource_id = {row(0)}
""")
    q(i+1 if i is not None else "Nothing found, so no", "unused resources deleted.")

def write_session(task_id, start, stop, finished=False, pause_time=0):
    query = submit_sql(f"""
        INSERT INTO sessions (task_id, start, stop, pause_time, finished)
        VALUES ('{task_id}', {int(start)}, {int(stop)}, {pause_time}, {finished})
        """)

def breakpoint_():
    from PyQt5.QtCore import pyqtRemoveInputHook
    pyqtRemoveInputHook()
    sys.breakpointhook()

class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
 
        @self.about.triggered.connect
        def _():
            webbrowser.open("https://github.com/amogorkon/watnu/blob/main/README.md")

        @self.attributions.triggered.connect
        def _():
            global win_attributions
            win_attributions = Attributions()
            win_attributions.show()

        @self.button7.clicked.connect
        def _():
            pass

        @self.button8.clicked.connect
        def companions():
            global win_companions
            win_companions = Companions()
            win_companions.show()

        @self.button9.clicked.connect
        def community():
            """Community."""
            webbrowser.open("https://watnu.slack.com/archives/C01HKH7R4AC")

        @self.button4.clicked.connect
        def list_tasks():
            """Task List."""
            win = Task_List()
            win.show()
            list_of_task_lists.append(win)
            
        @self.button5.clicked.connect
        def whatnow():
            """Watnu?!"""
            global win_what
            win_what = What_Now()
            if win_what.lets_check_whats_next():
                win_what.show()
                self.hide()

        @self.button6.clicked.connect
        def add_new_task():
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
            win = Editor()
            win.activateWindow()
            win.show()
     
        @self.button1.clicked.connect
        def statistics():
            global win_statistics
            win_statistics = Statistics()
            win_statistics.show()

        @self.button2.clicked.connect
        def character():
            global win_character
            win_character = Character()
            win_character.show()

        @self.button3.clicked.connect
        def inventory():
            global win_inventory
            win_inventory = Inventory()
            win_inventory.show()

        @self.actionSupportMe.triggered.connect
        def actionSupportMe_triggered():
            webbrowser.open("paypal.me/amogorkon")

        @self.actionIssue_Tracker.triggered.connect
        def actionIssueTracker():
            webbrowser.open("https://github.com/amogorkon/watnu/issues")

        @self.actionContact.triggered.connect
        def actionContact():
            webbrowser.open("https://calendly.com/amogorkon/officehours")


        @self.actionSettings.triggered.connect
        def actionSettings():
            global win_settings
            win_settings = Settings()
            win_settings.show()

        @self.actionExport.triggered.connect
        def actionExport():
            q("Not Implemented.")
            return

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
                            q(f"Tried to load a task with nothing to 'do': {d.items()}.")
                            continue

                        submit_sql(f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{d["space"]}')
""")
                        
                        submit_sql(f"""
INSERT INTO tasks (do, space_id, done)
VALUES ('{d["do"]}',
(SELECT space_id from spaces WHERE name='{d["space"]}'),
{int(bool(d["done"]))} 
)
""")
            state.flux_to(S.main)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            q(config.count, bin(config.coin))
            if config.autostart and False:  # TODO
                import getpass
                try:
                    link = rf'C:\Users\{getpass.getuser()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Start Watnu.bat'
                    target = Path(sys.executable)
                    with open(Path(link), "w+") as file:
                        file.write(rf'start "" {target}')
                except Exception as e:
                    q(e, link, target)
                
            config.write()
            tray.setVisible(False)
            state.flux_to(S.final)
            event.accept()
        else:
            event.ignore()


class What_Now(QtWidgets.QDialog, what_now.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task_priority = None
        self.task_timing = None
        self.task_balanced = None
        self.taskfont = self.task_desc_priority.property("font")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |Qt.CustomizeWindowHint )
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
            global list_of_task_lists
            win = Editor(self.task_priority, win_list=list_of_task_lists)
            if win.exec_():
                self.lets_check_whats_next()
        
        @self.edit_timing.clicked.connect
        def edit_timing():
            global list_of_task_lists
            win = Editor(self.task_timing, win_list=list_of_task_lists)
            if win.exec_():
                self.lets_check_whats_next()

        @self.edit_balanced.clicked.connect
        def edit_balanced():
            global list_of_task_lists
            win = Editor(self.task_balanced, win_list=list_of_task_lists)
            if win.exec_():
                self.lets_check_whats_next()
            
        
        @self.sec_timer.timeout.connect
        def sec_timer_timeout():
            T: float
            # every full second
            if self.task_timing:
                T = time()
                diff = self.task_timing.deadline - T
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

        @self.animation_timer.timeout.connect
        def animation_timer_timeout():
            T = time()
            if self.task_timing:
                self.frame_timing.setStyleSheet(f"""
        * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
                stop:0 black, 
                stop:1 white);
        background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
                stop:0 {activity_color.get(self.task_timing.primary_activity_id, "black")}, 
                stop:{sin(T*0.1) * 0.5 + 0.5} {activity_color.get(self.task_timing.secondary_activity_id, 
                    activity_color.get(
                self.task_timing.primary_activity_id, "black"))},
                stop:1 white);
        }}
        """)
            else:
                self.frame_timing.setStyleSheet("color: grey")

            if self.task_priority:
                self.frame_priority.setStyleSheet(f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
            stop:0 black, 
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
            stop:0 {activity_color.get(self.task_priority.primary_activity_id, "black")},
            stop:{sin(T*0.1) * 0.5 + 0.5} {activity_color.get(self.task_priority.secondary_activity_id, 
                    activity_color.get(self.task_priority.primary_activity_id, "black"))},
            stop:1 white);
    }}
    """)
            else:
                self.frame_priority.setStyleSheet("color: grey")

            if self.task_balanced:
                self.frame_balanced.setStyleSheet(f"""
    * {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
            stop:0 black, 
            stop:1 white);
    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
            stop:0 {activity_color.get(self.task_balanced.primary_activity_id, "black")},
            stop:{sin(T*0.1) * 0.5 + 0.5} {activity_color.get(self.task_balanced.secondary_activity_id, 
                    activity_color.get(self.task_balanced.primary_activity_id, "black"))},
            stop:1 white);
    }}
    """)
            else:
                self.frame_balanced.setStyleSheet("color: grey")

        @self.go_priority.clicked.connect
        def go_priority_clicked():
            self.hide()
            global win_running
            win_running = Running(self.task_priority)

        @self.skip_priority.clicked.connect
        def skip_priority_clicked():
            old_task = self.task_priority
            self.priority_tasks.rotate(-1)
            self.task_priority.last_checked = time()
            self.task_priority = self.priority_tasks[0]
            self.task_desc_priority.setText(self.task_priority.do)
            self.task_desc_priority.adjustSize()
            self.task_space_priority.setText(self.task_priority.space)

            if old_task == self.task_priority:
                mb = QtWidgets.QMessageBox()
                mb.setText("Sorry, es scheint, es gibt keine andere, ähnlich wichtige Aufgabe im Moment.\nAuf gehts!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/fast-forward.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()

        @self.go_balanced.clicked.connect
        def go_balanced_clicked():
            self.hide()
            global win_running
            win_running = Running(self.task_balanced)

        @self.skip_balanced.clicked.connect
        def skip_balanced_clicked():
            now = time()
            self.task_balanced.last_checked = now
            self.balanced_tasks.rotate(-1)
            self.task_balanced = self.balanced_tasks[0]
            self.task_desc_balanced.setText(self.task_balanced.do)
            self.task_desc_balanced.adjustSize()
            self.task_space_balanced.setText(self.task_balanced.space)


        @self.go_timing.clicked.connect
        def go_timing_clicked():
            self.hide()
            global win_running
            win_running = Running(self.task_timing)
 

        @self.skip_timing.clicked.connect
        def skip_timing_clicked():
            self.timing_tasks.rotate(-1)
            self.task_timing.last_checked = time()
            self.task_timing = self.timing_tasks[0]
            self.task_desc_timing.setText(self.task_timing.do)
            self.task_space_timing.setText(self.task_timing.space)

        @self.cancel.clicked.connect
        def cancel_clicked_():
            self.hide()
            win_main.show()

        @self.done_priority.clicked.connect
        def done_priority_clicked():
            win = Task_Finished(self.task_priority)
            win.exec_()            

        @self.done_balanced.clicked.connect
        def _done_balanced_clicked():
            win = Task_Finished(self.task_balanced)
            win.exec_()

        @self.done_timing.clicked.connect
        def done_timing_clicked():
            win = Task_Finished(self.task_timing)
            win.exec_()

    def lets_check_whats_next(self):
        global config, considered_tasks
        seed((config.coin^config.lucky_num) * config.count)
        config.count += 1

        self.groups = defaultdict(lambda: list())

        now = datetime.now()
        for t in considered_tasks:
            check_task_conditions(t, now=now)
        self.tasks = list(filter(lambda t: t.considered_open and constraints_met(t.constraints, now), considered_tasks))

        if not self.tasks:
            mb = QtWidgets.QMessageBox()
            mb.setText("Es sind noch keine Aufgaben gestellt aus denen ausgewählt werden könnte.")
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()
            self.hide()
            return False

        self.set_task_priority()
        self.set_task_balanced()
        self.set_timing_task()
        return True

    def reject(self):
        super().reject()
        win_main.show()
        self.sec_timer.stop()
        self.animation_timer.stop()
        win_what = None


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
            self.task_desc_timing.setText("nix was präsiert")
            self.taskfont.setItalic(True)
            self.task_desc_timing.setFont(self.taskfont)
            self.timing.setEnabled(False)
            self.task_timing = None
            self.deadline = None
            self.deadline_weeks.display("")
            self.deadline_days.display("")
            self.deadline_hours.display("")
            self.deadline_minutes.display("")
            self.deadline_seconds.display("")
            
        else:
            self.taskfont.setItalic(False)
            self.task_desc_timing.setFont(self.taskfont)
            self.timing.setEnabled(True)

        self.task_desc_timing.adjustSize()

    def set_task_balanced(self):
        activity_time_spent = defaultdict(lambda: 0)
        query = submit_sql(f"""
SELECT
    activity_id,
    adjust_time_spent
FROM activities
WHERE activity_id not NULL
""")
        for row in iter_over(query):
            activity_time_spent[typed(row, 0, int, default=None)] = typed(row, 1, int)
            
        query = submit_sql(f"""
SELECT
    primary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    primary_activity_id;
""")
        
        for row in iter_over(query):
            activity_time_spent[typed(row, 0, int, default=None)] += typed(row, 1, int)
        query = submit_sql(f"""
SELECT
    secondary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    secondary_activity_id;
""")
        for row in iter_over(query):
            activity_time_spent[typed(row, 0, int, default=None)] += int(typed(row, 1, int) * 0.382)
        activity_time_spent[None] = max(activity_time_spent.values())

        self.balanced_tasks = balance(self.tasks, activity_time_spent)
        
        self.task_balanced = self.balanced_tasks[0]
        self.task_desc_balanced.setText(self.task_balanced.do)
        self.task_desc_balanced.adjustSize()
        self.task_space_balanced.setText(self.task_balanced.space)
        self.task_space_balanced.setText(self.task_balanced.space)
        self.task_space_balanced.setText(self.task_balanced.space)
        
class Task_List(QtWidgets.QDialog, task_list.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.task_list.setStyleSheet("alternate-background-color: #bfffbf; background-color: #deffde;")
        header = self.task_list.horizontalHeader()
        self.tasks = []

        toolbar = QtWidgets.QToolBar()
        menu = QtWidgets.QMenu()
        clone_as_is = menu.addAction("genau so", self.clone_as_is)
        clone_as_sub = menu.addAction("als Subtask", self.clone_as_sub)
        clone_as_sup = menu.addAction("als Supertask", self.clone_as_sup)
        self.button9.setMenu(menu)
        
        item = QtWidgets.QTableWidgetItem()
        item.setFlags(Qt.ItemIsUserCheckable)
        self.task_list.setVerticalHeaderItem(0, item)
        
        if state() is S.running:
            self.button5.setEnabled(False)

        self.build_task_list()
        self.update()
        
        @self.button1.clicked.connect
        def draft_undraft():
            try:
                x = self.task_list.selectedItems()[0].row()
                task = Task(self.task_list.item(x, 0).data(Qt.UserRole))
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
            submit_sql(f"""
    UPDATE tasks
    SET draft = {not task.is_draft}
    WHERE id == {task.id}
    """)
            self.task_list.removeRow(x)
            self.update()

        @self.button2.clicked.connect
        def done_undone():
            try:
                x = self.task_list.selectedItems()[0].row()
                task = Task(self.task_list.item(x, 0).data(Qt.UserRole))
            except IndexError:
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            submit_sql(f"""
UPDATE tasks
SET done = {not task.is_done}
WHERE id == {task.id}
""")
            self.task_list.removeRow(x)
            self.update()
            consider_tasks()

        @self.button3.clicked.connect
        def active_inactive():
            try:
                x = self.task_list.selectedItems()[0].row()
                task = Task(self.task_list.item(x, 0).data(Qt.UserRole))
            except IndexError:
                q("indexerror?")
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            submit_sql(f"""
    UPDATE tasks
    SET inactive = {not task.is_inactive}
    WHERE id == {task.id}
    """)
            
            self.task_list.removeRow(x)
            self.update()
            consider_tasks()
            
        @self.button4.clicked.connect
        def edit_task():
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
            
            task = Task(self.task_list.item(x,0).data(Qt.UserRole))
            
            if state() is S.running and task == win_running.task:
                win_running.show()
                win_running.activateWindow()
                win_running.raise_()
                return
            
            win = Editor(task, win_list=self)
            win.show()

        @self.button5.clicked.connect
        def start_task():
            global win_running
            if state() is S.running:
                win_running.show()
                win_running.activateWindow()
                win_running.raise_()
                self.hide()
                return

            try:
                x = self.task_list.selectedItems()[0].row()
            except IndexError:
                return

            task = Task(self.task_list.item(x, 0).data(Qt.UserRole))
            self.hide()

            win_running = Running(task, win_list=self)

        @self.button6.clicked.connect
        def create_task():
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein Task bearbeitet.")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return
            
            win = Editor(win_list=self)
            win.show()
            
        @self.button7.clicked.connect
        def delete_undelete():
            try:
                x = self.task_list.selectedItems()[0].row()
                task = Task(self.task_list.item(x, 0).data(Qt.UserRole))
            except IndexError:
                return
            if state() is S.editing:
                mb = QtWidgets.QMessageBox()
                mb.setText("Es wird schon ein anderer Task bearbeitet.")
                mb = QtWidgets.QMessageBox()
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
                mb.setWindowTitle("Hmm..")
                mb.exec_()
                return

            submit_sql(f"""
UPDATE tasks
SET deleted = {not task.is_deleted}
WHERE id == {task.id}
""")
            self.task_list.removeRow(x)
            self.update()
            consider_tasks()

        @self.button8.clicked.connect
        def throw_coins():
            # vonNeumann!
            i = 0
            first = 0
            for i in count():
                # least significant bit of high-res time *should* give enough entropy
                first = (time_ns()// 100) & 1
                second = (time_ns()// 100) & 1
                if first != second:
                    break
            # 'threw 31688 pairs!' - so much for "should"
            q("threw", i, "pairs!")

            # bitshift to the left
            config.coin <<= 1
            # then set the bit - 
            config.coin |= first
            seed((config.coin^config.lucky_num) * config.count)

            x = choice(['Kopf', 'Zahl'])
            mb = QtWidgets.QMessageBox()
            mb.setWindowTitle("Hmm..")
            if x == "Kopf":
                mb.setText(f"Du hast Kopf geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-heads.svg"))
            else:
                mb.setText(f"Du hast Zahl geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-tails.svg"))
            mb.exec_()

        @self.status.buttonClicked.connect
        def status_switched():
            self.build_task_list()


        @self.field_filter.textChanged.connect
        def field_filter_changed():
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
        
        task = Task(self.task_list.item(x,0).data(Qt.UserRole))
        win = Editor(task, cloning=True, as_sup=0, win_list=self)
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
        
        task = Task(self.task_list.item(x,0).data(Qt.UserRole))
        win = Editor(task, cloning=True, as_sup=-1, win_list=self)
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
        
        task = Task(self.task_list.item(x,0).data(Qt.UserRole))
        win = Editor(task, cloning=True, as_sup=1, win_list=self)
        win.show()

    def build_task_list(self):
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
        query= submit_sql(f"""
        SELECT id FROM tasks 
        WHERE 
        done == {self.status_done.isChecked()} AND
        deleted == {self.status_deleted.isChecked()} AND 
        draft == {self.status_draft.isChecked()} AND
        inactive == {self.status_inactive.isChecked()};
        """)

        self.tasks  = [Task(row(0)) for row in iter_over(query)]
        filter_text = self.field_filter.text().casefold()
        self.arrange_list(filter_tasks(self.tasks, filter_text))
        self.update()

    def arrange_list(self, tasks):
        """Needs to be extra, otherwise filtering would hit the DB repeatedly."""
        q("arranging list", len(tasks), "tasks")
        self.task_list.setSortingEnabled(False)

        ok = QIcon("./extra/feathericons/check.svg")
        nok = QIcon("./extra/feathericons/x.svg")

        for i, t in enumerate(tasks):
            self.task_list.setRowCount(i+1)            
            item = QtWidgets.QWidget()
            chk_bx = QtWidgets.QCheckBox()
            lay_out = QtWidgets.QHBoxLayout(item)
            lay_out.addWidget(chk_bx)
            lay_out.setAlignment(Qt.AlignCenter)
            lay_out.setContentsMargins(0,0,0,0)
            item.setLayout(lay_out)
            self.task_list.setCellWidget(i, 0, item)
            item = QtWidgets.QTableWidgetItem()
            item.setData(Qt.UserRole, t.id)
            self.task_list.setItem(i, 0, item)
            short = t.do if len(t.do) <= 80 else t.do[:80] + "[…]"
            item = QtWidgets.QTableWidgetItem(short)
            item.setToolTip(t.do)
            self.task_list.setItem(i, 1, item)

            #item.setTextAlignment(QtCore.Qt.AlignCenter)
            item = QtWidgets.QTableWidgetItem(t.space)
            self.task_list.setItem(i, 2, item)
            item = QtWidgets.QTableWidgetItem(str(t.level))
            self.task_list.setItem(i, 3, item)
            item = QtWidgets.QTableWidgetItem(str(t.priority))
            self.task_list.setItem(i, 4, item)
            item = QtWidgets.QTableWidgetItem(str(t.ilk.name))
            self.task_list.setItem(i, 5, item)
            item = QtWidgets.QTableWidgetItem(
                datetime.fromtimestamp(t.deadline).isoformat() 
                    if not isinf(t.deadline) else
                "---")
            self.task_list.setItem(i, 6, item)
        
        if not tasks:
            self.task_list.clearContents()
            self.task_list.setRowCount(0)
        self.task_list.setSortingEnabled(True)
        self.task_list.resizeColumnsToContents()
        
    def reject(self):
        super().reject()
        if state() is  S.running:
            win_running.show()
            win_running.raise_()
        else:
            win_main.show()
            win_main.raise_()
        
        list_of_task_lists.remove(self)


class Editor(QtWidgets.QWizard, task_editor.Ui_Wizard):
    """Editor for new or existing tasks."""
    def __init__(self, 
                 task:Task=None, 
                 cloning:bool=False, 
                 templating:bool=False, 
                as_sup:bool=0, 
                win_list:Task_List=None,
                ):
        super().__init__()
        self.activateWindow()
        self.setupUi(self)
        self.win_list = win_list

        if cloning:
            self.setWindowTitle(_translate("Wizard", "Bearbeite Klon"))
        
        if templating:
            self.setWindowTitle(_translate("Wizard", "Bearbeite verknüpfte Aufgabe"))
        
        self.setOption(QtWidgets.QWizard.HaveFinishButtonOnEarlyPages, True)
        self.task:Task = task
        self.cloning = cloning
        self.templating = templating
        self.subtasks: list[int] = []
        self.supertasks: list[int] = []
        self.skill_ids: list[int] = []

        # clone as subtask of the given task
        if as_sup == -1:
            self.supertasks = [self.task.id]

        # given task is a subtask of the new task
        if as_sup == 1:
            self.subtasks = [self.task.id]

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
        model.setTable("spaces")
        model.setSort(1, Qt.AscendingOrder)
        model.select()
        self.space.setModel(model)
        self.space.setModelColumn(1)
        self.constraints:str = None
        self.deadline = float("inf")
        self.repeats: namedtuple = None

        query = submit_sql(f"""
        SELECT activity_id, name FROM activities;
        """)

        for i, row in enumerate(iter_over(query)):
            self.activity.addItem(row(1), QVariant(row(0)))
            self.secondary_activity.addItem(row(1), QVariant(row(0)))

        # editing a task - need to set all values accordingly
        if task:
            self.deadline = task.deadline
            self.skill_ids = self.task.skill_ids
            self.priority.setValue(task.priority)

            for url, ID in task.resources:
                self.resources.addItem(url, ID)

            self.desc.document().setPlainText(task.do)

            if task.ilk is ILK.habit:
                self.is_habit.setChecked(True)
            if task.ilk is ILK.tradition:
                self.is_tradition.setChecked(True)
            if task.ilk is ILK.routine:
                self.is_routine.setChecked(True)
                
            if task.ilk in (ILK.tradition, ILK.routine):
                self.button8.setEnabled(True)
            self.notes.document().setPlainText(task.notes)
            self.space.setCurrentIndex(self.space.findText(self.task.space))
            self.level.setCurrentIndex(self.level.findText(self.task.level))
            self.activity.setCurrentIndex(self.activity.findText(self.task.activity))
            self.secondary_activity.setCurrentIndex(
                self.secondary_activity.findText(self.task.secondary_activity))
            self.repeats = self.task.repeats
        # new task - preset space by previous edit
        else:
            self.space.setCurrentIndex(self.space.findText(last_edited_space))

        @self.kind_of.buttonToggled.connect
        def kind_of_toggled():
            if self.is_task.isChecked() or self.is_habit.isChecked():
                self.button8.setEnabled(False)
            else:
                self.button8.setEnabled(True)

        @self.resource_add.clicked.connect
        def resource_added():
            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                "Resource hinzufügen",
                f"Welche URL?", 
                QtWidgets.QLineEdit.Normal, "")

            if okPressed and text != '':
                submit_sql(f"""
INSERT OR IGNORE INTO resources
(url)
VALUES ('{text}')
""")
                query = submit_sql(f"""
SELECT resource_id
FROM resources
WHERE url = '{text}'
""")
                query.next()
                resource_id = query.value(0)
                self.resources.addItem(text, resource_id)

        @self.resource_remove.clicked.connect
        def _():
            self.resources.removeItem(self.resources.currentIndex())

        @self.button1.clicked.connect
        def subtasks_button():
            q("button1 clicked", self.task)
            dialog = Chooser(self, self.task, kind="subtasks")
            dialog.exec_()

        @self.button2.clicked.connect
        def time_constraints_button():
            q("button2 clicked", self.task)
            dialog = Chooser(self, self.task, kind="constraints")
            dialog.exec_()

        @self.button3.clicked.connect
        def _():
            q("button3 clicked", self.task)

        @self.button4.clicked.connect
        def _():
            q("button4 clicked", self.task)

        @self.button5.clicked.connect
        def _():
            q("button5 clicked", self.task)
            dialog = Chooser(self, self.task, kind="deadline")
            dialog.exec_()

        @self.button6.clicked.connect
        def _():
            q("button6 clicked", self.task)

        @self.button7.clicked.connect
        def supertasks_button():
            q("button7 clicked", self.task)
            dialog = Chooser(self, self.task, kind="supertasks")
            dialog.exec_()

        @self.button8.clicked.connect
        def _():
            q("button8 clicked", self.task)
            dialog = Chooser(self, self.task, kind="repeats")
            dialog.exec_()

        @self.button9.clicked.connect
        def skills_button():
            q("button9 clicked", self.task)
            dialog = Chooser(self, self.task, kind="skills")
            dialog.exec_()

        @self.space.currentIndexChanged.connect
        def _():
            space_id =  self.space.model().data(
                            self.space.model().index(
                            self.space.currentIndex(), 0))
            if space_id is not None:
                for row in iter_over(submit_sql(f"""
SELECT primary_activity_id, secondary_activity_id
FROM spaces
WHERE space_id = {space_id}
                """)):
                    if row(0):
                        self.activity.setCurrentIndex(self.activity.findData(QVariant(row(0))))
                    else:
                        self.activity.setCurrentIndex(0)
                    if row(1):
                        self.secondary_activity.setCurrentIndex(self.secondary_activity.findData(QVariant(row(1))))
                    else: 
                        self.secondary_activity.setCurrentIndex(0)

    def accept(self):
        # TODO check sanity for traditions and routines
        super().accept()
        global last_edited_space
        
        do = self.desc.toPlainText()
        priority:float = self.priority.value()
        space_id:int = self.space.model().data(self.space.model().index(self.space.currentIndex(), 0))

        last_edited_space = self.space.currentText()
        primary_activity_id = x if (x:=self.activity.currentData()) is not None else 'NULL'
        secondary_activity_id = x if (x:=self.secondary_activity.currentData()) is not None else 'NULL'
        level_id:int = self.level.model().data(self.level.model().index(self.level.currentIndex(), 0))
        
        task_type = ILK.task
        if self.is_habit.isChecked():
            task_type = ILK.habit
        if self.is_routine.isChecked():
            task_type = ILK.routine
        if self.is_tradition.isChecked():
            task_type = ILK.tradition
        
        task_id: int

        # it really is a new task
        if not self.task or (self.task and self.cloning) or (self.task and self.templating):
            query = submit_sql(f"""
INSERT INTO tasks 
(do, 
space_id, 
primary_activity_id,
secondary_activity_id,
ilk
)

VALUES 
('{do}', 
{x if (x := space_id) is not None else 0},
{primary_activity_id},
{secondary_activity_id},
{task_type.value}
);
""")             
        
            task_id = query.lastInsertId()
            
            # subtasks
            for required_task in self.subtasks:
                submit_sql(f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES (
{task_id}, {required_task}
);
""")
            # supertasks
            for task_of_concern in self.supertasks:
                submit_sql(f"""
    INSERT OR IGNORE INTO task_requires_task
        (task_of_concern, required_task)
        VALUES (
        {task_of_concern}, {task_id}
        );
    """)
        # we're editing a task
        else:
            task_id = self.task.id
            submit_sql(f"""
UPDATE tasks 
SET do = '{do}',
    priority = {priority},
    level_id = {level_id},
    primary_activity_id = {primary_activity_id},
    secondary_activity_id = {secondary_activity_id},
    space_id = {space_id},
    ilk = {task_type.value}
WHERE id={task_id}
""", debugging=True)        
            # need to clean up first
            submit_sql(f"""
DELETE FROM task_requires_task WHERE task_of_concern == {task_id}
    """)
            submit_sql(f"""
DELETE FROM task_requires_task WHERE required_task == {task_id}
""")
            submit_sql(f"""
DELETE FROM task_uses_resource WHERE task_id = {task_id}
    """)
            submit_sql(f"""
DELETE FROM task_trains_skill WHERE task_id = {task_id}
    """)
            submit_sql(f"""
DELETE FROM constraints WHERE task_id = {task_id}
            """)
            submit_sql(f"""
DELETE FROM deadlines WHERE task_id = {task_id}
            """)
            submit_sql(f"""
DELETE FROM repeats WHERE task_id = {task_id}
            """)

        # enter fresh, no matter whether new or old
        
        for required_task in self.subtasks:
           submit_sql(f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES ({task_id}, {required_task})
;
""")
        for task_of_concern in self.supertasks:
            submit_sql(f"""
INSERT OR IGNORE INTO task_requires_task
(task_of_concern, required_task)
VALUES ({task_of_concern}, {task_id})
;
""")        
        for skill_id in self.skill_ids:
            submit_sql(f"""
INSERT INTO task_trains_skill
(task_id, skill_id)
VALUES (
{task_id}, {skill_id}
    );
""")
        for i in range(self.resources.count()):
            submit_sql(f"""
INSERT INTO task_uses_resource
(task_id, resource_id)
VALUES ({task_id}, {self.resources.itemData(i)});
""")
        if self.constraints:
            submit_sql(f"""
    INSERT INTO constraints
    (task_id, flags)
    VALUES ({task_id}, '{self.constraints}')
            """)
        if self.deadline != float("inf"):
            submit_sql(f"""
INSERT INTO deadlines
(task_id, time_of_reference)
VALUES ({task_id}, '{self.deadline}')
            """)
            
        if self.repeats is not None:
            submit_sql(f"""
INSERT INTO repeats
(task_id, every_ilk, x_every, min_distance, x_per)
VALUES (
{task_id}, 
{self.repeats.every_ilk.value},
{self.repeats.x_every},
{self.repeats.x_per},
{self.repeats.per_ilk.value}
)
            """, debugging=True)

        for win in list_of_task_lists:
            win.build_task_list()
        
        consider_tasks()
        state.flux_to(S.main)

    def reject(self):
        super().reject()
        state.flux_to(S.main)

class Running(QtWidgets.QDialog, running_task.Ui_Dialog):
    def __init__(self, task, win_list=None):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |Qt.CustomizeWindowHint )
        win_main.hide()
        if win_new:
            win_new.hide()
            
        self.win_list = win_list
        
        if win_settings:
            win_settings.hide()

        self.task:Task = task
        self.skill_levels = [(skill.id, int(skill_level(skill.time_spent))) 
                                for skill in task.skills]
        self.pause_time = 0
        self.paused = False
        self.start_time = time()
        self.task.last_checked = self.start_time
        self.timer = QTimer()
        self.animation_timer = QTimer()
        self.animation_timer.start(15)
        self.player = QMediaPlayer()

        url = QUrl.fromLocalFile(r"./extra/alarm once.wav")
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(70)
        self.player.play()

        self.ticks = 0  # time tracked in this session
        self.time_spent = 0  # the time previously tracked by machine
        self.time_spent = self.task.time_spent
        # user estimates time spent with this task untracked 
        if task.ilk is ILK.habit:
            self.adjust_time_spent = 0  
        else:
            self.adjust_time_spent = self.task.adjust_time_spent
        state.flux_to(S.running)
        self.pomodoro = -35 * 60
        doc = QtGui.QTextDocument(task.notes)
        self.notes.setDocument(doc) 

        doc = QtGui.QTextDocument(task.do)
        self.desc.setDocument(doc)
        
        for win in list_of_task_lists:
            win.button5.setEnabled(False)

        progress.show()
        if self.task.resources:
            self.open_resources.setEnabled(True)
            text = '; '.join(url for url, ID in self.task.resources)
            self.open_resources.setText(str(text))   

        url = QUrl.fromLocalFile(r"./extra/tictoc.wav")
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(config.tictoc_volume)
        self.player.play()

        self.task_space.setText(task.space)
        
        
        self.show()
        self.start_task()
        self.timer.start(1000)
        self.pomodoro_bar.setStyleSheet("""
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
}

QProgressBar::chunk {
    background-color: steelblue;
    border-radius: 5px;
}
""")

        @self.animation_timer.timeout.connect
        def animation_timer_timeout():
            if self.task is None:
                return
            T = time()
            self.frame.setStyleSheet(f"""
* {{color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, 
        stop:0 black, 
        stop:1 white);
background: qlineargradient(x1:0 y1:0, x2:1 y2:0, 
        stop:0 {activity_color.get(self.task.primary_activity_id, "black")},
        stop:{sin(T*0.9) * 0.5 + 0.5} {activity_color.get(self.task.secondary_activity_id, 
                  activity_color.get(self.task.primary_activity_id, "black"))},
        stop:1 white);
}}
""")


        @self.open_resources.clicked.connect
        def _():
            for url, _ in self.task.resources:
                webbrowser.open(url)

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
                q("SQL failed:\n" + statement)
                q(query.lastError().text())
            return

        @self.timer.timeout.connect
        # timeout happens every 1 sec
        def _():
            if self.paused:
                self.pause_time += 1
                return

            self.ticks += 1
            self.pomodoro += 1

            if not self.task.ilk is ILK.habit:
                total = (x if 
                    (x:=(self.time_spent + self.adjust_time_spent + self.ticks)) > 0
                        else 0)
            else:
                total = self.ticks + self.adjust_time_spent
            
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
                try:
                    tell_telegram("pomodoro done! pause!", config)
                except Exception as e:
                    q(e)
                url = QUrl.fromLocalFile(r"./extra/alarm twice.wav")
                self.player.setMedia(QMediaContent(url))
                self.player.setVolume(70)
                self.player.play()
                progress.setValue(0)
                self.pause = True
                self.pomodoro_bar.setStyleSheet("""
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
}

QProgressBar::chunk {
    background-color: yellowgreen;
    border-radius: 5px;
}
""")
                

            if 0 < self.pomodoro <= 5 * 60:
                pomodoro_percent = 100 - (self.pomodoro / (5*60) * 100)
                self.pomodoro_bar.setProperty("value", pomodoro_percent)

            if self.pomodoro > 5 * 60:
                self.pomodoro = - 35 * 60
                tell_telegram(f"Pause vorbei! Weiter gehts mit: {self.task.do}", config)
                url = QUrl.fromLocalFile(r"./extra/alarm once.wav")
                self.player.setMedia(QMediaContent(url))
                self.player.setVolume(70)
                self.player.play()
                self.pomodoro_bar.reset()
                self.pomodoro_bar.setStyleSheet("""
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
}

QProgressBar::chunk {
    background-color: darkorange;
    border-radius: 5px;
}
""")

        @self.button1.clicked.connect
        def _():
            pass
        
        @self.button2.clicked.connect
        def _():
            print(23, self.paused)
            if not self.paused:
                self.button2.setText("Unpause")
                self.paused = True
                progress.pause()
                self.player.stop()
            else:
                self.button2.setText("Pause")
                self.paused = False
                progress.resume()
                self.player.play()
        
        @self.button3.clicked.connect
        def _():
            self.start_time = time()
            self.time_spent = self.task.time_spent
            self.adjust_time_spent = self.task.adjust_time_spent
            self.ticks = 0
        
        @self.button4.clicked.connect
        def _():
            pass
        
        @self.button5.clicked.connect
        def _():
            stop_time = time()
            self.player.stop()
            if self.timer.isActive():
                self.timer.stop()
            self.task.last_checked = stop_time
            self.task.time_spent = self.time_spent + self.ticks
            self.task.adjust_time_spent = self.adjust_time_spent
            self.hide()
            write_session(self.task.id, self.start_time, stop_time,
                            finished=False, pause_time=self.pause_time)
            win_main.show()
            if self.win_list:
                self.win_list.raise_()

            if not win_what.isHidden() and win_what:
                win_what.raise_()

            progress.setValue(0)

            state.flux_to(S.main)
        
        @self.button6.clicked.connect
        def _():
            pass

        @self.button7.clicked.connect
        def _():
            if (self.adjust_time_spent + self.time_spent + self.ticks) >= 5*60:
                self.adjust_time_spent -= 5 * 60

        @self.button8.clicked.connect
        def _():
            if (timer_was_running := self.timer.isActive()):
                self.timer.stop()
                self.player.pause()
            win = Task_Finished(self.task, 
                                ticks=self.ticks, 
                                start=self.start_time, 
                                pause_time=self.pause_time)
            if not win.exec_():
                if timer_was_running:
                    self.timer.start()
                    self.player.play()
                return
            self.hide()
            win_main.show()
            if self.win_list:
                self.win_list.raise_()
            if not win_what.isHidden() and win_what:
                win_what.raise_()
            
            progress.setValue(0)
            state.flux_to(S.main)
            
        @self.button9.clicked.connect
        def _():
            self.adjust_time_spent += 5 * 60


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
        for win in list_of_task_lists:
            win.button5.setEnabled(True)
        self.hide()

        if self.win_list:
            self.win_list.show()
            self.win_list.raise_()
        else:
            win_what.show()
            win_what.raise_()
        state.flux_to(S.main)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.cancel()
        event.accept()

    def start_task(self):
        # check if working conditions are optimal once a day
        query = submit_sql(f"""
        SELECT start 
        FROM sessions
        ORDER BY start DESC;
        """)

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

        query = submit_sql(f"""
        SELECT text, mantra_id
        FROM mantras
        ORDER BY last_time ASC;
        """)

        mantra_id = None
        
        if not query.next():
            mantra = None
        else:
            mantra, mantra_id = query.value(0), query.value(1)

        td = now - then

        if td.days == 0 and (60*25 <= td.seconds <= 60*120) or True:
            mb = QtWidgets.QMessageBox()
            mb.setText(f"""
Gesundheitshinweis:
Alle ~25 Minuten kurz Stoßlüften & ausreichend Wasser trinken :)
Und denk dran: 
{"Always look on the bright side of life!" if not mantra else mantra}
"""
)  

        if mantra:
            submit_sql(f"""
    UPDATE mantras
    SET last_time = {int(time())}
    WHERE mantra_id = {mantra_id}
    """)
            mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
            mb.setWindowTitle("Hmm..")
            mb.exec_()

def Chooser(editor: Editor, task: Task, kind:str):
    """Returns the fitting instance of a Chooser."""
    class SkillChooser(QtWidgets.QDialog, choose_skills.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.task = task
            self.editor = editor
            model = QSqlTableModel()
            model.setTable("skills")
            model.setSort(1, Qt.AscendingOrder)
            model.select()
            self.listView.setModel(model)
            self.listView.setModelColumn(1)

            if task:
                # holy crap, that was a difficult birth..
                self.listView.selectionModel().clear()
                for index in range(model.rowCount()):
                    if model.itemData(model.index(index, 0))[0] in task.skill_ids:
                        self.listView.selectionModel().select(
                            model.index(index, 1), QtCore.QItemSelectionModel.Select)    
        def accept(self):
            super().accept()
            self.editor.skill_ids = [self.listView.model().record(idx.row()).value("skill_id") for idx in self.listView.selectedIndexes()]
    class SubTaskChooser(QtWidgets.QDialog, choose_skills.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.task = task
            self.editor = editor
            model = QSqlTableModel()
            model.setTable("tasks")
            model.setSort(1, Qt.AscendingOrder)
            model.select()
            self.listView.setModel(model)
            self.listView.setModelColumn(1)

            if task:
                # holy crap, that was a difficult birth..
                self.listView.selectionModel().clear()
                for index in range(model.rowCount()):
                    if Task(model.itemData(model.index(index, 0))[0]) in task.subtasks:
                        self.listView.selectionModel().select(
                            model.index(index, 1), QtCore.QItemSelectionModel.Select)

        def accept(self):
            self.editor.subtasks = [self.listView.model().record(idx.row()).value("id") for idx in self.listView.selectedIndexes()]

    class SuperTaskChooser(QtWidgets.QDialog, choose_skills.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.task = task
            self.editor = editor
            model = QSqlTableModel()
            model.setTable("tasks")
            model.setSort(1, Qt.AscendingOrder)
            model.select()
            self.listView.setModel(model)
            self.listView.setModelColumn(1)

            if task:
                # holy crap, that was a difficult birth..
                self.listView.selectionModel().clear()
                for index in range(model.rowCount()):
                    if Task(model.itemData(model.index(index, 0))[0]) in task.supertasks:
                        self.listView.selectionModel().select(
                            model.index(index, 1), QtCore.QItemSelectionModel.Select)

        def accept(self):
            self.editor.supertasks = [self.listView.model().record(idx.row()).value("id") for idx in self.listView.selectedIndexes()]

    class Constraints(QtWidgets.QDialog, choose_constraints.Ui_Dialog):
        def __init__(self, editor, task:Task=None):
            super().__init__()
            self.setupUi(self)
            self.editor = editor
            self.table.horizontalHeader().setHighlightSections(False)
            for i, (hour, part) in enumerate((hour, part) for hour in range(24) 
                                                        for part in range(0,6)):
                item = QtWidgets.QTableWidgetItem(f"{hour}: {part}0-{part}9")
                if i % 6 == 0:
                    font = QtGui.QFont()
                    font.setItalic(True)
                    font.setWeight(90)
                    item.setFont(font)
                self.table.setVerticalHeaderItem(i, item)
            try: 
                for column, day in enumerate(np.reshape(task.constraints, (7,144))):
                    for row, value in enumerate(day):
                        if value:
                            self.table.setCurrentCell(row, column)
            except AttributeError:
                pass
                        

            @self.buttonBox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect
            def reset():
                self.table.clearSelection()

            @self.buttonBox.button(QtWidgets.QDialogButtonBox.Discard).clicked.connect
            def discard():
                self.editor.constraints = None
                self.close()

        def accept(self):
            super().accept()
            A = np.zeros(1008, int)
            A[[idx.column() *  144 + idx.row() for idx in  self.table.selectedIndexes()]] = 1
            self.editor.constraints = (x := ''.join(str(x) for x in A))

    class DeadlineChooser(QtWidgets.QDialog, choose_deadline.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.editor = editor
            self.reference_date.setDate(QtCore.QDate().currentDate())
        
            @self.enter_date.clicked.connect
            def enter_date():
                now = datetime.fromtimestamp(self.reference_date.dateTime().toSecsSinceEpoch())
                days = self.in_days.value()
                weeks = self.in_weeks.value()
                months = self.in_months.value()
                qdate = QDateTime()
                qdate.setSecsSinceEpoch(
                    int(datetime.timestamp(now + relativedelta(days=days, weeks=weeks, months=months))))
                self.reference_date.setDateTime(qdate)

        def accept(self):
            super().accept()
            self.editor.deadline = self.reference_date.dateTime().toSecsSinceEpoch()


    class RepeatChooser(QtWidgets.QDialog, choose_repeats.Ui_Dialog):
        def __init__(self, editor:Editor, task:Task=None):
            super().__init__()
            self.setupUi(self)
            self.editor = editor
            self.every_ilk.setId(self.every_minute, 1)
            self.every_ilk.setId(self.every_hour, 2)
            self.every_ilk.setId(self.every_day, 3)
            self.every_ilk.setId(self.every_week, 4)
            #self.every_ilk.setId(self.every_month, 5)
            self.every_ilk.setId(self.every_year, 6)
            
            self.per_ilk.setId(self.per_minute, 1)
            self.per_ilk.setId(self.per_hour, 2)
            self.per_ilk.setId(self.per_day, 3)
            self.per_ilk.setId(self.per_week, 4)
            #self.per_ilk.setId(self.per_month, 5)
            self.per_ilk.setId(self.per_year, 6)
            
            if task is not None:
                self.every_ilk.button(task.repeats.every_ilk.value).setChecked(True)
                self.x_every.setValue(task.repeats.amount)
                self.per_ilk.button(task.repeats.per_ilk.value).setChecked(True)
                self.x_per.setValue(task.repeats.min_distance)
                
        
        def accept(self):
            super().accept()
            self.editor.repeats = Every(EVERY(self.every_ilk.checkedId()),
                                        self.x_every.value(),
                                        EVERY(self.per_ilk.checkedId()),
                                        self.x_per.value()
                                        )

    cases = {"subtasks": SubTaskChooser, 
             "supertasks": SuperTaskChooser, 
             "skills": SkillChooser,
             "deadline": DeadlineChooser,
             "constraints": Constraints,
             "repeats": RepeatChooser,
             }
    return cases[kind](editor, task)


class Task_Finished(QtWidgets.QDialog, task_finished.Ui_Dialog):
    def __init__(self, task, ticks=0, start=None, old_skills=None, pause_time=0):
        super().__init__()
        self.setupUi(self)
        self.pause_time = pause_time
        self.task = task
        self.start = time() if not start else start
        self.old_skills = old_skills or [
            (skill.id, int(skill_level(skill.time_spent))) for skill in task.skills
        ]


        self.task_desc.setText(task.do)
        if task.ilk is not ILK.habit:
            total = task.time_spent + task.adjust_time_spent + ticks
        else:
            total = ticks
        rst, hours = modf(total/(60*60))
        rst, minutes = modf(rst*60)
        self.hours.setValue(int(hours))
        self.minutes.setValue(int(minutes))
                    
    def accept(self):
        super().accept()
        if self.task.ilk not in (ILK.habit, ILK.routine):  # ? is that right?
            total = self.hours.value() * 60*60 + self.minutes.value() * 60 - self.pause_time
        else:
            total = (self.task.time_spent + self.task.adjust_time_spent + 
                self.hours.value() * 60*60 + self.minutes.value() * 60)

        submit_sql(f"""
    UPDATE tasks 
    SET adjust_time_spent = {total - self.task.time_spent},     
        done=TRUE
    WHERE id={self.task.id};
    """)
        write_session(self.task.id, self.start, time(), 
                        finished=True, pause_time=self.pause_time)

        new_skills = [(skill.id, int(skill_level(skill.time_spent))) 
                                        for skill in self.task.skills]

        for x, y in zip(self.old_skills, new_skills):
            if x[1] < y[1]:
                mb = QtWidgets.QMessageBox()
                mb.setText("""
YEAH! You made it to the next LEVEL in {y[0]}: {y[1]}!
"""
            )
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/star.svg"))
                mb.setWindowTitle("LEVEL UP")
                mb.exec_()

        for win in list_of_task_lists:
            win.button5.setEnabled(True)
            win.build_task_list()
        win_what.lets_check_whats_next()
        
        if self.task.ilk is ILK.tradition:
                mb = QMessageBox()
                mb.setText("""
Die beendete Aufgabe ist eine Tradition - soll jetzt ein neuer Eintrag für den nächsten Stichtag erstellt werden?
""")
                mb.setInformativeText("Bitte bestätigen!")
                mb.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                mb.setDefaultButton(QMessageBox.Yes)
                 # TODO check on edit if deadline and repeat is set for tradition
                if mb.exec_():
                    win = Editor(task=self.task, templating=True)   # TODO templating!
                    win.exec_()
        return True

    def reject(self):
        super().reject()
        return False

class Character(QtWidgets.QDialog, character.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.skills_table.sortByColumn(0, Qt.AscendingOrder)
        self.build_skill_table()


    def build_skill_table(self):
        query = submit_sql(f"""
        SELECT skill_id, task_id FROM task_trains_skill;
        """)
        if not query: return

        self.skills_table.setSortingEnabled(False)

        skills_trained_by = defaultdict(lambda: list())

        for row in iter_over(query):
            skills_trained_by[row(0)].append(row(1))

        for i, skill in enumerate(skills_trained_by):
            query = submit_sql(f"""
            SELECT name FROM skills WHERE skill_id=={skill};
            """)

            self.skills_table.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem(query.value(0))
            self.skills_table.setItem(i, 0, item)
            item.setData(Qt.UserRole, skill)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item = QtWidgets.QTableWidgetItem(str(len(skills_trained_by[skill])))
            self.skills_table.setItem(i, 1, item)
            item = QtWidgets.QTableWidgetItem(str(sum(
                    Task(x).total_time_spent for x in skills_trained_by[skill]) 
                                                // (60*60)))
            self.skills_table.setItem(i, 2, item)
 
        self.skills_table.setSortingEnabled(True)
        self.update()


class Settings(QtWidgets.QDialog, settings.Ui_Dialog):
    def __init__(self):
        super().__init__() 
        self.setupUi(self) 
        
        self.build_spaces_table()
        self.space_id = None
        
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
                submit_sql(f"""
INSERT OR IGNORE INTO skills (name)
VALUES ('{text}')
""")
                self.build_skill_table()

        @self.rename_skill.clicked.connect
        def _():
            try:
                x = self.skills_table.selectedItems()[0].row()
            except IndexError:
                return
            
            skill_id = self.skills_table.item(x, 1).data(Qt.UserRole)
            name = self.skills_table.item(x, 1).text()

            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                "Fähigkeit umbenennen",
                f"Wie soll die Fähigkeit '{name}' umbenannt werden?", 
                QtWidgets.QLineEdit.Normal, "")

            if okPressed and text != '':
                submit_sql(f"""
UPDATE skills 
SET name = '{text}'
WHERE skill_id == {skill_id};
""")
                self.build_skill_table()

        @self.clear_unused_resources.clicked.connect
        def _():
            q("sanitizing db..")
            sanitize_db()

        @self.clear_all_deleted.clicked.connect
        def _():
            submit_sql(f"""
DELETE FROM tasks WHERE deleted == TRUE;
""")

        @self.delete_skill.clicked.connect
        def _():
            try:
                x = self.skills_table.selectedItems()[0].row()
            except IndexError:
                return

            skill_id = self.skills_table.item(x, 1).data(Qt.UserRole)
            name = self.skills_table.item(x, 1).text()

            mb = QMessageBox()
            mb.setText(f"Wirklich Fähigkeit '{name}' löschen?")
            mb.setInformativeText("Bitte bestätigen!")
            mb.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            mb.setDefaultButton(QMessageBox.No)

            if mb.exec_() == QMessageBox.Yes:
                submit_sql(f"""
DELETE FROM skills WHERE skill_id == {skill_id};
""")
                self.skills_table.removeRow(x)
                self.update()
        
        # SPACES

        @self.create_space.clicked.connect
        def _():
            text, okPressed = QtWidgets.QInputDialog.getText(self, 
                    "Neuer Space",
                    "Name des neuen Space", QtWidgets.QLineEdit.Normal, "")
            if okPressed and text != '':
                submit_sql(f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
""")
                self.build_spaces_table()

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
                submit_sql(f"""
DELETE FROM spaces WHERE space_id == {space_id};
""")
                self.spaces_table.removeRow(x)
                self.update()

        @self.spaces_table.itemSelectionChanged.connect
        def _():
            self.space_name.setEnabled(True)
            self.space_primary_activity.setEnabled(True)
            self.space_secondary_activity.setEnabled(True)
            self.space_priority.setEnabled(True)

            self.space_id = self.spaces_table.item(self.spaces_table.selectedItems()[0].row(), 0).data(Qt.UserRole)
            query = submit_sql(f"""
SELECT * from spaces where space_id = {self.space_id}
""")
            for row in iter_over(query):
                self.space_name.setText(row(1))
                self.space_priority.setValue(row(2))
                self.space_primary_activity.setCurrentIndex(
                        x if 
                        (x := self.space_primary_activity.findData(QVariant(row(3)))) != -1 
                        else 0)
                self.space_secondary_activity.setCurrentIndex(
                        x if 
                        (x := self.space_secondary_activity.findData(QVariant(row(4)))) != -1 
                        else 0)

        @self.space_name.textChanged.connect
        def space_name_changed():
            submit_sql(f"""
UPDATE spaces
SET name = '{self.space_name.toPlainText()}'
WHERE space_id = {self.space_id}
            """)
            self.spaces_table.item(self.spaces_table.selectedItems()[0].row(), 0).setText(self.space_name.toPlainText())

        @self.space_priority.valueChanged.connect
        def space_priority_changed():
            submit_sql(f"""
UPDATE spaces
SET priority = {self.space_priority.value()}
WHERE space_id = {self.space_id}
            """, debugging=True)

        @self.space_primary_activity.currentIndexChanged.connect
        def _():
            x = self.space_primary_activity.itemData(
                            self.space_primary_activity.currentIndex())
            submit_sql(f"""
UPDATE spaces
SET primary_activity_id = {x if x is not None else "NULL"}
WHERE space_id = {self.space_id}
"""
)

        @self.space_secondary_activity.currentIndexChanged.connect
        def _():
            x = self.space_secondary_activity.itemData(
                            self.space_secondary_activity.currentIndex())
            submit_sql(f"""
UPDATE spaces
SET secondary_activity_id = {x if x is not None else "NULL"}
WHERE space_id = {self.space_id}
"""
)

    def build_skill_table(self):
        query = submit_sql(f"""
        SELECT skill_id, name FROM skills;
        """)
        self.skills_table.setSortingEnabled(False)

        for i, row in enumerate(iter_over(query)):
            self.skills_table.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem()
            self.skills_table.setItem(i, 1, item)
            item.setText(row(1))
            # skill_id
            item.setData(Qt.UserRole, row(0))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.skills_table.setSortingEnabled(True)
        self.skills_table.sortItems(1)  # ? strange
        self.update()


    def build_spaces_table(self):
        query = submit_sql(f"""
        SELECT space_id, name FROM spaces;
        """)
        self.spaces_table.setSortingEnabled(False)

        for i, row in enumerate(iter_over(query)):
            self.spaces_table.setRowCount(i+1)
            item = QtWidgets.QTableWidgetItem(row(1))
            self.spaces_table.setItem(i, 0, item)
            item.setData(Qt.UserRole, row(0))
            item.setTextAlignment(QtCore.Qt.AlignCenter)

            inner_query = submit_sql(f"""
SELECT COUNT(*) FROM tasks WHERE space_id == {row(0)};
""")
            text = "0" if not inner_query.next() else str(inner_query.value(0))
            item = QtWidgets.QTableWidgetItem(text)
            self.spaces_table.setItem(i, 1, item)

        self.spaces_table.setSortingEnabled(True)
        self.spaces_table.sortItems(0)  # ? strange 

        query = submit_sql(f"""
        SELECT activity_id, name FROM activities;
        """)

        for i, row in enumerate(iter_over(query)):
            self.space_primary_activity.addItem(row(1), QVariant(row(0)))
            self.space_secondary_activity.addItem(row(1), QVariant(row(0)))
        self.update()
        
    def reject(self):
        super().reject()
        win_settings = None
        
class Attributions(QtWidgets.QDialog, attributions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.browser = QWebEngineView()
        with open('attributions.html', "r") as f:
            html = f.read()
        self.browser.setHtml(html)
        self.verticalLayout.addWidget(self.browser)
        
    def reject(self):
        super().reject()
        win_attributions = None

class Inventory(QtWidgets.QDialog, inventory.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
    def reject(self):
        super().reject()
        win_inventory = None

class Companions(QtWidgets.QDialog, companions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
    def reject(self):
        super().reject()
        win_companions = None

class Statistics(QtWidgets.QDialog, statistics.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        query = submit_sql(f"""
SELECT
    primary_activity_id,
    SUM(time_spent)
FROM
    tasks
GROUP BY
    primary_activity_id
""")
        activities = {row(0): row(1) for row in iter_over(query)}
        q(activities.items())
        if not activities:
            return

        query = submit_sql(f"""
SELECT
    activity_id, name, adjust_time_spent
FROM
    activities
""")

        for row in iter_over(query):
            activities[row(0)] += row(2)
        
    def reject(self):
        super().reject()
        win_statistics = None

class Landing(QtWidgets.QWizard, landing.Ui_Wizard):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
    def reject(self):
        super().reject()
        win_landing = None

class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent):
        super().__init__(icon, parent)
        menu = QtWidgets.QMenu()
        action = menu.addAction("Manage Aufgaben")
        self.setContextMenu(menu)
        menu.triggered.connect(self.liste)
        
    def liste(self):
        win = Task_List()
        list_of_task_lists.append(win)
        win.show()

class Application(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
    
    def mouseMoveEvent(self, event):
        global test
        event.ignore()
        return False
        #font = app.font()
        #font.setPointSize(font.pointSize() + 1)
        #app.setFont(font)

        # if QtGui.QApplication.keyboardModifiers() == Qt.ControlModifier:
        #     font = app.font()
        #     font.setPointSize(font.pointSize() + 1)
        #     app.setFont(font)

def consider_tasks():
    global considered_tasks
    query = submit_sql(f"""
        SELECT id FROM tasks
        WHERE deleted != TRUE AND draft != TRUE AND inactive != TRUE
        ;
        """)
    considered_tasks = [Task(row(0)) for row in iter_over(query)]

if __name__ == "__main__":
    q(46546, sys.argv)
    path = Path(__file__).resolve().parents[0]
    q(243234, path)
    # touch, just in case user killed the config or first start
    (path/"config.stay").touch()
    # overwriting the module with the instance for convenience
    config = config.read(path/"config.stay")

    seed((config.coin^config.lucky_num) * config.count)

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(config.database)
    query = QSqlQuery()
    classes.set_globals(config)

    if not db.open():
        q("Could not open DB!")

    
    if config.first_start:
        import first_start
        first_start.run(db, query, config)
        config.first_start = False
        config.write()
    
    if config.run_sql_stuff:
        config.run_sql_stuff = False
        config.write()
        # just in case..
        dbpath = path/config.database
        backup = path/(config.database + ".bak")
        backup.write_bytes(dbpath.read_bytes())  # nice way to copy a file
        import sql_stuff
    
    activity_color = {0: config.activity_color_body,
                    1: config.activity_color_mind,
                    2: config.activity_color_spirit,
                    }
    try: 
        from PyQt5.QtWinExtras import QtWin
        myappid = 'AGK.watnu.0.1.1'
        QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app = Application(sys.argv) 
    icon = QIcon(config.icon)
    win_main = MainWindow()
    win_main.setWindowIcon(icon)
    win_main.statusBar.show()
    win_main.statusBar.showMessage("Willkommen zurück! Lese Aufgaben ein...", 10000)
    considered_tasks = []
    consider_tasks()
    win_main.statusBar.showMessage("Bereit.", 10000)
    list_of_task_lists: list[Task_List] = []
    tasks = []
    win_what = None
    win_new = None
    win_character = None
    win_settings = None
    win_running = None
    win_attributions = None
    last_edited_space:str = None
    test = "..."  # TODO
        
    state = StateMachine(initial=S.init, name="Application State",
        states={S.init:{S.main},
                S.main:{S.final, S.running, S.editing},
                S.running: {S.main},
                S.editing: {S.main, S.final, S.editing}},
                
        enters={S.final:app.quit}
        )

    state.flux_to(S.main)
    timer = datetime 

    if not db.tables():
        config.first_start = True
        config.write()
        mb = QtWidgets.QMessageBox()
        state.flux_to(S.final)
        mb.setText("Found an empty DB. Everything has been reset. Shutting down - please restart!")
        mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/alert-triangle.svg"))
        mb.setWindowTitle("Hmm..")
        mb.exec_()
        sys.exit()

    win_main.show()
    if config.tutorial_active:
        win_landing = Landing()
        concluded = win_landing.exec_()
        if concluded:
            config.tutorial_active = False

    button = QWinTaskbarButton()
    button.setWindow(win_main.windowHandle())

    button.setOverlayIcon(icon)
    progress = button.progress()
    progress.setRange(0,100)
    tray = TrayIcon(icon, win_main)
    tray.show()

    sys.exit(app.exec_())
    