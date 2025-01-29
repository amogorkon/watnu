from PyQt6 import QtCore, QtWidgets

import src.ui as ui
from src import app

_translate = QtCore.QCoreApplication.translate


class CheckList(QtWidgets.QDialog, ui.task_checklist.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        app.list_of_task_checklists.append(self)
        app.list_of_windows.append(self)

    def reject(self):
        """
        Reimplemented to remove the current task checklist from the list of task checklists and windows,
        and to raise the previous window in the list of windows.
        """
        super().reject()
        app.list_of_task_checklists.remove(self)
        app.list_of_windows.remove(self)

        if not app.win_what.isHidden():
            app.win_what.raise_()
        else:
            app.list_of_windows[-1].raise_()
