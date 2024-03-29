# This work is dedicated to my loving partner and (soon to be) wife Sarah,
# whom I respect and adore above anything else.


from PyQt6 import QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView

import src.ui as ui


class Attributions(QtWidgets.QDialog, ui.attributions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.browser = QWebEngineView()
        with open("extra/attributions.html", "r") as f:
            html = f.read()
        self.browser.setHtml(html)
        self.verticalLayout.addWidget(self.browser)

    def reject(self):
        super().reject()
