from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication


import ui
from stuff import __version__

_translate = QCoreApplication.translate

class Companions(QtWidgets.QDialog, ui.companions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def reject(self):
        super().reject()
        win_companions = None
