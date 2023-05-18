from PyQt6 import QtCore, QtWidgets

import src.ui as ui

_translate = QtCore.QCoreApplication.translate


class CheckList(QtWidgets.QDialog, ui.task_list.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
