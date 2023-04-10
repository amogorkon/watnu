import contextlib
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
from logic import (filter_tasks_by_constraints, filter_tasks_by_content,
                   filter_tasks_by_ilk, filter_tasks_by_space,
                   filter_tasks_by_status, pipes, retrieve_tasks)
from stuff import app, config, db
from ux import (choose_space, task_editor, task_finished, task_list,
                task_running)

_translate = QtCore.QCoreApplication.translate

OK = QIcon(str(config.base_path / "src/extra/check.svg"))
NOK = QIcon(str(config.base_path / "src/extra/cross.svg"))


class Organizer(QtWidgets.QDialog, ui.task_organizer.Ui_Dialog):
    def rearrange_list(self):
        """Callback for easy rearranging of the list, no filtering."""
        self.arrange_list(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
        self.update()

    def __init__(self, task=None, filters=None):
        super().__init__()
        self.task = task
        self.filters = filters

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
            ("deadline", self.check_deadline, lambda t: task_list.deadline_as_str(t.deadline)),
            ("done", self.check_done, lambda t: OK if t.done else NOK),
            ("draft", self.check_draft, lambda t: OK if t.draft else NOK),
            ("inactive", self.check_inactive, lambda t: OK if t.inactive else NOK),
            ("deleted", self.check_deleted, lambda t: OK if t.deleted else NOK),
            ("do", self.check_do, lambda t: task_list.get_desc(t)),
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

        QShortcut(
            QKeySequence(
                QKeyCombination(Qt.Modifier.CTRL, Qt.Key.Key_F),
            ),
            self,
        ).activated.connect(lambda: self.field_filter.setFocus())

        task_list.build_space_list(self)
        self.space.setCurrentIndex(
            x if (x := self.space.findText(app.last_edited_space or config.last_selected_space)) > -1 else 0
        )

        @self.space.currentIndexChanged.connect
        def space_switched():
            self.build_task_list()
            config.last_selected_space = self.space.currentText() or ""
            config.save()

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
            self.select_respective_tasks(self.get_selected_tasks())

        @self.button1.clicked.connect
        def _():
            pass

        @self.button2.clicked.connect
        def button2_clicked():
            pass

        @self.button3.clicked.connect
        def _():
            pass

        @self.button4.clicked.connect
        def _():
            pass

        @self.button5.clicked.connect
        def _():
            pass

        @self.button6.clicked.connect
        def _():
            pass

        @self.button7.clicked.connect
        def _():
            pass

        @self.button8.clicked.connect
        def _():
            pass

        @self.button9.clicked.connect
        def _():
            pass

        @self.ilk.currentIndexChanged.connect
        def ilk_switched():
            self.build_task_list()

        @self.status.currentIndexChanged.connect
        def status_switched():
            self.build_task_list()

        # once we change the filter, we wait for 1 sec before applying the filter,
        # in order to avoid constant refiltering for something the user doesn't actually want.
        self.field_filter.textChanged.connect(lambda: QTimer.singleShot(1000, filter_changed))

        def filter_changed():
            self.arrange_list(list(filter_tasks_by_content(self.tasks, self.field_filter.text().casefold())))
            self.update()

    def build_task_list(self):
        """Prepare for filtering the tasks, then fetch and display them."""

        self.last_generated = time()

        config.last_selected_space = self.space.currentText() or ""
        config.save()
        self.tasks = task_list.get_filtered_tasks(self)

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

        currently_selected_rows = self.task_list.selectionModel()

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
                self.task_list.setItem(i, column_number, item)

        self.task_list.setSortingEnabled(True)
        self.task_list.resizeColumnsToContents()
        self.task_list.ensurePolished()
        self.task_list.setSelectionModel(currently_selected_rows)

        self.task_list.show()

    def select_respective_tasks(self, tasks):
        pass

    def set_header(self, text, font, column):
        item = QTableWidgetItem(text)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.task_list.setHorizontalHeaderItem(column, item)
        self.task_list.update()

    def reject(self):
        super().reject()
        app.list_of_task_organizers.remove(self)
        app.list_of_windows.remove(self)

        if app.win_running:
            app.win_running.show()
            app.win_running.raise_()
            return

        for win in app.list_of_windows:
            win.show()
            win.raise_()

    def get_selected_tasks(self) -> list[Task]:
        return [
            self.task_list.item(row, 0).data(Qt.ItemDataRole.UserRole)
            for row in range(self.task_list.rowCount())
            if (x := self.task_list.item(row, 0).isSelected()) and x is not None
        ]
