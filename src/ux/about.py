import sys

import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtCore import PYQT_VERSION_STR, QCoreApplication

import src.ui as ui
from src.version import __version__

_translate = QCoreApplication.translate


class About(QtWidgets.QDialog, ui.about.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        text = f"""
Watnu Version: {__version__[0]}.{__version__[1]}.{__version__[2]}
Python Version: {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}
PyQt Version: {PYQT_VERSION_STR}
NumPy Version: {np.__version__}
"""
        self.version.setText(text)
