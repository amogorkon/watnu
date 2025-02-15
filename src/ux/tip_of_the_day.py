import json
from pathlib import Path

import requests
from PyQt6 import QtCore, QtGui, QtWidgets

import src.ui as ui
from src import config

# Fetch tips.json instead of tips.py
try:
    response = requests.get("https://raw.githubusercontent.com/amogorkon/watnu/main/tips.json")
    response.raise_for_status()
    tips = json.loads(response.content)
except (requests.RequestException, json.JSONDecodeError):
    tips_json_path = Path(__file__).resolve().parent.parent.parent / "tips.json"
    tips = json.loads(tips_json_path.read_text())


already_checked = set(config.read_totds)
available_tips = {tip['name'] for tip in tips['TIPS']} - already_checked


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
            tip = next(t for t in tips['TIPS'] if t['name'] == name)
            page = QtWidgets.QWizardPage()
            page.setObjectName(f"wizardPage_{tip['name']}")
            verticalLayout = QtWidgets.QVBoxLayout(page)
            verticalLayout.setObjectName("verticalLayout")
            tip_text = QtWidgets.QLabel(parent=page)
            tip_text.setObjectName("tip_text")
            tip_text.setText(tip[config.language])
            verticalLayout.addWidget(tip_text)
            tip_visual = QtWidgets.QLabel(parent=page)
            tip_visual.setObjectName("tip_visual")
            # tip.img_url is a str url to the image, so we load it from the web and display it as pixmap
            if tip['img_url'] is not None:
                response = requests.get(tip['img_url'])
                image_data = response.content
                pixmap = QtGui.QPixmap()
                loaded = pixmap.loadFromData(image_data, "PNG")
                assert loaded, breakpoint()
                # now that we are sure to have something to display, resize the label to the image size
                tip_visual.setMaximumHeight(max(pixmap.width(), tip_text.width()))

                tip_visual.setScaledContents(False)
                tip_visual.setPixmap(
                    pixmap.scaled(
                        tip_visual.size(),
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation,
                    )
                )
            verticalLayout.addWidget(tip_visual)
            spacerItem = QtWidgets.QSpacerItem(
                20,
                40,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            )
            verticalLayout.addItem(spacerItem)
            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setContentsMargins(-1, 10, -1, -1)
            horizontalLayout.setObjectName("horizontalLayout")
            feedback_input = QtWidgets.QTextEdit(parent=page)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum,
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
