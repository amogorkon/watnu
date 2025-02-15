from pathlib import Path
from time import time

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QKeyCombination, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QMenu,
    QStatusBar,
    QTableWidgetItem,
)

import src.ui as ui
from src import app, config, ux_helpers
from src.classes import Task
from src.logic import (
    filter_tasks_by_content,
)
from src.ux import task_editor, task_list

_translate = QtCore.QCoreApplication.translate

translation = {
    "do": _translate("Organizer", "Beschreibung"),
    "space": _translate("Organizer", "Raum"),
    "level": _translate("Organizer", "Level"),
    "priority": _translate("Organizer", "Priorität"),
    "deadline": _translate("Organizer", "Deadline"),
    "done": _translate("Organizer", "Erledigt"),
    "draft": _translate("Organizer", "Entwurf"),
    "inactive": _translate("Organizer", "Inaktiv"),
    "deleted": _translate("Organizer", "Gelöscht"),
}


class Organizer(QDialog, ui.task_organizer.Ui_Dialog, ux_helpers.SpaceMixin):
    def __init__(
        self,
        task: Task | None = None,
        filters=None,
        editor=None,
        depends_on=True,
    ):
        super().__init__()

        global OK, NOK, ARROW_DOWN, ARROW_UP
        OK = QIcon(str(config.base_path / "extra/check.svg"))
        NOK = QIcon(str(config.base_path / "extra/cross.svg"))

        ARROW_DOWN = QIcon()
        ARROW_DOWN.addPixmap(
            QtGui.QPixmap("ui\\../extra/arrow-down.svg"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        ARROW_UP = QIcon()
        ARROW_UP.addPixmap(
            QtGui.QPixmap("ui\\../extra/arrow-up.svg"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )

        self.setupUi(self)

        app.list_of_task_organizers.append(self)
        app.list_of_windows.append(self)

        # buttonBox = QDialogButtonBox(self)
        # buttonBox.setOrientation(Qt.Orientation.Horizontal)
        # buttonBox.setStandardButtons(
        #     QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        # )

        # buttonBox.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        # buttonBox.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        # self.layout.addWidget(self.buttonBox)

        self.field_filter.setText(app.history[0] if app.history else "")

        self.task = task
        self.subtasks: set[Task] = set()
        self.supertasks: set[Task] = set()

        if task:
            self.subtasks = self.task.subtasks
            self.supertasks = self.task.supertasks

        self.filters = filters
        self.editor = editor

        self._drag_info: list[Task] = []
        self.statusBar = QStatusBar(self)
        self.statusBar.setSizeGripEnabled(False)
        self.gui_timer = QTimer()
        "Timer for polling if things changed and regenerate the GUI."
        self.gui_timer.start(100)
        self.last_generated = 0

        self.tasks: list[Task] = []
        self.check_do = QCheckBox()
        self.check_do.setChecked(True)

        self.depends_on = depends_on
        "Switch for relationship_button."

        if not self.depends_on:
            self.relationship_button.setText("ist Voraussetzung für")
            self.relationship_button.setIcon(ARROW_UP)
        else:
            self.relationship_button.setText("hängt ab von")
            self.relationship_button.setIcon(ARROW_DOWN)

        @self.relationship_button.clicked.connect
        def relationship_button_clicked():
            if self.depends_on:
                self.relationship_button.setText("ist Voraussetzung für")
                self.relationship_button.setIcon(ARROW_UP)
            else:
                self.relationship_button.setText("hängt ab von")
                self.relationship_button.setIcon(ARROW_DOWN)
            self.depends_on ^= True
            self.arrange_sub_sup_task_table(self.subtasks if self.depends_on else self.supertasks)

        # displayed columns: tuple[Header, displayed, how to get value]

        self.columns = (
            ("space", self.check_space, lambda t: str(t.space)),
            ("level", self.check_level, lambda t: str(t.level)),
            (
                "priority",
                self.check_priority,
                lambda t: str(t.priority),
            ),
            (
                "deadline",
                self.check_deadline,
                lambda t: task_list.deadline_as_str(t.deadline),
            ),
            (
                "done",
                self.check_done,
                lambda t: OK if t.done else NOK,
            ),
            (
                "draft",
                self.check_draft,
                lambda t: OK if t.draft else NOK,
            ),
            (
                "inactive",
                self.check_inactive,
                lambda t: OK if t.inactive else NOK,
            ),
            (
                "deleted",
                self.check_deleted,
                lambda t: OK if t.deleted else NOK,
            ),
            ("do", self.check_do, lambda t: t.get_short_do()),
        )

        for _, check, _ in self.columns:
            check.stateChanged.connect(self.rearrange_list)

        @self.gui_timer.timeout.connect
        def db_changed_check():
            if Path(config.db_path).stat().st_mtime > self.last_generated:
                self.build_task_table()
                if self.task:
                    self.task = self.task.reload()
                    self.arrange_concerned_task_table(self.task)
                self.arrange_sub_sup_task_table(self.subtasks if self.depends_on else self.supertasks)

        def toggle_fullscreen():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        QShortcut(QKeySequence(Qt.Key.Key_F11), self).activated.connect(toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.accept)

        QShortcut(
            QKeySequence(
                QKeyCombination(Qt.Modifier.CTRL, Qt.Key.Key_F),
            ),
            self,
        ).activated.connect(lambda: self.field_filter.setFocus())

        def remove_item_from_sub_sup():
            if not (selected := get_selected_tasks(self.sub_sup_tasks_table)):
                return
            for task in selected:
                if self.depends_on:
                    self.subtasks.remove(task)
                else:
                    self.supertasks.remove(task)
            self.arrange_sub_sup_task_table(self.subtasks if self.depends_on else self.supertasks)

        QShortcut(QKeySequence(Qt.Key.Key_Delete), self.sub_sup_tasks_table).activated.connect(
            remove_item_from_sub_sup
        )

        self.build_space_list()
        self.space.setCurrentIndex(x if (x := self.space.findText(config.last_selected_space)) > -1 else 0)

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_table()
            config.last_selected_space = self.space.currentText() or ""
            config.save()

        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable)
        self.tasks_table.setVerticalHeaderItem(0, item)

        self.build_task_table()

        self.statusBar = QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.layout.addWidget(self.statusBar)

        self.build_task_table()
        self.arrange_concerned_task_table(self.task)
        self.arrange_sub_sup_task_table(self.subtasks if self.depends_on else self.supertasks)

        def startDrag(action):
            self._drag_info = []
            for task in get_selected_tasks(self.tasks_table):
                self._drag_info.append(task)
            orig_drag(action)

        # better solution?
        orig_drag = self.tasks_table.startDrag
        self.tasks_table.startDrag = startDrag

        def dropEvent(event):
            if not self.task:
                self.statusBar.showMessage(
                    "Erstmal eine Aufgabe als Bezug auswählen...",
                    5000,
                )
                event.ignore()
                return
            if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
                for task in self._drag_info:
                    if task == self.task:
                        self.statusBar.showMessage(
                            "Aufgabe kann nicht ihre eigene Voraussetzung sein!",
                            5000,
                        )
                        continue
                    if self.depends_on:
                        self.subtasks.add(task)
                    else:
                        self.supertasks.add(task)
                self.task.set_subtasks(self.subtasks) if self.depends_on else self.task.set_supertasks(
                    self.supertasks
                )

                self.arrange_sub_sup_task_table(self.subtasks if self.depends_on else self.supertasks)
                event.accept()
            else:
                event.ignore()
            orig_drop(event)

        orig_drop = self.sub_sup_tasks_table.dropEvent
        self.sub_sup_tasks_table.dropEvent = dropEvent

        self.update()

        @self.tasks_table.cellDoubleClicked.connect
        def doubleclicked_tasks_table(row, column):
            self.organize_selected(self.tasks_table)

        @self.sub_sup_tasks_table.cellDoubleClicked.connect
        def doubleclicked_sub_sup_table(row, column):
            self.organize_selected(self.sub_sup_tasks_table)

        @self.concerned_task_table.cellDoubleClicked.connect
        def doubleclicked_concerned_task(row, column):
            self.organize_selected(self.concerned_task_table)

        @self.button1.clicked.connect
        def _():
            pass

        @self.button2.clicked.connect
        def _():
            pass

        @self.button3.clicked.connect
        def _():
            selected = get_selected_tasks(self.tasks_table)
            for task in selected:
                for win in app.list_of_task_organizers:
                    if win.task == task:
                        win.raise_()
                        break
                else:
                    win = Organizer(task)
                    win.show()

        @self.button4.clicked.connect
        def _():
            selected = get_selected_tasks(self.tasks_table)
            for task in selected:
                for win in app.list_of_task_editors:
                    if win.task == task:
                        win.raise_()
                        break
                else:
                    win = task_editor.Editor(task)
                    app.list_of_task_editors.append(win)
                    app.list_of_windows.append(win)
                    win.show()

        @self.button5.clicked.connect
        def _():
            pass

        @self.button6.clicked.connect
        def _():
            win = task_editor.Editor()
            app.list_of_windows.append(win)
            app.list_of_task_editors.append(win)
            win.show()

        @self.button7.clicked.connect
        def _():
            pass

        menu = QMenu()

        def print_as_mermaid():
            print("mermaid")
            print("graph LR")
            for task in app.tasks.values():
                for supertask in task.supertasks:
                    print(
                        f"{supertask.id}:{supertask.get_short_do(15)} --> {task.id}:{task.get_short_do(15)}"
                    )

        menu.addAction("Mermaid", print_as_mermaid)

        self.button8.setMenu(menu)

        @self.button8.clicked.connect
        def _():
            pass

        menu = QMenu()

        menu.addAction("Deadline", lambda: None)
        menu.addAction("Beschränkung", lambda: None)

        self.button9.setMenu(menu)

        @self.button9.clicked.connect
        def _():
            pass

        @self.ilk.currentIndexChanged.connect
        def ilk_switched():
            self.build_task_table()

        @self.status.currentIndexChanged.connect
        def status_switched():
            self.build_task_table()

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.field_filter.textChanged.connect(lambda: QTimer.singleShot(1000, filter_changed))

        def filter_changed():
            self.arrange_table(
                list(
                    filter_tasks_by_content(
                        self.tasks,
                        self.field_filter.text().casefold(),
                    )
                )
            )
            self.update()

    def get_selected_tasks(self, widget) -> set[Task]:
        return {
            widget.item(row, 0).data(Qt.ItemDataRole.UserRole)
            for row in range(widget.rowCount())
            if (x := widget.item(row, 0).isSelected()) and x is not None
        }

    def build_task_table(self):
        """Prepare for filtering the tasks, then fetch and display them."""
        from src.ux.task_list import filter_tasks

        self.last_generated = time()

        config.last_selected_space = self.space.currentText() or ""
        config.save()
        # exclude tasks that are in the concerned_tasks list
        self.tasks = filter_tasks(self, app.tasks.values())

        self.arrange_table(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.update()

    def arrange_table(self, tasks: list[Task]):
        """Arrange the tasks in the list for display."""
        self.tasks_table.setStyleSheet(
            """
alternate-background-color: #bfffbf;
background-color: #deffde;
font-size: 12pt;
        """
        )
        self.tasks_table.ensurePolished()
        self.tasks_table.setSortingEnabled(False)
        self.tasks_table.setRowCount(len(tasks))

        header_font = QFont("Segoi UI")
        header_font.setBold(True)
        header_font.setPixelSize(10)

        self.tasks_table.setColumnCount(len(list(filter(lambda c: c[1].isChecked(), self.columns))))

        currently_selected_rows = self.tasks_table.selectionModel()

        selected_columns = list(filter(lambda c: c[1].isChecked(), self.columns))

        for column_number, column in enumerate(selected_columns):
            set_header(
                self.tasks_table,
                translation[column[0]],
                header_font,
                column_number,
            )

        for i, task in enumerate(tasks):
            for column_number, (header, displayed, func) in enumerate(selected_columns):
                content = func(task)
                if isinstance(content, str):
                    item = QTableWidgetItem(content)
                    item.setFont(app.fira_font)
                    item.setData(Qt.ItemDataRole.UserRole, task)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if isinstance(content, QIcon):
                    item = QTableWidgetItem()
                    item.setIcon(content)
                self.tasks_table.setItem(i, column_number, item)

        self.tasks_table.setSortingEnabled(True)
        self.tasks_table.resizeColumnsToContents()
        self.tasks_table.ensurePolished()
        self.tasks_table.setSelectionModel(currently_selected_rows)

        self.tasks_table.show()

    def edit_selected(self, widget):
        for task in self.get_selected_tasks(widget):
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

    def organize_selected(self, widget):
        for task in self.get_selected_tasks(widget):
            for win in app.list_of_task_organizers:
                if win.task == task:
                    win.show()
                    win.raise_()
                    break
            else:
                win = Organizer(task)
                win.show()

    def arrange_sub_sup_task_table(self, tasks: set[Task]):
        """Arrange the tasks in the list for display."""
        self.sub_sup_tasks_table.setStyleSheet(
            """
alternate-background-color: #bfffbf;
background-color: #deffde;
font-size: 12pt;
        """
        )
        self.sub_sup_tasks_table.ensurePolished()
        self.sub_sup_tasks_table.setSortingEnabled(False)
        self.sub_sup_tasks_table.setRowCount(len(tasks))

        header_font = QFont("Segoi UI")
        header_font.setBold(True)
        header_font.setPixelSize(10)

        self.sub_sup_tasks_table.setColumnCount(len(list(filter(lambda c: c[1].isChecked(), self.columns))))

        currently_selected_rows = self.sub_sup_tasks_table.selectionModel()

        selected_columns = list(filter(lambda c: c[1].isChecked(), self.columns))

        for column_number, column in enumerate(selected_columns):
            set_header(
                self.sub_sup_tasks_table,
                translation[column[0]],
                header_font,
                column_number,
            )

        for i, task in enumerate(tasks):
            for column_number, (header, displayed, func) in enumerate(selected_columns):
                content = func(task)
                if isinstance(content, str):
                    item = QTableWidgetItem(content)
                    item.setFont(app.fira_font)
                    item.setData(Qt.ItemDataRole.UserRole, task)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if isinstance(content, QIcon):
                    item = QTableWidgetItem()
                    item.setIcon(content)
                self.sub_sup_tasks_table.setItem(i, column_number, item)

        self.sub_sup_tasks_table.setSortingEnabled(True)
        self.sub_sup_tasks_table.resizeColumnsToContents()
        self.sub_sup_tasks_table.ensurePolished()
        self.sub_sup_tasks_table.setSelectionModel(currently_selected_rows)

        self.sub_sup_tasks_table.show()

    def arrange_concerned_task_table(self, task: Task | None):
        """Arrange the concerned task for display."""
        self.concerned_task_table.setStyleSheet(
            """
alternate-background-color: #bfffbf;
background-color: #deffde;
font-size: 12pt;
        """
        )
        self.concerned_task_table.ensurePolished()
        if not task:
            return
        self.concerned_task_table.setColumnCount(len(list(filter(lambda c: c[1].isChecked(), self.columns))))

        selected_columns = list(filter(lambda c: c[1].isChecked(), self.columns))

        for column_number, (header, displayed, func) in enumerate(selected_columns):
            content = func(task)
            if isinstance(content, str):
                item = QTableWidgetItem(content)
                item.setFont(app.fira_font)
                item.setData(Qt.ItemDataRole.UserRole, task)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if isinstance(content, QIcon):
                item = QTableWidgetItem()
                item.setIcon(content)
            self.concerned_task_table.setItem(0, column_number, item)

        self.concerned_task_table.resizeColumnsToContents()
        self.concerned_task_table.ensurePolished()

        self.concerned_task_table.show()
        self.update()

    def reject(self):
        super().reject()
        app.list_of_task_organizers.remove(self)
        app.list_of_windows.remove(self)

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()

    def accept(self):
        super().accept()
        app.list_of_task_organizers.remove(self)
        app.list_of_windows.remove(self)

        save_task(self.task, self.subtasks, self.supertasks)

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()

    def rearrange_list(self):
        """Callback for easy rearranging of the list, no filtering."""
        self.arrange_table(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.arrange_sub_sup_task_table(self.subtasks if self.depends_on else self.supertasks)
        self.arrange_concerned_task_table(self.task)
        self.update()


def get_selected_tasks(table) -> list[Task]:
    return [
        table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(table.rowCount())
        if (x := table.item(row, 0).isSelected()) and x is not None
    ]


def set_header(widget, text, font, column):
    item = QTableWidgetItem(text)
    item.setFont(font)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
    widget.setHorizontalHeaderItem(column, item)
    widget.update()


def save_task(task: Task, subtasks: set[Task], supertasks: set[Task]):
    if not task:
        return
    task.set_subtasks(subtasks)
    task.set_supertasks(supertasks)
