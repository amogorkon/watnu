# Form implementation generated from reading ui file 'ui\task_running.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(627, 540)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.LCD_days = QtWidgets.QLCDNumber(parent=self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(120)
        font.setBold(True)
        font.setWeight(75)
        self.LCD_days.setFont(font)
        self.LCD_days.setDigitCount(4)
        self.LCD_days.setObjectName("LCD_days")
        self.horizontalLayout.addWidget(self.LCD_days)
        self.LCD_hours = QtWidgets.QLCDNumber(parent=self.groupBox)
        self.LCD_hours.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LCD_hours.sizePolicy().hasHeightForWidth())
        self.LCD_hours.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(120)
        font.setBold(True)
        font.setWeight(75)
        self.LCD_hours.setFont(font)
        self.LCD_hours.setDigitCount(2)
        self.LCD_hours.setProperty("intValue", 0)
        self.LCD_hours.setObjectName("LCD_hours")
        self.horizontalLayout.addWidget(self.LCD_hours)
        self.LCD_minutes = QtWidgets.QLCDNumber(parent=self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(120)
        self.LCD_minutes.setFont(font)
        self.LCD_minutes.setDigitCount(2)
        self.LCD_minutes.setObjectName("LCD_minutes")
        self.horizontalLayout.addWidget(self.LCD_minutes)
        self.LCD_seconds = QtWidgets.QLCDNumber(parent=self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(120)
        self.LCD_seconds.setFont(font)
        self.LCD_seconds.setDigitCount(2)
        self.LCD_seconds.setObjectName("LCD_seconds")
        self.horizontalLayout.addWidget(self.LCD_seconds)
        self.verticalLayout.addWidget(self.groupBox)
        self.tabWidget = QtWidgets.QTabWidget(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.common = QtWidgets.QWidget()
        self.common.setObjectName("common")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.common)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame = QtWidgets.QFrame(parent=self.common)
        self.frame.setSizeIncrement(QtCore.QSize(0, 10))
        self.frame.setBaseSize(QtCore.QSize(0, 10))
        self.frame.setAutoFillBackground(True)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(9, -1, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.task_space = QtWidgets.QLabel(parent=self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space.sizePolicy().hasHeightForWidth())
        self.task_space.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(50)
        self.task_space.setFont(font)
        self.task_space.setText("")
        self.task_space.setWordWrap(False)
        self.task_space.setObjectName("task_space")
        self.horizontalLayout_3.addWidget(self.task_space)
        self.horizontalLayout_2.addWidget(self.frame)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.desc = QtWidgets.QTextEdit(parent=self.common)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.desc.sizePolicy().hasHeightForWidth())
        self.desc.setSizePolicy(sizePolicy)
        self.desc.setLineWidth(1)
        self.desc.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.desc.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow
        )
        self.desc.setUndoRedoEnabled(False)
        self.desc.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.FixedColumnWidth)
        self.desc.setLineWrapColumnOrWidth(95)
        self.desc.setReadOnly(True)
        self.desc.setObjectName("desc")
        self.verticalLayout_2.addWidget(self.desc)
        spacerItem = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.verticalLayout_2.addItem(spacerItem)
        self.open_resources = QtWidgets.QPushButton(parent=self.common)
        self.open_resources.setEnabled(False)
        self.open_resources.setText("")
        self.open_resources.setObjectName("open_resources")
        self.verticalLayout_2.addWidget(self.open_resources)
        self.notes = QtWidgets.QTextEdit(parent=self.common)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.notes.sizePolicy().hasHeightForWidth())
        self.notes.setSizePolicy(sizePolicy)
        self.notes.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.notes.setAutoFormatting(QtWidgets.QTextEdit.AutoFormattingFlag.AutoAll)
        self.notes.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.FixedColumnWidth)
        self.notes.setLineWrapColumnOrWidth(95)
        self.notes.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard
            | QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
            | QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
            | QtCore.Qt.TextInteractionFlag.TextEditable
            | QtCore.Qt.TextInteractionFlag.TextEditorInteraction
            | QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard
            | QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.notes.setObjectName("notes")
        self.verticalLayout_2.addWidget(self.notes)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.verticalLayout_2.addItem(spacerItem1)
        self.tabWidget.addTab(self.common, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.button9 = QtWidgets.QPushButton(parent=Dialog)
        self.button9.setEnabled(True)
        self.button9.setAutoDefault(True)
        self.button9.setObjectName("button9")
        self.gridLayout.addWidget(self.button9, 4, 2, 1, 1)
        self.button5 = QtWidgets.QPushButton(parent=Dialog)
        self.button5.setEnabled(True)
        self.button5.setAutoDefault(True)
        self.button5.setObjectName("button5")
        self.gridLayout.addWidget(self.button5, 5, 1, 1, 1)
        self.button8 = QtWidgets.QPushButton(parent=Dialog)
        self.button8.setAutoDefault(True)
        self.button8.setDefault(False)
        self.button8.setObjectName("button8")
        self.gridLayout.addWidget(self.button8, 4, 1, 1, 1)
        self.button6 = QtWidgets.QPushButton(parent=Dialog)
        self.button6.setEnabled(True)
        self.button6.setAutoDefault(True)
        self.button6.setDefault(False)
        self.button6.setObjectName("button6")
        self.gridLayout.addWidget(self.button6, 5, 2, 1, 1)
        self.button4 = QtWidgets.QPushButton(parent=Dialog)
        self.button4.setEnabled(False)
        self.button4.setText("")
        self.button4.setAutoDefault(True)
        self.button4.setObjectName("button4")
        self.gridLayout.addWidget(self.button4, 5, 0, 1, 1)
        self.button2 = QtWidgets.QPushButton(parent=Dialog)
        self.button2.setAutoDefault(True)
        self.button2.setDefault(True)
        self.button2.setObjectName("button2")
        self.gridLayout.addWidget(self.button2, 7, 1, 1, 1)
        self.button3 = QtWidgets.QPushButton(parent=Dialog)
        self.button3.setAutoDefault(True)
        self.button3.setDefault(False)
        self.button3.setObjectName("button3")
        self.gridLayout.addWidget(self.button3, 7, 2, 1, 1)
        self.button1 = QtWidgets.QPushButton(parent=Dialog)
        self.button1.setEnabled(False)
        self.button1.setText("")
        self.button1.setAutoDefault(True)
        self.button1.setObjectName("button1")
        self.gridLayout.addWidget(self.button1, 7, 0, 1, 1)
        self.button7 = QtWidgets.QPushButton(parent=Dialog)
        self.button7.setEnabled(True)
        self.button7.setAutoDefault(True)
        self.button7.setObjectName("button7")
        self.gridLayout.addWidget(self.button7, 4, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Läuft.."))
        self.groupBox.setTitle(_translate("Dialog", "Zeit mit Aufgabe"))
        self.notes.setPlaceholderText(_translate("Dialog", "Notizen"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.common), _translate("Dialog", "Beschreibung"))
        self.button9.setText(_translate("Dialog", "+5"))
        self.button9.setShortcut(_translate("Dialog", "9"))
        self.button5.setText(_translate("Dialog", "später weiter"))
        self.button5.setShortcut(_translate("Dialog", "5"))
        self.button8.setText(_translate("Dialog", "Aufgabe beendet"))
        self.button8.setShortcut(_translate("Dialog", "8"))
        self.button6.setText(_translate("Dialog", "erstelle neue Aufgabe (Entwurf)"))
        self.button6.setShortcut(_translate("Dialog", "6"))
        self.button4.setShortcut(_translate("Dialog", "4"))
        self.button2.setText(_translate("Dialog", "Pause"))
        self.button2.setShortcut(_translate("Dialog", "2"))
        self.button3.setText(_translate("Dialog", "Zurücksetzen"))
        self.button3.setShortcut(_translate("Dialog", "3"))
        self.button1.setShortcut(_translate("Dialog", "1"))
        self.button7.setText(_translate("Dialog", "-5"))
        self.button7.setShortcut(_translate("Dialog", "7"))
