from datetime import datetime
from math import isinf

import use
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont, QFontDatabase

import ui


def arrange_list(self: ui.task_list.Ui_Dialog, tasks):
    """Needs to be extra, otherwise filtering would hit the DB repeatedly."""
    self.task_list.hide()
    self.task_list.clear()

    self.task_list.setSortingEnabled(False)
    self.task_list.setRowCount(len(tasks))
    ID = QFontDatabase.addApplicationFont("./extra/Fira_Sans/FiraSans-Regular.ttf")
    family = QFontDatabase.applicationFontFamilies(ID)
    font = QFont(family)
    breakpoint()

    for i, task in enumerate(tasks):
        short = (
            task.do.split("\n")[0][:72].ljust(72, " ") + ("" if len(task.do) < 72 else "[…]")
        ) + f" ({task.ilk.name})"
        item = QtWidgets.QTableWidgetItem(short)
        item.setFont(font)
        item.setToolTip(task.space)
        item.setData(Qt.ItemDataRole.UserRole, task)
        self.task_list.setItem(i, 0, item)

        item = QtWidgets.QTableWidgetItem(str(task.level))
        self.task_list.setItem(i, 1, item)
        item = QtWidgets.QTableWidgetItem(str(task.priority))
        self.task_list.setItem(i, 2, item)
        item = QtWidgets.QTableWidgetItem(
            "---" if isinf(task.deadline) else datetime.fromtimestamp(task.deadline).isoformat()
        )
        self.task_list.setItem(i, 4, item)

    if not tasks:
        self.task_list.clearContents()
        self.task_list.setRowCount(0)
    self.task_list.setSortingEnabled(True)
    self.task_list.resizeColumnsToContents()
    self.task_list.show()
