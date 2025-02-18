from PyQt6 import QtWidgets

from src import ui

from .mixin import SpaceMixin


class SpaceSelection(QtWidgets.QDialog, ui.choose_space.Ui_Dialog, SpaceMixin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.build_space_list()
        self.space.removeItem(0)
