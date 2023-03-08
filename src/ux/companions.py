
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication

_translate = QCoreApplication.translate

import ui

from .stuff import app, db, config, __version__

class Companions(QtWidgets.QDialog, ui.companions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def reject(self):
        super().reject()
        win_companions = None
