import requests
import use
from PyQt6 import QtCore, QtGui, QtWidgets

import src.ui as ui
import tips as current_tips
from src.stuff import config

online_tips = use(use.URL("https://raw.githubusercontent.com/amogorkon/watnu/main/tips.py"))

actual_tips = max(current_tips, online_tips, key=lambda mod: mod.version)

already_checked = set(config.read_totds)
available_tips = {tip.name for tip in actual_tips.tips} - already_checked


class TipOfTheDay(QtWidgets.QWizard, ui.tip_of_the_day.Ui_Wizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

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
        for name in available_tips:
            tip = getattr(actual_tips.tips, name)
            page = QtWidgets.QWizardPage()
            page.setObjectName(f"wizardPage_{tip.name}")
            verticalLayout = QtWidgets.QVBoxLayout(page)
            verticalLayout.setObjectName("verticalLayout")
            tip_text = QtWidgets.QLabel(parent=page)
            tip_text.setObjectName("tip_text")
            tip_text.setText(tip.de)
            verticalLayout.addWidget(tip_text)
            tip_visual = QtWidgets.QLabel(parent=page)
            # tip.img_url is a str url to the image, so we load it from the web and display it as pixmap
            if tip.img_url is not None:
                response = requests.get(tip.img_url)
                image_data = response.content
                pixmap = QtGui.QPixmap()
                loaded = pixmap.loadFromData(image_data, "PNG")
                assert loaded, breakpoint()
                tip_visual.setPixmap(pixmap)
                tip_visual.setScaledContents(True)
                tip_visual.setObjectName("tip_visual")
                tip_visual.show()
            verticalLayout.addWidget(tip_visual)
            spacerItem = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.MinimumExpanding
            )
            verticalLayout.addItem(spacerItem)
            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setContentsMargins(-1, 10, -1, -1)
            horizontalLayout.setObjectName("horizontalLayout")
            feedback_input = QtWidgets.QTextEdit(parent=page)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
            )
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(feedback_input.sizePolicy().hasHeightForWidth())
            feedback_input.setSizePolicy(sizePolicy)
            feedback_input.setObjectName("feedback_input")
            horizontalLayout.addWidget(feedback_input)
            good_button = QtWidgets.QPushButton(parent=page)
            good_button.setText("")
            icon1 = QtGui.QIcon()
            icon1.addPixmap(
                QtGui.QPixmap("src\\ui\\../extra/feathericons/thumbs-up.svg"),
                QtGui.QIcon.Mode.Normal,
                QtGui.QIcon.State.Off,
            )
            good_button.setIcon(icon1)
            good_button.setObjectName("good_button")
            horizontalLayout.addWidget(good_button)
            bad_button = QtWidgets.QPushButton(parent=page)
            bad_button.setText("")
            icon2 = QtGui.QIcon()
            icon2.addPixmap(
                QtGui.QPixmap("src\\ui\\../extra/feathericons/thumbs-down.svg"),
                QtGui.QIcon.Mode.Normal,
                QtGui.QIcon.State.Off,
            )
            bad_button.setIcon(icon2)
            bad_button.setObjectName("bad_button")
            horizontalLayout.addWidget(bad_button)
            verticalLayout.addLayout(horizontalLayout)
            self.addPage(page)

        # set up the wizard buttons
        self.setButtonText(QtWidgets.QWizard.WizardButton.NextButton, "Next")
        self.setButtonText(QtWidgets.QWizard.WizardButton.BackButton, "Back")
        self.setButtonText(QtWidgets.QWizard.WizardButton.FinishButton, "Close")
        self.setButtonText(QtWidgets.QWizard.WizardButton.CancelButton, "Close")
