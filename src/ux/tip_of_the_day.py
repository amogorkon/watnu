import use
from PyQt6 import QtCore, QtGui, QtWidgets

import src.ui as ui
from tips import tips
from src.stuff import config

online_tips = use(use.URL("https://raw.githubusercontent.com/amogorkon/watnu/main/tips.py"))

tips = max(tips, online_tips, key=lambda x: x.version)

already_checked = set(config.read_totds)
available_tips = already_checked.difference({tip.name for tip in tips})


class TipOfTheDay(QtWidgets.QWizard, ui.tip_of_the_day.Ui_Wizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowTitleHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowSystemMenuHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMinMaxButtonsHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowShadeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowFullscreenButtonHint, False)

        # set up the wizard pages based on the tips
        for tip in available_tips:
            page = QtWidgets.QWizardPage()
            page.setTitle(tip.name)
            page.setSubTitle(tip.en)
            page.setPixmap(QtGui.QPixmap(tip.img_url))
            self.addPage(page)
