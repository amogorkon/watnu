from PyQt6 import QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView

import src.ui as ui
from src import config


class Attributions(QtWidgets.QDialog, ui.attributions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.browser = QWebEngineView()
        html = (config.base_path / "extra/attributions.html").read_text()
        self.browser.setHtml(html)
        self.verticalLayout.addWidget(self.browser)

    def reject(self):
        super().reject()
