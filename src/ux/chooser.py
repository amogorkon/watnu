from datetime import datetime

import numpy as np

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QDate, QDateTime, QItemSelectionModel, Qt
from PyQt6.QtSql import QSqlTableModel
from dateutil.relativedelta import relativedelta

import ui
from classes import EVERY, Every, Task2

from .stuff import app, db, config, __version__


def Chooser(editor: "task_editor.Editor", task: Task2, kind: str):
    """Returns the fitting instance of a Chooser."""

    class SkillChooser(QtWidgets.QDialog, ui.choose_skills.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.task = task
            self.editor = editor
            model = QSqlTableModel()
            model.setTable("skills")
            model.setSort(1, Qt.SortOrder.AscendingOrder)
            model.select()
            self.listView.setModel(model)
            self.listView.setModelColumn(1)

            if task:
                # holy crap, that was a difficult birth..
                self.listView.selectionModel().clear()
                for index in range(model.rowCount()):
                    if model.itemData(model.index(index, 0))[0] in task.skill_ids:
                        self.listView.selectionModel().select(
                            model.index(index, 1), QItemSelectionModel.Select
                        )

        def accept(self):
            super().accept()
            self.editor.skill_ids = [
                self.listView.model().record(idx.row()).value("skill_id")
                for idx in self.listView.selectedIndexes()
            ]

    class SubTaskChooser(QtWidgets.QDialog, ui.choose_skills.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.task = task
            self.editor = editor
            model = QSqlTableModel()
            model.setTable("tasks")
            model.setSort(1, Qt.SortOrder.AscendingOrder)
            model.select()
            self.listView.setModel(model)
            self.listView.setModelColumn(1)

            if task:
                # holy crap, that was a difficult birth..
                self.listView.selectionModel().clear()
                for index in range(model.rowCount()):
                    if model.itemData(model.index(index, 0))[0] in [t.id for t in task.subtasks]:
                        self.listView.selectionModel().select(
                            model.index(index, 1), QItemSelectionModel.Select
                        )

        def accept(self):
            self.editor.subtasks = [
                self.listView.model().record(idx.row()).value("id") for idx in self.listView.selectedIndexes()
            ]

    class SuperTaskChooser(QtWidgets.QDialog, ui.choose_skills.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.task = task
            self.editor = editor
            model = QSqlTableModel()
            model.setTable("tasks")
            model.setSort(1, Qt.SortOrder.AscendingOrder)
            model.select()
            self.listView.setModel(model)
            self.listView.setModelColumn(1)

            if task:
                # holy crap, that was a difficult birth..
                self.listView.selectionModel().clear()
                for index in range(model.rowCount()):
                    if model.itemData(model.index(index, 0))[0] in [t.id for t in task.supertasks]:
                        self.listView.selectionModel().select(
                            model.index(index, 1), QItemSelectionModel.Select
                        )

        def accept(self):
            self.editor.supertasks = [
                self.listView.model().record(idx.row()).value("id") for idx in self.listView.selectedIndexes()
            ]

    class ConstraintChooser(QtWidgets.QDialog, ui.choose_constraints.Ui_Dialog):
        def __init__(self, editor, task: Task2 = None):
            super().__init__()
            self.setupUi(self)
            self.editor = editor
            self.table.horizontalHeader().setHighlightSections(False)
            for i, (hour, part) in enumerate((hour, part) for hour in range(24) for part in range(6)):
                item = QtWidgets.QTableWidgetItem(f"{hour}: {part}0-{part}9")
                if i % 6 == 0:
                    font = QtGui.QFont()
                    font.setItalic(True)
                    font.setWeight(90)
                    item.setFont(font)
                self.table.setVerticalHeaderItem(i, item)
            for column, day in enumerate(editor.constraints):
                for row, value in enumerate(day):
                    if value:
                        self.table.setCurrentCell(row, column)

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
            A[[idx.column() * 144 + idx.row() for idx in self.table.selectedIndexes()]] = 1
            self.editor.constraints = A.reshape(7, 144)

    class DeadlineChooser(QtWidgets.QDialog, ui.choose_deadline.Ui_Dialog):
        def __init__(self, editor, task=None):
            super().__init__()
            self.setupUi(self)
            self.editor = editor
            self.reference_date.setDate(QDate().currentDate())

            @self.enter_date.clicked.connect
            def enter_date():
                now = datetime.fromtimestamp(self.reference_date.dateTime().toSecsSinceEpoch())
                days = self.in_days.value()
                weeks = self.in_weeks.value()
                months = self.in_months.value()
                qdate = QDateTime()
                qdate.setSecsSinceEpoch(
                    int(datetime.timestamp(now + relativedelta(days=days, weeks=weeks, months=months)))
                )
                self.reference_date.setDateTime(qdate)

        def accept(self):
            super().accept()
            self.editor.deadline = self.reference_date.dateTime().toSecsSinceEpoch()

    class RepeatChooser(QtWidgets.QDialog, ui.choose_repeats.Ui_Dialog):
        def __init__(self, editor: task_editor.Editor, task: Task2 = None):
            super().__init__()
            self.setupUi(self)
            self.editor = editor
            self.every_ilk.setId(self.every_minute, 1)
            self.every_ilk.setId(self.every_hour, 2)
            self.every_ilk.setId(self.every_day, 3)
            self.every_ilk.setId(self.every_week, 4)
            # self.every_ilk.setId(self.every_month, 5)
            self.every_ilk.setId(self.every_year, 6)

            self.per_ilk.setId(self.per_minute, 1)
            self.per_ilk.setId(self.per_hour, 2)
            self.per_ilk.setId(self.per_day, 3)
            self.per_ilk.setId(self.per_week, 4)
            # self.per_ilk.setId(self.per_month, 5)
            self.per_ilk.setId(self.per_year, 6)

            if task is not None:
                self.every_ilk.button(task.repeats.every_ilk.value).setChecked(True)
                self.x_every.setValue(task.repeats.amount)
                self.per_ilk.button(task.repeats.per_ilk.value).setChecked(True)
                self.x_per.setValue(task.repeats.min_distance)

        def accept(self):
            super().accept()
            self.editor.repeats = Every(
                EVERY(self.every_ilk.checkedId()),
                self.x_every.value(),
                EVERY(self.per_ilk.checkedId()),
                self.x_per.value(),
            )

    match kind:
        case "subtasks":
            return SubTaskChooser(editor, task)
        case "supertasks":
            return SuperTaskChooser(editor, task)
        case "skills":
            return SkillChooser(editor, task)
        case "deadline":
            return DeadlineChooser(editor, task)
        case "constraints":
            return ConstraintChooser(editor, task)
        case "repeats":
            return RepeatChooser(editor, task)


from ux import task_editor
