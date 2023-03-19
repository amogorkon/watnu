from datetime import datetime
from functools import partial
from itertools import count
from math import isinf
from pathlib import Path
from random import choice, seed
from time import time, time_ns

import use
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, QVariant
from PyQt6.QtGui import QFont, QFontDatabase, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

import q
import ui
from logic import filter_tasks
from classes import Task, cached_and_invalidated, iter_over, submit_sql, typed
from ux import task_editor, task_finished, task_running

from .stuff import app, config, db


class TaskList(QtWidgets.QDialog, ui.task_list.Ui_Dialog):
    def __init__(self):
        self.task_list: QtWidgets.QTableWidget
        self.status: QtWidgets.QComboBox
        super().__init__()
        self.setupUi(self)
        self.timer = QTimer()
        "Timer for polling if the db has changed and regenerate the list."
        self.timer.start(100)
        self.last_generated = 0

        @self.timer.timeout.connect
        def db_changed_check():
            if Path(config.db_path).stat().st_mtime > self.last_generated:
                self.build_task_list()

        def delete_item():
            selected = self.task_list.selectedItems()
            if not selected:
                return
            # if we are dealing with tasks in the bin, we need to ask if we want to delete permanently
            if self.status.currentIndex() == 4:
                match QMessageBox.question(
                    self,
                    f"Aufgabe{'' if len(selected) == 1 else 'n'} löschen",
                    "Wirklich - unwiderruflich - löschen?",
                ):
                    case QMessageBox.StandardButton.Yes:
                        pass
                    case _:
                        return
            for x in selected:
                task: Task = x.data(Qt.ItemDataRole.UserRole)
                task.delete()
            self.build_task_list()

        QShortcut(QKeySequence(Qt.Key.Key_Delete), self).activated.connect(delete_item)

        self.task_list.setStyleSheet("alternate-background-color: #bfffbf; background-color: #deffde;")

        def build_space_list():
            self.space.clear()
            query = submit_sql(
                """
            SELECT space_id, name FROM spaces;
            """
            )
            for row in iter_over(query):
                space_id = typed(row, 0, int)
                space_name = typed(row, 1, str)
                self.space.addItem(space_name, QVariant(space_id))

            self.space.model().sort(1, Qt.SortOrder.AscendingOrder)

        build_space_list()
        self.space.setCurrentIndex(config.last_selected_space)

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_list()
            config.last_selected_space = self.space.currentIndex()
            config.write()

        self.tasks = []

        menu = QtWidgets.QMenu()
        menu.addAction("genau so", self.clone_as_is)
        menu.addAction("als Subtask", self.clone_as_sub)
        menu.addAction("als Supertask", self.clone_as_sup)
        self.button9.setMenu(menu)

        menu = QtWidgets.QMenu()
        menu.addAction("erledigt", partial(self.set_as, "done", True))
        menu.addAction("Entwurf", partial(self.set_as, "draft", True))
        menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
        menu.addAction("gelöscht", partial(self.set_as, "deleted", True))
        self.button1.setMenu(menu)

        menu = QtWidgets.QMenu()

        def space_add():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self, "Neuer Space", "Name des neuen Space", QtWidgets.QLineEdit.EchoMode.Normal, ""
            )
            if okPressed and text != "":
                submit_sql(
                    f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                )
            build_space_list()

        menu.addAction("hinzufügen", space_add)

        def space_delete():
            space_name = self.space.currentText()
            if self.task_list.rowCount() > 0:
                QtWidgets.QMessageBox.information(
                    self, f"Der Raum '{space_name}' ist nicht leer und kann daher nicht gelöscht werden."
                )
            else:
                match QtWidgets.QMessageBox.question(
                    "Wirklich den ausgewählten Raum löschen?",
                    f"Soll der Raum '{space_name}' wirklich gelöscht werden?",
                ):
                    case QtWidgets.QMessageBox.StandardButton.Yes:
                        submit_sql(
                            f"""
DELETE FROM spaces where name=='{space_name}'
"""
                        )
                        app.win_settings.statusbar.showMessage(f"Raum '{space_name}' gelöscht.")

        menu.addAction("löschen", space_delete)
        self.button7.setMenu(menu)

        item = QtWidgets.QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable)
        self.task_list.setVerticalHeaderItem(0, item)

        self.build_task_list()

        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.layout.addWidget(self.statusBar)
        self.update()

        @self.task_list.cellDoubleClicked.connect
        def task_list_doubleclicked(row, column):
            task = self.task_list.item(row, 0).data(Qt.ItemDataRole.UserRole)

            win = task_editor.Editor(task)
            win.show()

        @self.button1.clicked.connect
        def _():
            pass

        @self.button2.clicked.connect
        def _():
            pass

        @self.button3.clicked.connect
        def _():
            pass

        @self.button4.clicked.connect
        def edit_task():
            X: list[QTableWidgetItem] = list(
                filter(lambda t: t.column() == 0, self.task_list.selectedItems())
            )

            for x in X:
                task = self.task_list.item(x.row(), 0).data(Qt.ItemDataRole.UserRole)
                win = list(filter(lambda w: w.task == task, app.list_of_editors))
                if win:
                    win[0].show()
                    win[0].raise_()
                    continue
                win = task_editor.Editor(task)
                app.list_of_editors.append(win)
                win.show()

        @self.button5.clicked.connect
        def start_task():
            X = list(filter(lambda t: t.column() == 0, self.task_list.selectedItems()))

            if not X:
                return
            elif len(X) > 1:
                self.statusBar.showMessage("Es kann jeweils nur eine Aufgabe gestartet werden.", 5000)
                return
            else:
                x = X[0].row()
                task = self.task_list.item(x, 0).data(Qt.ItemDataRole.UserRole)
                self.hide()
                task_running.Running(task)

        @self.button6.clicked.connect
        def create_task():
            win = task_editor.Editor(current_space=self.space.currentText())
            app.list_of_editors.append(win)
            win.show()

        @self.button8.clicked.connect
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
            q("threw", i, "pairs!")

            # bitshift to the left
            config.coin <<= 1
            # then set the bit -
            config.coin |= first
            seed((config.coin ^ config.lucky_num) * config.count)

            x = choice(["Kopf", "Zahl"])
            mb = QtWidgets.QMessageBox()
            mb.setWindowTitle("Hmm..")
            if x == "Kopf":
                mb.setText("Du hast Kopf geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-heads.svg"))
            else:
                mb.setText("Du hast Zahl geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-tails.svg"))
            mb.exec()

        @self.status.currentIndexChanged.connect
        def status_switched():
            menu = QtWidgets.QMenu()
            match self.status.currentIndex():
                case 0:  # open
                    menu.addAction("Entwurf", partial(self.set_as, "draft", True))
                    menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
                    menu.addAction("erledigt", partial(self.set_as, "done", True))
                    menu.addAction("gelöscht", partial(self.set_as, "deleted", True))
                case 1:  # draft
                    menu.addAction("offen", self.set_as_open)
                    menu.addAction("kein Entwurf", partial(self.set_as, "draft", False))
                    menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
                    menu.addAction("erledigt", partial(self.set_as, "done", True))
                    menu.addAction("gelöscht", partial(self.set_as, "deleted", True))
                case 2:  # inactive
                    menu.addAction("offen", self.set_as_open)
                    menu.addAction("Entwurf", partial(self.set_as, "draft", True))
                    menu.addAction("nicht inaktiv", partial(self.set_as, "inactive", False))
                    menu.addAction("erledigt", partial(self.set_as, "done", True))
                    menu.addAction("gelöscht", partial(self.set_as, "deleted", True))

                case 3:  # done
                    menu.addAction("offen", self.set_as_open)
                    menu.addAction("Entwurf", partial(self.set_as, "draft", True))
                    menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
                    menu.addAction("nicht erledigt", partial(self.set_as, "done", False))
                    menu.addAction("gelöscht", partial(self.set_as, "deleted", True))
                case 4:  # deleted
                    menu.addAction("offen", self.set_as_open)
                    menu.addAction("Entwurf", partial(self.set_as, "draft", True))
                    menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
                    menu.addAction("erledigt", partial(self.set_as, "done", True))
                    menu.addAction("nicht gelöscht", partial(self.set_as, "deleted", False))
            self.button1.setMenu(menu)
            self.build_task_list()

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.filter_timer = QTimer()
        "Timer to give the user 1 sec to finish typing their filter query."

        @self.field_filter.textChanged.connect
        def field_filter_changed():
            self.filter_timer.start(1000)

        @self.filter_timer.timeout.connect
        def filter_changed():
            self.arrange_list(filter_tasks(self.tasks, self.field_filter.text().casefold()))
            self.update()
            self.filter_timer.stop()

    def set_as_open(self):
        X = list(filter(lambda t: t.column() == 0, self.task_list.selectedItems()))

        if not X:
            return

        for x in X:
            task = self.task_list.item(x.row(), 0).data(Qt.ItemDataRole.UserRole)

            submit_sql(
                f"""
UPDATE tasks
SET 'deleted' = False, 'done' = False, 'draft' = False, 'inactive' = False
WHERE id == {task.id}
"""
            )

    def set_as(self, property: str, set_flag):
        X = list(filter(lambda t: t.column() == 0, self.task_list.selectedItems()))

        if not X:
            return

        for x in X:
            task = self.task_list.item(x.row(), 0).data(Qt.ItemDataRole.UserRole)
            if property == "done" and set_flag:
                task_finished.Task_Finished(task).exec()
            else:
                submit_sql(
                    f"""
UPDATE tasks
SET '{property}' = {set_flag}
WHERE id == {task.id}
"""
                )
        self.build_task_list()

    def clone_as_is(self):
        try:
            x = self.task_list.selectedItems()[0].row()
        except IndexError:
            return

        task = self.task_list.item(x, 0).data(Qt.ItemDataRole.UserRole)
        win = task_editor.Editor(task, cloning=True, as_sup=0)
        win.show()

    def clone_as_sub(self):

        try:
            x = self.task_list.selectedItems()[0].row()
        except IndexError:
            return

        task = self.task_list.item(x, 0).data(Qt.ItemDataRole.UserRole)
        win = task_editor.Editor(task, cloning=True, as_sup=-1)
        win.show()

    def clone_as_sup(self):
        try:
            x = self.task_list.selectedItems()[0].row()
        except IndexError:
            return

        task = self.task_list.item(x, 0).data(Qt.ItemDataRole.UserRole)
        win = task_editor.Editor(task, cloning=True, as_sup=1)
        win.show()

    @cached_and_invalidated
    def build_task_list(self):
        self.last_generated = time()

        selected_space = self.space.itemData(self.space.currentIndex())
        if self.status.currentIndex() == 0:
            query = submit_sql(
                f"""
SELECT id FROM tasks
WHERE
done == FALSE AND
deleted == FALSE AND
draft == FALSE AND
inactive == FALSE
{f"AND space_id == {selected_space}" if selected_space else ""}
"""
            )
        if self.status.currentIndex() == 1:
            query = submit_sql(
                f"""
SELECT id FROM tasks 
WHERE 
draft == TRUE
{f"AND space_id == {selected_space}" if selected_space else ""}
"""
            )
        if self.status.currentIndex() == 2:
            query = submit_sql(
                f"""
SELECT id FROM tasks 
WHERE 
inactive == TRUE
{f"AND space_id == {selected_space}" if selected_space else ""}
"""
            )
        if self.status.currentIndex() == 3:
            query = submit_sql(
                f"""
SELECT id FROM tasks 
WHERE 
done == TRUE
{f"AND space_id == {selected_space}" if selected_space else ""}
"""
            )
        if self.status.currentIndex() == 4:
            query = submit_sql(
                f"""
SELECT id FROM tasks 
WHERE 
deleted == TRUE
{f"AND space_id == {selected_space}" if selected_space else ""}
"""
            )

        self.tasks = [Task(typed(row, 0, int)) for row in iter_over(query)]
        filter_text = self.field_filter.text().casefold()
        self.arrange_list(filter_tasks(self.tasks, filter_text))
        self.update()

    def reject(self):
        super().reject()
        if app.win_running:
            app.win_running.show()
            app.win_running.raise_()
        else:
            app.win_main.show()
            app.win_main.raise_()

        app.list_of_task_lists.remove(self)

    @use.woody_logger
    def arrange_list(self, tasks):
        """Needs to be extra, otherwise filtering would hit the DB repeatedly."""
        self.task_list.hide()
        self.task_list.clear()

        self.task_list.setSortingEnabled(False)
        self.task_list.setRowCount(len(tasks))
        ID = QFontDatabase.addApplicationFont("./extra/Fira_Sans/FiraSans-Regular.ttf")
        family = QFontDatabase.applicationFontFamilies(ID)
        font = QFont(family)

        # self.displayed_columns -> tuple of displayed columns
        displayed = (False, False, False, False)
        match displayed:
            case _:
                self.task_list.setColumnCount(1)
                item = QTableWidgetItem("Beschreibung")
                item.setFont(font)

                self.task_list.setHorizontalHeaderItem(0, item)

                for i, task in enumerate(tasks):
                    lines = task.do.split("\n")
                    desc = lines[0] + ("" if len(lines) == 1 else " […]")
                    item = QtWidgets.QTableWidgetItem(desc)
                    item.setFont(font)
                    item.setToolTip(task.space)
                    item.setData(Qt.ItemDataRole.UserRole, task)
                    self.task_list.setItem(i, 0, item)

            # item = QtWidgets.QTableWidgetItem(str(task.level))
            # self.task_list.setItem(i, 1, item)
            # item = QtWidgets.QTableWidgetItem(str(task.priority))
            # self.task_list.setItem(i, 2, item)
            # item = QtWidgets.QTableWidgetItem(
            #     "---" if isinf(task.deadline) else datetime.fromtimestamp(task.deadline).isoformat()
            # )
            # self.task_list.setItem(i, 4, item)

        if not tasks:
            self.task_list.clearContents()
            self.task_list.setRowCount(0)
        self.task_list.setSortingEnabled(True)
        self.task_list.resizeColumnsToContents()
        self.task_list.show()
