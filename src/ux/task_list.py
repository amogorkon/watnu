import contextlib
import webbrowser
from datetime import datetime
from functools import partial
from itertools import count
from pathlib import Path
from random import choice, seed
from time import time, time_ns

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QKeyCombination, Qt, QTimer, QVariant
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
from ux import choose_space, space_editor, task_editor, task_finished, task_organizer, task_running

_translate = QtCore.QCoreApplication.translate

from beartype import beartype

OK = QIcon(str(config.base_path / "src/extra/check.svg"))
NOK = QIcon(str(config.base_path / "src/extra/cross.svg"))


class TaskList(QtWidgets.QDialog, ui.task_list.Ui_Dialog):
    def rearrange_list(self):
        """Callback for easy rearranging of the list, no filtering."""
        self.arrange_table(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
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
            ("priority", self.check_priority, lambda t: str(t.total_priority)),
            ("deadline", self.check_deadline, lambda t: deadline_as_str(t.deadline)),
            ("done", self.check_done, lambda t: OK if t.done else NOK),
            ("draft", self.check_draft, lambda t: OK if t.draft else NOK),
            ("inactive", self.check_inactive, lambda t: OK if t.inactive else NOK),
            ("deleted", self.check_deleted, lambda t: OK if t.deleted else NOK),
            ("do", self.check_do, lambda t: t.get_short_do()),
        )

        for _, check, _ in self.columns:
            check.stateChanged.connect(self.rearrange_list)

        @self.db_timer.timeout.connect
        def db_changed_check():
            if Path(config.db_path).stat().st_mtime > self.last_generated:
                self.build_task_table()

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

        QShortcut(QKeySequence(Qt.Key.Key_Delete), self).activated.connect(delete_item)

        def toggle_fullscreen():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(toggle_fullscreen)

        QShortcut(
            QKeySequence(
                QKeyCombination(Qt.Modifier.CTRL, Qt.Key.Key_F),
            ),
            self,
        ).activated.connect(lambda: self.field_filter.setFocus())

        build_space_list(self)
        self.space.setCurrentIndex(
            x if (x := self.space.findText(app.last_edited_space or config.last_selected_space)) > -1 else 0
        )

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_table()
            config.last_selected_space = self.space.currentText() or ""
            config.save()

        self.build_button1_menu()

        def create_task():
            win = task_editor.Editor(current_space=self.space.currentText())
            app.list_of_task_editors.append(win)
            app.list_of_windows.append(win)
            win.show()

        menu = QtWidgets.QMenu()

        menu.addAction("neu", create_task)
        menu.addAction("als Klon", self.clone_as_is)
        menu.addAction("kloniert als Subtask", self.clone_as_sub)
        menu.addAction("kloniert als Supertask", self.clone_as_sup)
        self.button6.setMenu(menu)

        menu = QtWidgets.QMenu()

        def space_set():
            match (win := choose_space.Space_Selection()).exec():
                case QtWidgets.QDialog.DialogCode.Accepted:
                    space = get_space_id(win.space.currentText(), win.space.currentIndex())
                case _:  # Cancelled
                    return
            for task in (selected := self.get_selected_tasks()):
                task.set_("space_id", space)
            self.build_task_table()
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
            if self.task_table.rowCount() > 0:
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
                        for win in app.list_of_task_organizers:
                            build_space_list(win)
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)

        menu.addAction("löschen", space_delete)

        def space_edit():
            space_editor.Space_Editor(self.space.currentText()).exec()

        menu.addAction("bearbeiten", space_edit)

        self.button9.setMenu(menu)

        item = QtWidgets.QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable)
        self.task_table.setVerticalHeaderItem(0, item)

        self.build_task_table()

        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.layout.addWidget(self.statusBar)
        self.update()

        @self.task_table.cellDoubleClicked.connect
        def task_list_doubleclicked(row, column):
            self.edit_selected()

        @self.button1.clicked.connect
        def _():
            pass

        def button2_clicked():
            selected = self.get_selected_tasks()
            for task in selected:
                if task is None:
                    continue
                match self.status.currentIndex():
                    # open
                    case 0:
                        task.set_("done", True)
                    # draft
                    case 1:
                        task.set_("draft", False)
                    # inactive
                    case 2:
                        task.set_("inactive", False)
                    # done
                    case 3:
                        task.set_("done", False)
                    # deleted
                    case 4:
                        task.set_("deleted", False)
                    # all
                    case 5:
                        pass
            self.build_task_table()

        QShortcut(QKeySequence(Qt.Key.Key_2), self.task_table).activated.connect(button2_clicked)
        self.button2.clicked.connect(button2_clicked)

        @self.button3.clicked.connect
        def _():
            selected = self.get_selected_tasks()
            if not selected:
                win = task_organizer.Organizer()
                app.list_of_task_organizers.append(win)
                app.list_of_windows.append(win)
                win.show()
                return

            for task in selected:
                for win in app.list_of_task_organizers:
                    if win.task == task:
                        win.show()
                        win.raise_()
                        break
                else:
                    win = task_organizer.Organizer(task)
                    app.list_of_task_organizers.append(win)
                    app.list_of_windows.append(win)
                    win.show()

        @self.button4.clicked.connect
        def button4_clicked():
            self.edit_selected()

        @self.button5.clicked.connect
        def start_task():
            selected = self.get_selected_tasks()

            if not selected:
                return
            elif len(selected) > 1:
                self.statusBar.showMessage("Es kann jeweils nur eine Aufgabe gestartet werden.", 5000)
                return
            else:
                self.hide()
                task_running.Running(selected[0])

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
            self.build_task_table()

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
            self.build_task_table()

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.field_filter.textChanged.connect(lambda: QTimer.singleShot(1000, filter_changed))

        def filter_changed():
            self.arrange_table(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
            self.update()

    def set_as_open(self):
        selected = self.get_selected_tasks()
        if not selected:
            return

        for task in selected:
            db.execute(
                f"""
UPDATE tasks
SET 'deleted' = False, 'done' = False, 'draft' = False, 'inactive' = False
WHERE id == {task.id}
"""
            )
            db.commit()

    def set_as(self, property: str, set_flag):
        selected = self.get_selected_tasks()

        if not selected:
            return

        for task in selected:
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
        self.build_task_table()

    def clone_as_is(self):
        try:
            x = self.task_table.selectedItems()[0].row()
        except IndexError:
            return

        task = self.task_table.item(x, 0).data(Qt.ItemDataRole.UserRole)
        win = task_editor.Editor(task, cloning=True, as_sup=0)
        win.show()

    def clone_as_sub(self):

        try:
            x = self.task_table.selectedItems()[0].row()
        except IndexError:
            return

        task = self.task_table.item(x, 0).data(Qt.ItemDataRole.UserRole)
        win = task_editor.Editor(task, cloning=True, as_sup=-1)
        win.show()

    def clone_as_sup(self):
        try:
            x = self.task_table.selectedItems()[0].row()
        except IndexError:
            return

        task = self.task_table.item(x, 0).data(Qt.ItemDataRole.UserRole)
        win = task_editor.Editor(task, cloning=True, as_sup=1)
        win.show()

    def build_task_table(self):
        """Prepare for filtering the tasks, then fetch and display them."""

        self.last_generated = time()

        config.last_selected_space = self.space.currentText() or ""
        config.save()
        self.tasks = get_filtered_tasks(self)

        self.arrange_table(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.update()

    def arrange_table(self, tasks: list[Task]):
        """Arrange the tasks in the list for display."""
        self.task_table.setStyleSheet(
            """
alternate-background-color: #bfffbf; 
background-color: #deffde;
font-size: 12pt;
        """
        )
        self.task_table.ensurePolished()
        self.task_table.setSortingEnabled(False)
        self.task_table.setRowCount(len(tasks))

        ID = QFontDatabase.addApplicationFont("./extra/Fira_Sans/FiraSans-Regular.ttf")
        family = QFontDatabase.applicationFontFamilies(ID)
        item_font = QFont(family)
        header_font = QFont("Segoi UI")
        header_font.setBold(True)
        header_font.setPixelSize(10)

        self.task_table.setColumnCount(len(list(filter(lambda c: c[1].isChecked(), self.columns))))

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

        currently_selected_rows = self.task_table.selectionModel()

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
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if isinstance(content, QIcon):
                    item = QtWidgets.QTableWidgetItem()
                    item.setIcon(content)
                self.task_table.setItem(i, column_number, item)

        self.task_table.setSortingEnabled(True)
        self.task_table.resizeColumnsToContents()
        self.task_table.ensurePolished()
        self.task_table.setSelectionModel(currently_selected_rows)

        self.task_table.show()

    def set_header(self, text, font, column):
        item = QTableWidgetItem(text)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.task_table.setHorizontalHeaderItem(column, item)
        self.task_table.update()

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

    def edit_selected(self):
        for task in self.get_selected_tasks():
            for win in app.list_of_task_editors:
                if win.task == task:
                    win.show()
                    win.raise_()
                    break
            else:
                win = task_editor.Editor(task)
                app.list_of_task_editors.append(win)
                app.list_of_windows.append(win)
                win.show()
                win.raise_()

    def reject(self):
        super().reject()
        app.list_of_task_lists.remove(self)
        app.list_of_windows.remove(self)
        if app.win_running:
            app.win_running.show()
            app.win_running.raise_()
            return
        for win in app.list_of_windows:
            win.show()
            win.raise_()

    def get_selected_tasks(self) -> set[Task]:
        return {
            self.task_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            for row in range(self.task_table.rowCount())
            if (x := self.task_table.item(row, 0).isSelected()) and x is not None
        }

    def share_via_telegram(self, task):
        text = task.do
        url = ""
        webbrowser.open(f"https://t.me/share/url?url={url}&text={text}")

    def notify_windows_of_task_deletion(self, task):
        for win in app.list_of_task_lists:
            win.build_task_list()
        for win in app.list_of_task_organizers:
            win.build_task_list()
            win.subtasks.remove
            win.arrange_sub_sup_task_table()


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


def deadline_as_str(deadline: float) -> str:
    if deadline == float("inf"):
        return ""
    try:
        return str(datetime.fromtimestamp(deadline))
    except OSError:
        print(deadline, type(deadline))
        return ""


def build_space_list(parent, first_item_text="alle Räume") -> None:
    parent.space.clear()
    parent.space.addItem(first_item_text, QVariant(None))
    # set font of first item to bold
    # parent.space.setItemData(0, QFont("Arial", 10, QFont.setBold(True)), Qt.FontRole)

    parent.space.insertSeparator(1)

    query = db.execute(
        """
    SELECT space_id, name FROM spaces;
    """
    )
    spaces = query.fetchall()

    def number_of_tasks_in_space(item):
        space_id = item[0]
        return db.execute(
            """
            SELECT COUNT(*) FROM tasks WHERE space_id=?;
            """,
            (space_id,),
        ).fetchone()[0]

    sorted_spaces_by_number = sorted(spaces, key=number_of_tasks_in_space, reverse=True)

    for space_id, name in sorted_spaces_by_number[:3]:
        parent.space.addItem(typed(name, str), QVariant(typed(space_id, int)))

    parent.space.insertSeparator(5)

    sorted_spaces_by_name = sorted(sorted_spaces_by_number[3:], key=lambda x: x[1].casefold())
    for space_id, name in sorted_spaces_by_name:
        parent.space.addItem(typed(name, str), QVariant(typed(space_id, int)))
