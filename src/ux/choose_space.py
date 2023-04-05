from PyQt6 import QtCore, QtGui, QtWidgets

import ui
from ux.task_list import build_space_list, get_space_id


class Space_Selection(QtWidgets.QDialog, ui.choose_space.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        build_space_list(self)
        self.space.removeItem(0)
