from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

import ui
from stuff import __version__


class Companions(QtWidgets.QDialog, ui.companions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        bing_chat_url = QUrl("bing.com/chat")

        self.browser = QWebEngineView()
        self.browser.load(bing_chat_url)
        # self.horizontalLayout.addWidget(self.browser)

    def reject(self):
        super().reject()
