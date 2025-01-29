from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication

import src.ui as ui
from src.version import __version__

_translate = QCoreApplication.translate


class About(QtWidgets.QDialog, ui.about.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.version.setText(str(__version__))
