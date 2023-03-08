from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication

_translate = QCoreApplication.translate

import ui

from .stuff import __version__


class About(QtWidgets.QDialog, ui.about.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.version.setText(str(__version__))
