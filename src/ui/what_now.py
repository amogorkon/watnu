# Form implementation generated from reading ui file 'src\ui\what_now.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        Dialog.setEnabled(True)
        Dialog.resize(765, 458)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src\\ui\\../extra/watnu1.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        Dialog.setWindowIcon(icon)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.priority = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.priority.sizePolicy().hasHeightForWidth())
        self.priority.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.priority.setFont(font)
        self.priority.setMouseTracking(True)
        self.priority.setTabletTracking(True)
        self.priority.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
        self.priority.setTitle("")
        self.priority.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.priority.setFlat(False)
        self.priority.setCheckable(False)
        self.priority.setObjectName("priority")
        self.gridLayout = QtWidgets.QGridLayout(self.priority)
        self.gridLayout.setObjectName("gridLayout")
        self.task_desc_priority = QtWidgets.QLabel(parent=self.priority)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_desc_priority.sizePolicy().hasHeightForWidth())
        self.task_desc_priority.setSizePolicy(sizePolicy)
        self.task_desc_priority.setMinimumSize(QtCore.QSize(195, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.task_desc_priority.setFont(font)
        self.task_desc_priority.setMouseTracking(False)
        self.task_desc_priority.setToolTip("")
        self.task_desc_priority.setAutoFillBackground(True)
        self.task_desc_priority.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.task_desc_priority.setText("")
        self.task_desc_priority.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.task_desc_priority.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignJustify | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.task_desc_priority.setWordWrap(True)
        self.task_desc_priority.setOpenExternalLinks(False)
        self.task_desc_priority.setObjectName("task_desc_priority")
        self.gridLayout.addWidget(self.task_desc_priority, 4, 0, 1, 1)
        self.priority_header = QtWidgets.QHBoxLayout()
        self.priority_header.setContentsMargins(-1, 0, -1, -1)
        self.priority_header.setObjectName("priority_header")
        self.frame_priority = QtWidgets.QFrame(parent=self.priority)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.frame_priority.sizePolicy().hasHeightForWidth())
        self.frame_priority.setSizePolicy(sizePolicy)
        self.frame_priority.setMinimumSize(QtCore.QSize(9, 0))
        self.frame_priority.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_priority.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_priority.setObjectName("frame_priority")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_priority)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.task_space_priority = QtWidgets.QLabel(parent=self.frame_priority)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space_priority.sizePolicy().hasHeightForWidth())
        self.task_space_priority.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        font.setKerning(True)
        self.task_space_priority.setFont(font)
        self.task_space_priority.setText("")
        self.task_space_priority.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading
            | QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.task_space_priority.setObjectName("task_space_priority")
        self.horizontalLayout.addWidget(self.task_space_priority)
        self.priority_header.addWidget(self.frame_priority)
        self.gridLayout.addLayout(self.priority_header, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.horizontalLayout_5.addWidget(self.priority)
        self.timing = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timing.sizePolicy().hasHeightForWidth())
        self.timing.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.timing.setFont(font)
        self.timing.setTitle("")
        self.timing.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.timing.setObjectName("timing")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.timing)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.task_desc_timing = QtWidgets.QLabel(parent=self.timing)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_desc_timing.sizePolicy().hasHeightForWidth())
        self.task_desc_timing.setSizePolicy(sizePolicy)
        self.task_desc_timing.setMinimumSize(QtCore.QSize(195, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.task_desc_timing.setFont(font)
        self.task_desc_timing.setToolTip("")
        self.task_desc_timing.setAutoFillBackground(False)
        self.task_desc_timing.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.task_desc_timing.setText("")
        self.task_desc_timing.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.task_desc_timing.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignJustify | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.task_desc_timing.setWordWrap(True)
        self.task_desc_timing.setOpenExternalLinks(False)
        self.task_desc_timing.setObjectName("task_desc_timing")
        self.gridLayout_2.addWidget(self.task_desc_timing, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.gridLayout_2.addItem(spacerItem1, 4, 0, 1, 1)
        self.timing_header = QtWidgets.QHBoxLayout()
        self.timing_header.setContentsMargins(-1, 0, -1, -1)
        self.timing_header.setObjectName("timing_header")
        self.frame_timing = QtWidgets.QFrame(parent=self.timing)
        self.frame_timing.setMinimumSize(QtCore.QSize(9, 0))
        self.frame_timing.setBaseSize(QtCore.QSize(9, 0))
        self.frame_timing.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_timing.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_timing.setObjectName("frame_timing")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_timing)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.task_space_timing = QtWidgets.QLabel(parent=self.frame_timing)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space_timing.sizePolicy().hasHeightForWidth())
        self.task_space_timing.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.task_space_timing.setFont(font)
        self.task_space_timing.setText("")
        self.task_space_timing.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading
            | QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.task_space_timing.setObjectName("task_space_timing")
        self.horizontalLayout_2.addWidget(self.task_space_timing)
        self.timing_header.addWidget(self.frame_timing)
        self.gridLayout_2.addLayout(self.timing_header, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.timing)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Reference Sans Serif")
        font.setPointSize(7)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.deadline_weeks = QtWidgets.QLCDNumber(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_weeks.sizePolicy().hasHeightForWidth())
        self.deadline_weeks.setSizePolicy(sizePolicy)
        self.deadline_weeks.setDigitCount(4)
        self.deadline_weeks.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.deadline_weeks.setObjectName("deadline_weeks")
        self.horizontalLayout_3.addWidget(self.deadline_weeks)
        self.deadline_days = QtWidgets.QLCDNumber(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_days.sizePolicy().hasHeightForWidth())
        self.deadline_days.setSizePolicy(sizePolicy)
        self.deadline_days.setDigitCount(2)
        self.deadline_days.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.deadline_days.setObjectName("deadline_days")
        self.horizontalLayout_3.addWidget(self.deadline_days)
        self.deadline_hours = QtWidgets.QLCDNumber(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_hours.sizePolicy().hasHeightForWidth())
        self.deadline_hours.setSizePolicy(sizePolicy)
        self.deadline_hours.setDigitCount(3)
        self.deadline_hours.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.deadline_hours.setObjectName("deadline_hours")
        self.horizontalLayout_3.addWidget(self.deadline_hours)
        self.deadline_minutes = QtWidgets.QLCDNumber(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_minutes.sizePolicy().hasHeightForWidth())
        self.deadline_minutes.setSizePolicy(sizePolicy)
        self.deadline_minutes.setDigitCount(3)
        self.deadline_minutes.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.deadline_minutes.setObjectName("deadline_minutes")
        self.horizontalLayout_3.addWidget(self.deadline_minutes)
        self.deadline_seconds = QtWidgets.QLCDNumber(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_seconds.sizePolicy().hasHeightForWidth())
        self.deadline_seconds.setSizePolicy(sizePolicy)
        self.deadline_seconds.setDigitCount(3)
        self.deadline_seconds.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.deadline_seconds.setObjectName("deadline_seconds")
        self.horizontalLayout_3.addWidget(self.deadline_seconds)
        self.gridLayout_2.addWidget(self.groupBox_2, 5, 0, 1, 1)
        self.horizontalLayout_5.addWidget(self.timing)
        self.balance = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.balance.sizePolicy().hasHeightForWidth())
        self.balance.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.balance.setFont(font)
        self.balance.setMouseTracking(False)
        self.balance.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.balance.setAcceptDrops(False)
        self.balance.setAutoFillBackground(False)
        self.balance.setTitle("")
        self.balance.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.balance.setObjectName("balance")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.balance)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.task_desc_balanced = QtWidgets.QLabel(parent=self.balance)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_desc_balanced.sizePolicy().hasHeightForWidth())
        self.task_desc_balanced.setSizePolicy(sizePolicy)
        self.task_desc_balanced.setMinimumSize(QtCore.QSize(195, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.task_desc_balanced.setFont(font)
        self.task_desc_balanced.setMouseTracking(False)
        self.task_desc_balanced.setToolTip("")
        self.task_desc_balanced.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.task_desc_balanced.setText("")
        self.task_desc_balanced.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.task_desc_balanced.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignJustify | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.task_desc_balanced.setWordWrap(True)
        self.task_desc_balanced.setOpenExternalLinks(False)
        self.task_desc_balanced.setObjectName("task_desc_balanced")
        self.gridLayout_3.addWidget(self.task_desc_balanced, 2, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.gridLayout_3.addItem(spacerItem2, 3, 1, 1, 1)
        self.balance_header = QtWidgets.QHBoxLayout()
        self.balance_header.setContentsMargins(-1, 0, -1, -1)
        self.balance_header.setObjectName("balance_header")
        self.frame_balanced = QtWidgets.QFrame(parent=self.balance)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_balanced.sizePolicy().hasHeightForWidth())
        self.frame_balanced.setSizePolicy(sizePolicy)
        self.frame_balanced.setMinimumSize(QtCore.QSize(9, 0))
        self.frame_balanced.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_balanced.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_balanced.setObjectName("frame_balanced")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_balanced)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.task_space_balanced = QtWidgets.QLabel(parent=self.frame_balanced)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space_balanced.sizePolicy().hasHeightForWidth())
        self.task_space_balanced.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.task_space_balanced.setFont(font)
        self.task_space_balanced.setText("")
        self.task_space_balanced.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading
            | QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.task_space_balanced.setObjectName("task_space_balanced")
        self.horizontalLayout_4.addWidget(self.task_space_balanced)
        self.balance_header.addWidget(self.frame_balanced)
        self.gridLayout_3.addLayout(self.balance_header, 0, 1, 1, 1)
        self.horizontalLayout_5.addWidget(self.balance)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.num_buttons = QtWidgets.QGridLayout()
        self.num_buttons.setContentsMargins(-1, 10, -1, -1)
        self.num_buttons.setObjectName("num_buttons")
        self.button9 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button9.setFont(font)
        self.button9.setAutoDefault(False)
        self.button9.setObjectName("button9")
        self.num_buttons.addWidget(self.button9, 0, 2, 1, 1)
        self.button7 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button7.setFont(font)
        self.button7.setAutoDefault(False)
        self.button7.setObjectName("button7")
        self.num_buttons.addWidget(self.button7, 0, 0, 1, 1)
        self.button8 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button8.setFont(font)
        self.button8.setAutoDefault(False)
        self.button8.setObjectName("button8")
        self.num_buttons.addWidget(self.button8, 0, 1, 1, 1)
        self.button6 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button6.setFont(font)
        self.button6.setText("")
        self.button6.setAutoDefault(False)
        self.button6.setObjectName("button6")
        self.num_buttons.addWidget(self.button6, 1, 2, 1, 1)
        self.button5 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button5.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap("src\\ui\\../extra/coin.svg"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.button5.setIcon(icon1)
        self.button5.setAutoDefault(False)
        self.button5.setObjectName("button5")
        self.num_buttons.addWidget(self.button5, 1, 1, 1, 1)
        self.button3 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button3.setFont(font)
        self.button3.setText("")
        self.button3.setAutoDefault(False)
        self.button3.setObjectName("button3")
        self.num_buttons.addWidget(self.button3, 2, 2, 1, 1)
        self.button2 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button2.setFont(font)
        self.button2.setText("")
        self.button2.setAutoDefault(False)
        self.button2.setObjectName("button2")
        self.num_buttons.addWidget(self.button2, 2, 1, 1, 1)
        self.button4 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button4.setFont(font)
        self.button4.setText("")
        self.button4.setAutoDefault(False)
        self.button4.setObjectName("button4")
        self.num_buttons.addWidget(self.button4, 1, 0, 1, 1)
        self.button1 = QtWidgets.QPushButton(parent=Dialog)
        font = QtGui.QFont()
        font.setItalic(False)
        self.button1.setFont(font)
        self.button1.setText("")
        self.button1.setAutoDefault(False)
        self.button1.setObjectName("button1")
        self.num_buttons.addWidget(self.button1, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.num_buttons)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Was jetzt?"))
        self.groupBox_2.setTitle(
            _translate(
                "Dialog",
                "Weeks        Days          Hours    Minutes   Seconds",
            )
        )
        self.button9.setText(_translate("Dialog", "Aufgabe - Balance..."))
        self.button9.setShortcut(_translate("Dialog", "9"))
        self.button7.setText(_translate("Dialog", "Aufgabe - Priorität..."))
        self.button7.setShortcut(_translate("Dialog", "7"))
        self.button8.setText(_translate("Dialog", "Aufgabe - Timing..."))
        self.button8.setShortcut(_translate("Dialog", "8"))
        self.button6.setShortcut(_translate("Dialog", "6"))
        self.button5.setText(_translate("Dialog", "Wirf Münze"))
        self.button5.setShortcut(_translate("Dialog", "5"))
        self.button3.setShortcut(_translate("Dialog", "3"))
        self.button2.setShortcut(_translate("Dialog", "2"))
        self.button4.setShortcut(_translate("Dialog", "4"))
        self.button1.setShortcut(_translate("Dialog", "1"))
