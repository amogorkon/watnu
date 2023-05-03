from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

import src.ui as ui
from src.stuff import config


class Companions(QtWidgets.QDialog, ui.companions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.face_left.setPixmap(QtGui.QPixmap(str(config.base_path / "extra/faces/face1.png")))
        self.face_right.setPixmap(QtGui.QPixmap(str(config.base_path / "extra/faces/face3.png")))

        bing_chat_url = QUrl("bing.com/chat")

        self.browser = QWebEngineView()
        self.browser.load(bing_chat_url)
        # self.horizontalLayout.addWidget(self.browser)

    def reject(self):
        super().reject()
