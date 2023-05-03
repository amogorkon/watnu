from datetime import datetime

from dateutil.relativedelta import relativedelta
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QDate, QDateTime

import src.ui as ui


class DeadlineChooser(QtWidgets.QDialog, ui.choose_deadline.Ui_Dialog):
    def __init__(self, editor, task):
        super().__init__()
        self.setupUi(self)
        self.editor = editor
        self.task = task
        if task.deadline != float("inf"):
            self.reference_date.setDateTime(QDateTime().fromSecsSinceEpoch(int(task.deadline)))
        else:
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
