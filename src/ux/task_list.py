from datetime import datetime
from functools import partial
from itertools import count
from pathlib import Path
from random import choice, seed
from time import time, time_ns

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, QVariant
from PyQt6.QtGui import QFont, QFontDatabase, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

import ui
from classes import Task, typed
from logic import (
    filter_tasks_by_constraints,
    filter_tasks_by_content,
    filter_tasks_by_ilk,
    filter_tasks_by_space,
    filter_tasks_by_status,
    pipes,
    retrieve_tasks,
)
from stuff import app, config, db
from ux import task_editor, task_finished, task_running

_translate = QtCore.QCoreApplication.translate


class TaskList(QtWidgets.QDialog, ui.task_list.Ui_Dialog):
    def rearrange_list(self):
        self.arrange_list(
            list(filter_tasks_by_content(retrieve_tasks(), self.field_filter.text().casefold()))
        )
        self.update()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db_timer = QTimer()
        "Timer for polling if the db has changed and regenerate the list."
        self.db_timer.start(100)
        self.last_generated = 0
        self.tasks: list[Task] = []
        self.check_deadline.stateChanged.connect(self.rearrange_list)
        self.check_level.stateChanged.connect(self.rearrange_list)
        self.check_priority.stateChanged.connect(self.rearrange_list)
        self.check_space.stateChanged.connect(self.rearrange_list)

        @self.db_timer.timeout.connect
        def db_changed_check():
            if Path(config.db_path).stat().st_mtime > self.last_generated:
                self.build_task_list()

        def delete_item():
            selected: list[Task] = [x.data(Qt.ItemDataRole.UserRole) for x in self.task_list.selectedItems()]
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
                        for task in selected:
                            task.really_delete()
                    case _:
                        return
            else:
                for task in selected:
                    task.delete()
            self.build_task_list()

        QShortcut(QKeySequence(Qt.Key.Key_Delete), self).activated.connect(delete_item)

        def toggle_fullscreen():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(toggle_fullscreen)

        def build_space_list():
            self.space.clear()
            self.space.addItem("-- alle Räume --")
            self.space.setItemData(0, self.font, Qt.ItemDataRole.FontRole)
            query = db.execute(
                """
            SELECT space_id, name FROM spaces;
            """
            )
            for space_id, name in query.fetchall():
                self.space.addItem(typed(name, str), QVariant(typed(space_id, int)))

            self.space.model().sort(1, Qt.SortOrder.AscendingOrder)

        build_space_list()
        self.space.setCurrentIndex(config.last_selected_space)

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_list()
            config.last_selected_space = self.space.currentIndex()
            config.save()

        self.build_button1_menu()

        menu = QtWidgets.QMenu()
        menu.addAction("genau so", self.clone_as_is)
        menu.addAction("als Subtask", self.clone_as_sub)
        menu.addAction("als Supertask", self.clone_as_sup)
        self.button9.setMenu(menu)

        menu = QtWidgets.QMenu()

        def space_add():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self, "Neuer Space", "Name des neuen Space", QtWidgets.QLineEdit.EchoMode.Normal, ""
            )
            if okPressed and text != "":
                db.execute(
                    f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                )
                db.commit()
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
                        db.execute(
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
                win = list(filter(lambda w: w.task == task, app.list_of_task_editors))
                if win:
                    win[0].show()
                    win[0].raise_()
                    continue
                win = task_editor.Editor(task)
                app.list_of_task_editors.append(win)
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
            app.list_of_task_editors.append(win)
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
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-heads.svg"))
            else:
                mb.setText("Du hast Zahl geworfen!")
                mb.setIconPixmap(QtGui.QPixmap("extra/feathericons/coin-tails.svg"))
            mb.exec()

        @self.ilk.currentIndexChanged.connect
        def ilk_switched():
            self.build_task_list()

        @self.status.currentIndexChanged.connect
        def status_switched():
            self.build_button1_menu()
            self.build_task_list()

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.field_filter.textChanged.connect(lambda: QTimer.singleShot(1000, filter_changed))

        def filter_changed():
            self.arrange_list(
                list(filter_tasks_by_content(retrieve_tasks(), self.field_filter.text().casefold()))
            )
            self.update()

    def set_as_open(self):
        X = list(filter(lambda t: t.column() == 0, self.task_list.selectedItems()))

        if not X:
            return

        for x in X:
            task = self.task_list.item(x.row(), 0).data(Qt.ItemDataRole.UserRole)

            db.execute(
                f"""
UPDATE tasks
SET 'deleted' = False, 'done' = False, 'draft' = False, 'inactive' = False
WHERE id == {task.id}
"""
            )
            db.commit()

    def set_as(self, property: str, set_flag):
        X = list(filter(lambda t: t.column() == 0, self.task_list.selectedItems()))

        if not X:
            return

        for x in X:
            task: Task = self.task_list.item(x.row(), 0).data(Qt.ItemDataRole.UserRole)
            if property == "done" and set_flag:
                task_finished.Task_Finished(task).exec()
            else:
                db.execute(
                    f"""
UPDATE tasks
SET '{property}' = {set_flag}
WHERE id == {task.id}
"""
                )
        db.commit()
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


    def build_task_list(self):
        self.last_generated = time()

        self.selected_space = self.space.itemData(self.space.currentIndex())
        config.last_selected_space = self.selected_space or 0
        config.save()

        self.arrange_list(get_filtered_tasks(self))
        self.update()

    def arrange_list(self, tasks: list[Task]):
        """Needs to be extra, otherwise filtering would hit the DB repeatedly."""
        self.task_list.setStyleSheet(
            """
alternate-background-color: #bfffbf; 
background-color: #deffde;
font-size: 12pt;
        """
        )
        self.task_list.ensurePolished()
        self.task_list.setSortingEnabled(False)
        self.task_list.setRowCount(len(tasks))

        # displayed columns: tuple[Header, displayed, how to get value]
        columns = (
            ("space", self.check_space.isChecked(), lambda t: t.space),
            ("level", self.check_level.isChecked(), lambda t: t.level),
            ("priority", self.check_priority.isChecked(), lambda t: t.priority),
            ("deadline", self.check_deadline.isChecked(), lambda t: deadline_as_str(t.deadline)),
            ("do", True, lambda t: get_desc(t)),
        )

        ID = QFontDatabase.addApplicationFont("./extra/Fira_Sans/FiraSans-Regular.ttf")
        family = QFontDatabase.applicationFontFamilies(ID)
        item_font = QFont(family)
        header_font = QFont("Segoi UI")
        header_font.setBold(True)
        header_font.setPixelSize(10)

        self.task_list.setColumnCount(len(list(filter(lambda c: c[1], columns))))

        # TODO: use _translate
        translation = {
            "do": "Beschreibung",
            "space": "Raum",
            "level": "Level",
            "priority": "Priorität",
            "deadline": "Deadline",
        }

        for column_number, column in enumerate(filter(lambda c: c[1], columns)):
            self.set_header(translation[column[0]], header_font, column_number)

        for i, task in enumerate(tasks):
            for column_number, (header, displayed, func) in enumerate(filter(lambda c: c[1], columns)):
                content = str(func(task))
                item = QtWidgets.QTableWidgetItem(content)
                item.setFont(item_font)
                if column_number == 0:
                    item.setData(Qt.ItemDataRole.UserRole, task)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.task_list.setItem(i, column_number, item)

        self.task_list.setSortingEnabled(True)
        self.task_list.resizeColumnsToContents()
        self.task_list.ensurePolished()
        self.task_list.show()
        return tasks

    def set_header(self, text, font, column):
        item = QTableWidgetItem(text)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.task_list.setHorizontalHeaderItem(column, item)
        self.task_list.update()

    def build_button1_menu(self):
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
            case 5:  # all
                menu.addAction("offen", self.set_as_open)
                menu.addAction("Entwurf", partial(self.set_as, "draft", True))
                menu.addAction("inaktiv", partial(self.set_as, "inactive", True))
                menu.addAction("erledigt", partial(self.set_as, "done", True))
                menu.addAction("gelöscht", partial(self.set_as, "deleted", True))
        self.button1.setMenu(menu)

    def reject(self):
        super().reject()
        if app.win_running:
            app.win_running.show()
            app.win_running.raise_()
        else:
            app.win_main.show()
            app.win_main.raise_()

        app.list_of_task_lists.remove(self)


def get_desc(task):
    lines = task.do.split("\n")
    return lines[0] + ("" if len(lines) == 1 else " […]")


@pipes
def get_filtered_tasks(self):
    self.tasks = (
        retrieve_tasks(db)
        >> filter_tasks_by_status(self.status.currentIndex())
        >> filter_tasks_by_content(self.field_filter.text().casefold())
        >> filter_tasks_by_ilk(self.ilk.currentIndex())
        >> filter_tasks_by_space(self.selected_space)
        >> list
    )


def deadline_as_str(deadline) -> str:
    if deadline == float("inf"):
        return ""
    return str(datetime.fromtimestamp(deadline))
