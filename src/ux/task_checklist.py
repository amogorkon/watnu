from PyQt6 import QtCore, QtWidgets

import src.ui as ui
from src.stuff import app

_translate = QtCore.QCoreApplication.translate


class CheckList(QtWidgets.QDialog, ui.task_checklist.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        app.list_of_task_checklists.append(self)
        app.list_of_windows.append(self)

    def reject(self):
        super().reject()
        app.list_of_task_checklists.remove(self)
        app.list_of_windows.remove(self)

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()
