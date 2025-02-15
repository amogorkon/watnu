import urllib
import webbrowser
from functools import partial
from itertools import product
from pathlib import Path
from time import time

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QKeyCombination, QStringListModel, Qt, QTimer
from PyQt6.QtGui import (
    QFont,
    QGuiApplication,
    QIcon,
    QKeySequence,
    QShortcut,
)
from PyQt6.QtWidgets import (
    QCompleter,
    QListWidget,
    QMessageBox,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import src.ui as ui
from src import app, config, db
from src.classes import Task
from src.logic import filter_tasks_by_content
from src.ux import (
    choose_skills,
    choose_space,
    space_editor,
    task_editor,
    task_finished,
    task_organizer,
    task_running,
)
from src.ux_helpers import (
    SpaceMixin,
    deadline_as_str,
    filter_tasks,
    get_space_id,
)

_translate = QtCore.QCoreApplication.translate


def init_():
    global OK, NOK, status_icons
    OK = QIcon(str(config.base_path / "extra/check.svg"))
    NOK = QIcon(str(config.base_path / "extra/cross.svg"))

    status_icons = {
        C: QIcon(str(config.base_path / f"extra/status_icons/{''.join(str(int(x)) for x in C)}.svg"))
        for C in list(product([True, False], repeat=4))
    }


class Checklist(QWidget):
    """Must be a separate class because you can only setWindowFlags on top-level widgets."""

    def __init__(self, tasklist, column_names: list[QtWidgets.QCheckBox]):
        super().__init__()
        init_()
        self.setWindowFlags(Qt.WindowType.Popup | QtCore.Qt.WindowType.FramelessWindowHint)

        self.checkboxes = QListWidget(self)
        sizePolicy = self.checkboxes.sizePolicy()
        sizePolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        self.checkboxes.setSizePolicy(sizePolicy)

        maxWidth = 0

        for name in column_names:
            item = QtWidgets.QListWidgetItem(name)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            item.setText(_translate("Dialog", name))
            self.checkboxes.addItem(item)
            setattr(tasklist, f"check_{name}", item)

            maxWidth = max(maxWidth, self.checkboxes.sizeHintForColumn(0)) * 1.05

        self.checkboxes.setMaximumWidth(int(maxWidth))

        itemHeight = self.checkboxes.sizeHintForRow(0)
        itemCount = self.checkboxes.count()
        maxHeight = itemHeight * itemCount * 1.05
        self.checkboxes.setMaximumHeight(int(maxHeight))

        layout = QVBoxLayout(self)
        layout.addWidget(self.checkboxes)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


class TaskList(QtWidgets.QDialog, ui.task_list.Ui_Dialog, SpaceMixin):
    def rearrange_list(self, item):
        """Callback for easy rearranging of the list, no filtering."""
        # save the current selected rows in the task_table
        selection = self.task_table.selectedRanges()
        # also save the current scroll position and sorting
        scroll_pos = self.task_table.verticalScrollBar().value()
        sort_col = self.task_table.horizontalHeader().sortIndicatorSection()
        sort_order = self.task_table.horizontalHeader().sortIndicatorOrder()

        self.arrange_table(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.update()
        # restore the sorting, scroll position and selection
        self.task_table.horizontalHeader().setSortIndicator(sort_col, sort_order)
        self.task_table.verticalScrollBar().setValue(scroll_pos)

        for i in selection:
            self.task_table.setRangeSelected(i, True)

    def __init__(self, selected_tasks: set | None = None):
        super().__init__()
        self.setupUi(self)

        app.list_of_task_lists.append(self)
        app.list_of_windows.append(self)

        self.gui_timer = QTimer()
        "Timer for polling if something has changed and regenerate the GUI."
        self.gui_timer.start(100)
        self.last_generated = 0
        self.field_filter.setCompleter(QCompleter(app.history))
        self.tasks: list[Task] = []
        self.selected_tasks: set[Task] = selected_tasks or {}
        if self.selected_tasks:
            self.setWindowTitle(f"Aufgabenliste ( auf {len(self.selected_tasks)} Aufgaben gefiltert)")

        # displayed columns: tuple[Header, displayed, how to get value]

        self.columns = (
            ("space", lambda t: str(t.space.name)),
            ("level", lambda t: str(t.level)),
            ("priority", lambda t: str(t.get_total_priority())),
            ("deadline", lambda t: deadline_as_str(t.deadline)),
            ("done", lambda t: OK if t.done else NOK),
            ("draft", lambda t: OK if t.draft else NOK),
            ("inactive", lambda t: OK if t.inactive else NOK),
            ("deleted", lambda t: OK if t.deleted else NOK),
            ("status", lambda t: status_icons[t.get_status()]),
            ("do", lambda t: t.get_short_do()),
        )

        self.column_selection = Checklist(self, [name for name, _ in self.columns[:-2]])
        self.column_selection.setHidden(True)

        # to make it compatible with the rest of the code
        self.check_do = QtWidgets.QListWidgetItem("do")
        self.check_do.setCheckState(QtCore.Qt.CheckState.Checked)
        self.check_status = QtWidgets.QListWidgetItem("status")
        self.check_status.setCheckState(QtCore.Qt.CheckState.Checked)

        self.column_selection.checkboxes.itemChanged.connect(self.rearrange_list)

        def _show_column_selection():
            self.column_selection.setHidden(False)
            # mouse cursor position
            global_pos = QtGui.QCursor.pos()
            self.column_selection.move(global_pos)

            screen_geometry = app.primaryScreen().geometry()
            if self.column_selection.frameGeometry().right() > screen_geometry.right():
                self.column_selection.move(
                    global_pos.x() - self.column_selection.width(),
                    global_pos.y(),
                )
            if self.column_selection.frameGeometry().bottom() > screen_geometry.bottom():
                self.column_selection.move(
                    global_pos.x(),
                    global_pos.y() - self.column_selection.height(),
                )

        self.task_table.horizontalHeader().setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_table.horizontalHeader().customContextMenuRequested.connect(_show_column_selection)

        @self.gui_timer.timeout.connect
        def db_changed_check():
            if Path(config.db_path).stat().st_mtime > self.last_generated:
                self.build_task_table()

        def _delete_item():
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

        QShortcut(QKeySequence(Qt.Key.Key_Delete), self).activated.connect(_delete_item)

        def toggle_fullscreen():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(toggle_fullscreen)

        def copy_to_clipboard():
            if not (selected := self.get_selected_tasks()):
                return
            text = turn_tasks_into_text(selected)
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)

        QShortcut(
            QKeySequence(
                QKeyCombination(Qt.Modifier.CTRL, Qt.Key.Key_C),
            ),
            self,
        ).activated.connect(copy_to_clipboard)

        QShortcut(
            QKeySequence(
                QKeyCombination(Qt.Modifier.CTRL, Qt.Key.Key_F),
            ),
            self,
        ).activated.connect(lambda: self.field_filter.setFocus())

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)

        self.build_space_list()
        self._first_space_switch = True
        if self.selected_tasks:
            self.space.setCurrentIndex(0)
        else:
            self.space.setCurrentIndex(
                x
                if (x := self.space.findText(config.last_selected_space or config.last_edited_space)) > -1
                else 0
            )

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_table()
            config.last_selected_space = self.space.currentText() or ""
            config.save()

        self._build_button1_menu()

        def create_task():
            win = task_editor.Editor(current_space=self.space.currentText())
            win.show()

        menu = QtWidgets.QMenu()

        menu.addAction("neu", create_task)
        menu.addAction("als Klon", self.clone_as_is)
        menu.addAction("kloniert als Subtask", self.clone_as_sub)
        menu.addAction("kloniert als Supertask", self.clone_as_sup)
        self.button6.setMenu(menu)

        # space menu
        menu = QtWidgets.QMenu()

        def _space_set():
            match (win := choose_space.SpaceSelection()).exec():
                case QtWidgets.QDialog.DialogCode.Accepted:
                    space = get_space_id(
                        win.space.currentText(),
                        win.space.currentIndex(),
                    )
                case _:  # Cancelled
                    return
            for task in (selected := self.get_selected_tasks()):
                task.set_("space_id", space)
            self.build_task_table()
            self.statusBar.showMessage(
                f"Raum für {len(selected)} Aufgabe{'' if len(selected) == 1 else 'n'} gesetzt.",
                5000,
            )

        menu.addAction("für ausgewählte Aufgaben setzen", _space_set)

        def _space_add():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self,
                "Neuer Space",
                "Name des neuen Space",
                QtWidgets.QLineEdit.EchoMode.Normal,
                "",
            )
            if okPressed and text != "":
                db.execute(
                    f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                )
                db.commit()
                space_editor.SpaceEditor(text).exec()
                self.statusBar.showMessage(f"Raum '{text}' hinzugefügt.", 5000)
                for win in app.list_of_task_editors:
                    win.build_space_list()
                for win in app.list_of_task_lists:
                    win.build_space_list()

        menu.addAction("hinzufügen", _space_add)

        def _space_delete():
            space_name = self.space.currentText()
            if [task for task in app.tasks.values() if task.space.name == space_name]:
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
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_editors:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_organizers:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)

        menu.addAction("löschen", _space_delete)

        def space_edit():
            if self.space.currentData() is None:
                self.statusBar.showMessage("Dieser 'Raum' lässt sich nicht bearbeiten.", 5000)
                return
            space_editor.SpaceEditor(self.space.currentText()).exec()

        menu.addAction("bearbeiten", space_edit)

        self.button9a.setMenu(menu)

        # skill menu
        menu = QtWidgets.QMenu()

        def _skill_set():
            match (win := choose_skills.Skill_Selection()).exec():
                case QtWidgets.QDialog.DialogCode.Accepted:
                    space = get_space_id(
                        win.space.currentText(),
                        win.space.currentIndex(),
                    )
                case _:  # Cancelled
                    return
            for task in (selected := self.get_selected_tasks()):
                task.set_("space_id", space)
            self.build_task_table()
            self.statusBar.showMessage(
                f"Raum für {len(selected)} Aufgabe{'' if len(selected) == 1 else 'n'} gesetzt.",
                5000,
            )

        menu.addAction("für ausgewählte Aufgaben setzen", _space_set)

        def _skill_add():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self,
                "Neuer Space",
                "Name des neuen Space",
                QtWidgets.QLineEdit.EchoMode.Normal,
                "",
            )
            if okPressed and text != "":
                db.execute(
                    f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                )
                db.commit()
                space_editor.SpaceEditor(text).exec()
                self.statusBar.showMessage(f"Raum '{text}' hinzugefügt.", 5000)
                for win in app.list_of_task_editors:
                    win.build_space_list()
                for win in app.list_of_task_lists:
                    win.build_space_list()

        menu.addAction("hinzufügen", _space_add)

        def _skill_delete():
            space_name = self.space.currentText()
            if [task for task in app.tasks.values() if task.space.name == space_name]:
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
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_editors:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)
                        for win in app.list_of_task_organizers:
                            win.build_space_list()
                            if win.space.currentText() == space_name:
                                win.space.setCurrentIndex(0)

        menu.addAction("löschen", _skill_delete)

        def skill_edit():
            if self.space.currentData() is None:
                self.statusBar.showMessage("Dieser 'Raum' lässt sich nicht bearbeiten.", 5000)
                return
            space_editor.SpaceEditor(self.space.currentText()).exec()

        menu.addAction("bearbeiten", skill_edit)
        self.button9b.setMenu(menu)

        item = QtWidgets.QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable)
        self.task_table.setVerticalHeaderItem(0, item)

        self.build_task_table()

        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.layout.addWidget(self.statusBar)
        self.update()

        @self.task_table.cellDoubleClicked.connect
        def _task_list_doubleclicked(row, column):
            self.edit_selected(self.task_table)

        @self.button1.clicked.connect
        def _button1_clicked():
            """
            Handle the event when button 1 is clicked.
            """
            pass

        def _button2_clicked():
            selected = self.get_selected_tasks()
            for task in selected:
                if task is None:
                    continue
                match self.status.currentIndex():
                    # open
                    case 0:
                        task_finished.Finisher(task, direct=True).exec()
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
            self.task_table.clearSelection()

        QShortcut(QKeySequence(Qt.Key.Key_2), self.task_table).activated.connect(_button2_clicked)
        self.button2.clicked.connect(_button2_clicked)

        @self.button3.clicked.connect
        def _organize_task():
            self.organize_selected(self.task_table)

        @self.button4.clicked.connect
        def _edit_task():
            self.edit_selected(self.task_table)

        @self.button5.clicked.connect
        def _start_task():
            selected = self.get_selected_tasks()

            if not selected:
                return
            elif len(selected) > 1:
                self.statusBar.showMessage(
                    "Es kann jeweils nur eine Aufgabe gestartet werden.",
                    5000,
                )
            else:
                self.hide()
                task_running.Running(selected.pop())

        # button8

        @self.ilk.currentIndexChanged.connect
        def ilk_switched():
            self.build_task_table()

        @self.status.currentIndexChanged.connect
        def _status_switched():
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
            self._build_button1_menu()
            self.build_task_table()

        if self.selected_tasks:
            self.status.setCurrentIndex(5)

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.field_filter.textChanged.connect(lambda: QTimer.singleShot(1000, _filter_changed))

        def _filter_changed():
            text = self.field_filter.text().casefold()
            self.arrange_table(list(filter_tasks_by_content(self.tasks, text.casefold())))
            if len(text) > 3 and text not in app.history and not text.isspace():
                app.history.appendleft(self.field_filter.text())
            self.field_filter.completer().setModel(QStringListModel(app.history))
            self.update()

    def _set_as_open(self):
        selected = [task for task in self.get_selected_tasks() if task.is_open]
        if not selected:
            return

        db.executemany(
            """
UPDATE tasks
SET 'deleted' = False, 'done' = False, 'draft' = False, 'inactive' = False
WHERE id == (?)
""",
            [(task.id,) for task in selected],
        )
        db.commit()

    def _set_as(self, property: str, set_flag):
        selected = self.get_selected_tasks()

        if not selected:
            return

        for task in selected:
            if property == "done" and set_flag:
                task_finished.Finisher(task).exec()
            else:
                task.set_(property, set_flag)
            task.reload()

    def clone_as_is(self):
        for task in self.get_selected_tasks():
            self.open_editor(task, cloning=True)

    def clone_as_sub(self):
        for task in self.get_selected_tasks():
            self.open_editor(task, cloning=True, as_sup=-1)

    def clone_as_sup(self):
        for task in self.get_selected_tasks():
            self.open_editor(task, cloning=True, as_sup=1)

    def build_task_table(self):
        """Prepare for filtering the tasks, then fetch and display them."""

        self.last_generated = time()

        if self.selected_tasks:
            self.tasks = filter_tasks(self, self.selected_tasks)
        else:
            self.tasks = filter_tasks(self, app.tasks.values())

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

        header_font = QFont("Segoi UI")
        header_font.setBold(True)
        header_font.setPixelSize(10)

        self.task_table.setColumnCount(
            len(
                list(
                    filter(
                        lambda c: getattr(self, f"check_{c[0]}").checkState() == QtCore.Qt.CheckState.Checked,
                        self.columns,
                    )
                )
            )
        )

        translation = {
            "do": _translate("TaskList", "Beschreibung"),
            "status": _translate("TaskList", "Status"),
            "space": _translate("TaskList", "Raum"),
            "level": _translate("TaskList", "Level"),
            "priority": _translate("TaskList", "Priorität"),
            "deadline": _translate("TaskList", "Deadline"),
            "done": _translate("TaskList", "Erledigt"),
            "draft": _translate("TaskList", "Entwurf"),
            "inactive": _translate("TaskList", "Inaktiv"),
            "deleted": _translate("TaskList", "Gelöscht"),
        }

        currently_selected_rows = self.task_table.selectionModel()

        selected_columns = list(
            filter(
                lambda c: getattr(self, f"check_{c[0]}").checkState() == QtCore.Qt.CheckState.Checked,
                self.columns,
            )
        )

        for column_number, column in enumerate(selected_columns):
            self._set_header(translation[column[0]], header_font, column_number)

        for i, task in enumerate(tasks):
            for column_number, (header, func) in enumerate(selected_columns):
                content = func(task)
                if isinstance(content, str):
                    item = QtWidgets.QTableWidgetItem(content)
                    item.setFont(app.fira_font)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if isinstance(content, QIcon):
                    item = QtWidgets.QTableWidgetItem()
                    item.setIcon(content)
                item.setData(Qt.ItemDataRole.UserRole, task)
                self.task_table.setItem(i, column_number, item)
                if header == "status":
                    item.setToolTip(task.get_status_text())

        self.task_table.setSortingEnabled(True)
        self.task_table.resizeColumnsToContents()
        self.task_table.ensurePolished()
        self.task_table.setSelectionModel(currently_selected_rows)

        self.task_table.show()

    def _set_header(self, text, font, column):
        item = QTableWidgetItem(text)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.task_table.setHorizontalHeaderItem(column, item)
        self.task_table.update()

    def _build_button1_menu(self):
        menu = QtWidgets.QMenu()
        DRAFT = ("Entwurf", partial(self._set_as, "draft", True))
        INACTIVE = ("inaktiv", partial(self._set_as, "inactive", True))
        DONE = ("erledigt", partial(self._set_as, "done", True))
        DELETED = ("gelöscht", partial(self._set_as, "deleted", True))

        match self.status.currentIndex():
            case 0:  # open
                menu.addAction(*DRAFT)
                menu.addAction(*INACTIVE)
                menu.addAction(*DONE)
                menu.addAction(*DELETED)
            case 1:  # draft
                menu.addAction("offen", self._set_as_open)
                menu.addAction(
                    "kein Entwurf",
                    partial(self._set_as, "draft", False),
                )
                menu.addAction(*INACTIVE)
                menu.addAction(*DONE)
                menu.addAction(*DELETED)
            case 2:  # inactive
                menu.addAction("offen", self._set_as_open)
                menu.addAction(*DRAFT)
                menu.addAction(
                    "nicht inaktiv",
                    partial(self._set_as, "inactive", False),
                )
                menu.addAction(*DONE)
                menu.addAction(*DELETED)

            case 3:  # done
                menu.addAction("offen", self._set_as_open)
                menu.addAction(*DRAFT)
                menu.addAction(*INACTIVE)
                menu.addAction(
                    "nicht erledigt",
                    partial(self._set_as, "done", False),
                )
                menu.addAction(*DELETED)
            case 4:  # deleted
                menu.addAction("offen", self._set_as_open)
                menu.addAction(*DRAFT)
                menu.addAction(*INACTIVE)
                menu.addAction(*DONE)
                menu.addAction(
                    "nicht gelöscht",
                    partial(self._set_as, "deleted", False),
                )
            case 5:  # all
                menu.addAction("offen", self._set_as_open)
                menu.addAction(*DRAFT)
                menu.addAction(*INACTIVE)
                menu.addAction(*DONE)
                menu.addAction(*DELETED)
        self.button1.setMenu(menu)

    def edit_selected(self, widget):
        selected = self.get_selected_tasks()
        if not selected:
            self.statusBar.showMessage("Keine Aufgabe ausgewählt", 5000)
        for task in selected:
            # breakpoint()
            for win in app.list_of_task_editors:
                if win.task == task:
                    win.show()
                    win.raise_()
                    break
            else:
                win = task_editor.Editor(task)
                win.show()

    def organize_selected(self, widget):
        selected = self.get_selected_tasks()
        if not selected:
            self.statusBar.showMessage("Keine Aufgabe ausgewählt", 5000)
        for task in selected:
            for win in app.list_of_task_organizers:
                if win.task == task:
                    win.show()
                    win.raise_()
                    break
            else:
                win = task_organizer.Organizer(task)
                win.show()

    def open_editor(self, task, cloning=False, as_sup=0):
        win = task_editor.Editor(task, cloning=cloning, as_sup=as_sup)
        app.list_of_task_editors.append(win)
        app.list_of_windows.append(win)
        win.show()

    def reject(self):
        """Reject the task list and remove it from the application.

        Args:
            self: The task list to be rejected.

        Returns:
            None

        Raises:
            None

        Examples:
            To reject a task list, call the reject() method on the task list object:
            >>> task_list.reject()
        """
        super().reject()
        app.list_of_task_lists.remove(self)
        app.list_of_windows.remove(self)

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            try:
                app.list_of_windows[-1].raise_()
            except RuntimeError:
                breakpoint()

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

    def _notify_windows_of_task_deletion(self, task):
        for win in app.list_of_task_lists:
            win.build_task_list()
        for win in app.list_of_task_organizers:
            win.build_task_list()
            win.subtasks.remove
            win.arrange_sub_sup_task_table()

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            print("Right-mouse double-click detected")
        else:
            super().mouseDoubleClickEvent(event)

    # right click on a table item opens a menu with options to send the task via telegram
    def _showContextMenu(self, pos):
        if not self.task_table.rect().contains(pos):
            return

        def _send_task():
            selected = self.get_selected_tasks()
            if not selected:
                return
            text = turn_tasks_into_text(selected)
            # escape characters in the text for http
            text = urllib.parse.quote(text)
            webbrowser.open(f"https://t.me/share/url?url= &text={text}")

        menu = QtWidgets.QMenu()
        icon = QtGui.QIcon(str(config.base_path / "extra/feathericons/send.svg"))
        menu.addAction(icon, "Senden", _send_task)
        menu.exec(self.mapToGlobal(pos))


def turn_tasks_into_text(tasks: list[Task]):
    return "\n\n".join(
        f"=== Task {task.id} {task.printable_deadline} {task.printable_percentage} ===\n{task.do}"
        for task in tasks
    )
