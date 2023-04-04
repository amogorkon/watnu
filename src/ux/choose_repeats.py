from datetime import datetime

import numpy as np
from dateutil.relativedelta import relativedelta
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QDate, QDateTime, QItemSelectionModel, Qt
from PyQt6.QtSql import QSqlTableModel

import ui, ux
from classes import EVERY, Every, Task
from stuff import __version__



class RepeatChooser(QtWidgets.QDialog, ui.choose_repeats.Ui_Dialog):
    def __init__(self, editor: "ux.task_editor.Editor", task: Task = None):
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
