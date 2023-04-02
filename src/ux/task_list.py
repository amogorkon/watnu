import contextlib
from datetime import datetime
from functools import partial
from itertools import count
from pathlib import Path
from random import choice, seed
from time import time, time_ns

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, QVariant
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

import ui
from classes import Task, typed, typed_row
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
from ux import choose_space, task_editor, task_finished, task_running

_translate = QtCore.QCoreApplication.translate

OK = QIcon("extra/check.svg")
NOK = QIcon("extra/cross.svg")


class TaskList(QtWidgets.QDialog, ui.task_list.Ui_Dialog):
    def rearrange_list(self):
        """Callback for easy rearranging of the list, no filtering."""
        self.arrange_list(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.update()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db_timer = QTimer()
        "Timer for polling if the db has changed and regenerate the list."
        self.db_timer.start(100)
        self.last_generated = 0

        self.tasks: list[Task] = []
        # to make it compatible with the rest of the code
        self.check_do = QtWidgets.QCheckBox()
        self.check_do.setChecked(True)

        # displayed columns: tuple[Header, displayed, how to get value]

        self.columns = (
            ("space", self.check_space, lambda t: str(t.space)),
            ("level", self.check_level, lambda t: str(t.level)),
            ("priority", self.check_priority, lambda t: str(t.priority)),
            ("deadline", self.check_deadline, lambda t: deadline_as_str(t.deadline)),
            ("done", self.check_done, lambda t: OK if t.done else NOK),
            ("draft", self.check_draft, lambda t: OK if t.draft else NOK),
            ("inactive", self.check_inactive, lambda t: OK if t.inactive else NOK),
            ("deleted", self.check_deleted, lambda t: OK if t.deleted else NOK),
            ("do", self.check_do, lambda t: get_desc(t)),
        )

        for _, check, _ in self.columns:
            check.stateChanged.connect(self.rearrange_list)

        @self.db_timer.timeout.connect
        def db_changed_check():
            if Path(config.db_path).stat().st_mtime > self.last_generated:
                self.build_task_list()

        def delete_item():
            if not (selected := self.get_selected_tasks()):
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

        build_space_list(self)
        self.space.setCurrentIndex(
            x if (x := self.space.findText(app.last_edited_space or config.last_selected_space)) > -1 else 0
        )

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_list()
            config.last_selected_space = self.space.currentText() or ""
            config.save()

        self.build_button1_menu()

        menu = QtWidgets.QMenu()
        menu.addAction("genau so", self.clone_as_is)
        menu.addAction("als Subtask", self.clone_as_sub)
        menu.addAction("als Supertask", self.clone_as_sup)
        self.button9.setMenu(menu)

        menu = QtWidgets.QMenu()

        def space_set():
            match (win := choose_space.Space_Selection()).exec():
                case QtWidgets.QDialog.DialogCode.Accepted:
                    space = get_space_id(win.space.currentText(), win.space.currentIndex())
                case _:  # Cancelled
                    return
            for task in (selected := self.get_selected_tasks()):
                task.set_("space_id", space)
            self.build_task_list()
            self.statusBar.showMessage(
                f"Raum für {len(selected)} Aufgabe{'' if len(selected) == 1 else 'n'} gesetzt.", 5000
            )

        menu.addAction("für ausgewählte Aufgaben setzen", space_set)

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
                self.statusBar.showMessage(f"Raum '{text}' hinzugefügt.", 5000)
                for win in app.list_of_task_editors:
                    build_space_list(win)
                for win in app.list_of_task_lists:
                    build_space_list(win)

        menu.addAction("hinzufügen", space_add)

        def space_delete():
            space_name = self.space.currentText()
            if self.task_list.rowCount() > 0:
                QtWidgets.QMessageBox.information(
                    self,
                    "Sorry..",
                    f"Der Raum '{space_name}' ist nicht leer und kann daher nicht gelöscht werden.",
                )
            else:
                match QtWidgets.QMessageBox.question(
                    self,
                    "Wirklich den ausgewählten Raum löschen?",
                    f"Soll der Raum '{space_name}' wirklich gelöscht werden?",
                ):
                    case QtWidgets.QMessageBox.StandardButton.Yes:
                        db.execute(
                            f"""
DELETE FROM spaces where name=='{space_name}'
"""
                        )
                        db.commit()
                        self.statusBar.showMessage(f"Raum '{space_name}' gelöscht.", 5000)
                        for win in app.list_of_task_lists:
                            build_space_list(win)
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_editors:
                            build_space_list(win)
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)

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

        def button2_clicked():
            selected = self.get_selected_tasks()
            match self.status.currentIndex():
                # open
                case 0:
                    for task in selected:
                        task.set_("done", True)
                # draft
                case 1:
                    for task in selected:
                        task.set_("draft", False)
                # inactive
                case 2:
                    for task in selected:
                        task.set_("inactive", False)
                # done
                case 3:
                    for task in selected:
                        task.set_("done", False)
                # deleted
                case 4:
                    for task in selected:
                        task.set_("deleted", False)
                # all
                case 5:
                    pass
            self.build_task_list()

        QShortcut(QKeySequence(Qt.Key.Key_2), self.task_list).activated.connect(button2_clicked)
        self.button2.clicked.connect(button2_clicked)

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
            self.button2.setEnabled(True)
            match self.status.currentIndex():
                # open
                case 0:
                    self.button2.setText("Erledigt!")
                # draft
                case 1:
                    self.button2.setText("kein Entwurf")
                # inactive
                case 2:
                    self.button2.setText("Aktivieren")
                # done
                case 3:
                    self.button2.setText("doch nicht erledigt")
                # deleted
                case 4:
                    self.button2.setText("wiederherstellen")
                # all
                case 5:
                    self.button2.setEnabled(False)
                    self.button2.setText("")

            self.build_button1_menu()
            self.build_task_list()

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.field_filter.textChanged.connect(lambda: QTimer.singleShot(1000, filter_changed))

        def filter_changed():
            self.arrange_list(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
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
        """Prepare for filtering the tasks, then fetch and display them."""

        self.last_generated = time()

        config.last_selected_space = self.space.currentText() or ""
        config.save()
        self.tasks = get_filtered_tasks(self)

        self.arrange_list(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.update()

    def arrange_list(self, tasks: list[Task]):
        """Arrange the tasks in the list for display."""
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

        ID = QFontDatabase.addApplicationFont("./extra/Fira_Sans/FiraSans-Regular.ttf")
        family = QFontDatabase.applicationFontFamilies(ID)
        item_font = QFont(family)
        header_font = QFont("Segoi UI")
        header_font.setBold(True)
        header_font.setPixelSize(10)

        self.task_list.setColumnCount(len(list(filter(lambda c: c[1].isChecked(), self.columns))))

        # TODO: use _translate
        translation = {
            "do": "Beschreibung",
            "space": "Raum",
            "level": "Level",
            "priority": "Priorität",
            "deadline": "Deadline",
            "done": "Erledigt",
            "draft": "Entwurf",
            "inactive": "Inaktiv",
            "deleted": "Gelöscht",
        }
        selected_columns = list(filter(lambda c: c[1].isChecked(), self.columns))

        for column_number, column in enumerate(selected_columns):
            self.set_header(translation[column[0]], header_font, column_number)

        for i, task in enumerate(tasks):
            for column_number, (header, displayed, func) in enumerate(selected_columns):
                content = func(task)
                if isinstance(content, str):
                    item = QtWidgets.QTableWidgetItem(content)
                    item.setFont(item_font)
                    item.setData(Qt.ItemDataRole.UserRole, task)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                if isinstance(content, QIcon):
                    item = QtWidgets.QTableWidgetItem()
                    item.setIcon(content)
                self.task_list.setItem(i, column_number, item)

        self.task_list.setSortingEnabled(True)
        self.task_list.resizeColumnsToContents()
        self.task_list.ensurePolished()
        self.task_list.show()

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

    def get_selected_tasks(self) -> list[Task]:
        return [
            self.task_list.item(row, 0).data(Qt.ItemDataRole.UserRole)
            for row in range(self.task_list.rowCount())
            if self.task_list.item(row, 0).isSelected()
        ]


def get_desc(task):
    lines = task.do.split("\n")
    return lines[0] + ("" if len(lines) == 1 else " […]")


def get_space_id(name, index) -> int | None:
    return (
        typed_row(
            db.execute(
                """
                SELECT space_id FROM spaces WHERE name=?;
                """,
                (name,),
            ).fetchone(),
            0,
            int | None,
        )
        if index
        else None
    )


@pipes
def get_filtered_tasks(self):
    """Filter tasks according to the current filter settings."""
    return (
        retrieve_tasks(db)
        >> filter_tasks_by_space(get_space_id(self.space.currentText(), self.space.currentIndex()))
        >> filter_tasks_by_status(self.status.currentIndex())
        >> filter_tasks_by_ilk(self.ilk.currentIndex())
        >> list
    )


def deadline_as_str(deadline) -> str:
    if deadline == float("inf"):
        return ""
    return str(datetime.fromtimestamp(deadline))


def build_space_list(parent):
    parent.space.clear()
    parent.space.addItem("-- alle Räume --")
    parent.space.setItemData(0, parent.font, Qt.ItemDataRole.FontRole)
    query = db.execute(
        """
    SELECT space_id, name FROM spaces;
    """
    )
    for space_id, name in query.fetchall():
        parent.space.addItem(typed(name, str), QVariant(typed(space_id, int)))

    parent.space.model().sort(1, Qt.SortOrder.AscendingOrder)
