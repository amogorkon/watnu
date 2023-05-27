from PyQt6 import QtWidgets

import src.ui as ui
from src.ux.task_list import Space_Mixin


class Space_Selection(QtWidgets.QDialog, ui.choose_space.Ui_Dialog, Space_Mixin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.build_space_list()
        self.space.removeItem(0)
