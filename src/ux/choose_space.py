from PyQt6 import QtWidgets

import src.ui as ui
from src.ux.task_list import SpaceMixin


class SpaceSelection(QtWidgets.QDialog, ui.choose_space.Ui_Dialog, SpaceMixin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.build_space_list()
        self.space.removeItem(0)
