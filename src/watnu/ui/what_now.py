# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\what_now.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(752, 458)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.priority = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
        self.priority.setFocusPolicy(QtCore.Qt.TabFocus)
        self.priority.setTitle("")
        self.priority.setAlignment(QtCore.Qt.AlignCenter)
        self.priority.setFlat(False)
        self.priority.setCheckable(False)
        self.priority.setObjectName("priority")
        self.gridLayout = QtWidgets.QGridLayout(self.priority)
        self.gridLayout.setObjectName("gridLayout")
        self.done_priority = QtWidgets.QPushButton(self.priority)
        font = QtGui.QFont()
        font.setItalic(False)
        self.done_priority.setFont(font)
        self.done_priority.setObjectName("done_priority")
        self.gridLayout.addWidget(self.done_priority, 7, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 1)
        self.go_priority = QtWidgets.QPushButton(self.priority)
        font = QtGui.QFont()
        font.setItalic(False)
        self.go_priority.setFont(font)
        self.go_priority.setAutoDefault(False)
        self.go_priority.setObjectName("go_priority")
        self.gridLayout.addWidget(self.go_priority, 8, 0, 1, 1)
        self.skip_priority = QtWidgets.QPushButton(self.priority)
        font = QtGui.QFont()
        font.setItalic(False)
        self.skip_priority.setFont(font)
        self.skip_priority.setAutoDefault(False)
        self.skip_priority.setObjectName("skip_priority")
        self.gridLayout.addWidget(self.skip_priority, 9, 0, 1, 1)
        self.task_desc_priority = QtWidgets.QLabel(self.priority)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
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
        self.task_desc_priority.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.task_desc_priority.setText("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum ")
        self.task_desc_priority.setTextFormat(QtCore.Qt.PlainText)
        self.task_desc_priority.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.task_desc_priority.setWordWrap(True)
        self.task_desc_priority.setOpenExternalLinks(False)
        self.task_desc_priority.setObjectName("task_desc_priority")
        self.gridLayout.addWidget(self.task_desc_priority, 5, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.priority)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 1)
        self.priority_header = QtWidgets.QHBoxLayout()
        self.priority_header.setContentsMargins(-1, 0, -1, -1)
        self.priority_header.setObjectName("priority_header")
        self.frame_priority = QtWidgets.QFrame(self.priority)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.frame_priority.sizePolicy().hasHeightForWidth())
        self.frame_priority.setSizePolicy(sizePolicy)
        self.frame_priority.setMinimumSize(QtCore.QSize(9, 0))
        self.frame_priority.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_priority.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_priority.setObjectName("frame_priority")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_priority)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.task_space_priority = QtWidgets.QLabel(self.frame_priority)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space_priority.sizePolicy().hasHeightForWidth())
        self.task_space_priority.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        font.setKerning(True)
        self.task_space_priority.setFont(font)
        self.task_space_priority.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.task_space_priority.setObjectName("task_space_priority")
        self.horizontalLayout.addWidget(self.task_space_priority)
        self.priority_header.addWidget(self.frame_priority)
        self.gridLayout.addLayout(self.priority_header, 4, 0, 1, 1)
        self.horizontalLayout_5.addWidget(self.priority)
        self.timing = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timing.sizePolicy().hasHeightForWidth())
        self.timing.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.timing.setFont(font)
        self.timing.setTitle("")
        self.timing.setAlignment(QtCore.Qt.AlignCenter)
        self.timing.setObjectName("timing")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.timing)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.timing)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
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
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.deadline_weeks = QtWidgets.QLCDNumber(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_weeks.sizePolicy().hasHeightForWidth())
        self.deadline_weeks.setSizePolicy(sizePolicy)
        self.deadline_weeks.setDigitCount(5)
        self.deadline_weeks.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.deadline_weeks.setObjectName("deadline_weeks")
        self.horizontalLayout_3.addWidget(self.deadline_weeks)
        self.deadline_days = QtWidgets.QLCDNumber(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_days.sizePolicy().hasHeightForWidth())
        self.deadline_days.setSizePolicy(sizePolicy)
        self.deadline_days.setDigitCount(2)
        self.deadline_days.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.deadline_days.setObjectName("deadline_days")
        self.horizontalLayout_3.addWidget(self.deadline_days)
        self.deadline_hours = QtWidgets.QLCDNumber(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_hours.sizePolicy().hasHeightForWidth())
        self.deadline_hours.setSizePolicy(sizePolicy)
        self.deadline_hours.setDigitCount(3)
        self.deadline_hours.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.deadline_hours.setObjectName("deadline_hours")
        self.horizontalLayout_3.addWidget(self.deadline_hours)
        self.deadline_minutes = QtWidgets.QLCDNumber(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_minutes.sizePolicy().hasHeightForWidth())
        self.deadline_minutes.setSizePolicy(sizePolicy)
        self.deadline_minutes.setDigitCount(3)
        self.deadline_minutes.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.deadline_minutes.setObjectName("deadline_minutes")
        self.horizontalLayout_3.addWidget(self.deadline_minutes)
        self.deadline_seconds = QtWidgets.QLCDNumber(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline_seconds.sizePolicy().hasHeightForWidth())
        self.deadline_seconds.setSizePolicy(sizePolicy)
        self.deadline_seconds.setDigitCount(3)
        self.deadline_seconds.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.deadline_seconds.setObjectName("deadline_seconds")
        self.horizontalLayout_3.addWidget(self.deadline_seconds)
        self.gridLayout_2.addWidget(self.groupBox_2, 6, 0, 1, 1)
        self.done_timing = QtWidgets.QPushButton(self.timing)
        font = QtGui.QFont()
        font.setItalic(False)
        self.done_timing.setFont(font)
        self.done_timing.setObjectName("done_timing")
        self.gridLayout_2.addWidget(self.done_timing, 7, 0, 1, 1)
        self.task_desc_timing = QtWidgets.QLabel(self.timing)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
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
        self.task_desc_timing.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.task_desc_timing.setText("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum ")
        self.task_desc_timing.setTextFormat(QtCore.Qt.PlainText)
        self.task_desc_timing.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.task_desc_timing.setWordWrap(True)
        self.task_desc_timing.setOpenExternalLinks(False)
        self.task_desc_timing.setObjectName("task_desc_timing")
        self.gridLayout_2.addWidget(self.task_desc_timing, 4, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 5, 0, 1, 1)
        self.skip_timing = QtWidgets.QPushButton(self.timing)
        font = QtGui.QFont()
        font.setItalic(False)
        self.skip_timing.setFont(font)
        self.skip_timing.setAutoDefault(False)
        self.skip_timing.setObjectName("skip_timing")
        self.gridLayout_2.addWidget(self.skip_timing, 9, 0, 1, 1)
        self.go_timing = QtWidgets.QPushButton(self.timing)
        font = QtGui.QFont()
        font.setItalic(False)
        self.go_timing.setFont(font)
        self.go_timing.setAutoDefault(False)
        self.go_timing.setObjectName("go_timing")
        self.gridLayout_2.addWidget(self.go_timing, 8, 0, 1, 1)
        self.timing_header = QtWidgets.QHBoxLayout()
        self.timing_header.setContentsMargins(-1, 0, -1, -1)
        self.timing_header.setObjectName("timing_header")
        self.frame_timing = QtWidgets.QFrame(self.timing)
        self.frame_timing.setMinimumSize(QtCore.QSize(9, 0))
        self.frame_timing.setBaseSize(QtCore.QSize(9, 0))
        self.frame_timing.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_timing.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_timing.setObjectName("frame_timing")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_timing)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.task_space_timing = QtWidgets.QLabel(self.frame_timing)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space_timing.sizePolicy().hasHeightForWidth())
        self.task_space_timing.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.task_space_timing.setFont(font)
        self.task_space_timing.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.task_space_timing.setObjectName("task_space_timing")
        self.horizontalLayout_2.addWidget(self.task_space_timing)
        self.timing_header.addWidget(self.frame_timing)
        self.gridLayout_2.addLayout(self.timing_header, 2, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.timing)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.gridLayout_2.addWidget(self.frame_2, 0, 0, 1, 1)
        self.horizontalLayout_5.addWidget(self.timing)
        self.balance = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.balance.sizePolicy().hasHeightForWidth())
        self.balance.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.balance.setFont(font)
        self.balance.setMouseTracking(False)
        self.balance.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.balance.setAcceptDrops(False)
        self.balance.setAutoFillBackground(False)
        self.balance.setTitle("")
        self.balance.setAlignment(QtCore.Qt.AlignCenter)
        self.balance.setObjectName("balance")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.balance)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.done_balanced = QtWidgets.QPushButton(self.balance)
        font = QtGui.QFont()
        font.setItalic(False)
        self.done_balanced.setFont(font)
        self.done_balanced.setObjectName("done_balanced")
        self.gridLayout_3.addWidget(self.done_balanced, 5, 1, 1, 1)
        self.skip_balanced = QtWidgets.QPushButton(self.balance)
        font = QtGui.QFont()
        font.setItalic(False)
        self.skip_balanced.setFont(font)
        self.skip_balanced.setAutoDefault(False)
        self.skip_balanced.setObjectName("skip_balanced")
        self.gridLayout_3.addWidget(self.skip_balanced, 7, 1, 1, 1)
        self.task_desc_balanced = QtWidgets.QLabel(self.balance)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
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
        self.task_desc_balanced.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.task_desc_balanced.setText("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum ")
        self.task_desc_balanced.setTextFormat(QtCore.Qt.PlainText)
        self.task_desc_balanced.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.task_desc_balanced.setWordWrap(True)
        self.task_desc_balanced.setOpenExternalLinks(False)
        self.task_desc_balanced.setObjectName("task_desc_balanced")
        self.gridLayout_3.addWidget(self.task_desc_balanced, 3, 1, 1, 1)
        self.go_balanced = QtWidgets.QPushButton(self.balance)
        font = QtGui.QFont()
        font.setItalic(False)
        self.go_balanced.setFont(font)
        self.go_balanced.setAutoDefault(False)
        self.go_balanced.setObjectName("go_balanced")
        self.gridLayout_3.addWidget(self.go_balanced, 6, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem2, 4, 1, 1, 1)
        self.balance_header = QtWidgets.QHBoxLayout()
        self.balance_header.setContentsMargins(-1, 0, -1, -1)
        self.balance_header.setObjectName("balance_header")
        self.frame_balanced = QtWidgets.QFrame(self.balance)
        self.frame_balanced.setMinimumSize(QtCore.QSize(9, 0))
        self.frame_balanced.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_balanced.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_balanced.setObjectName("frame_balanced")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_balanced)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.task_space_balanced = QtWidgets.QLabel(self.frame_balanced)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_space_balanced.sizePolicy().hasHeightForWidth())
        self.task_space_balanced.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.task_space_balanced.setFont(font)
        self.task_space_balanced.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.task_space_balanced.setObjectName("task_space_balanced")
        self.horizontalLayout_4.addWidget(self.task_space_balanced)
        self.balance_header.addWidget(self.frame_balanced)
        self.gridLayout_3.addLayout(self.balance_header, 1, 1, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.balance)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.frame_3)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.gridLayout_3.addWidget(self.frame_3, 0, 1, 1, 1)
        self.horizontalLayout_5.addWidget(self.balance)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.cancel = QtWidgets.QPushButton(Dialog)
        self.cancel.setAutoDefault(True)
        self.cancel.setDefault(True)
        self.cancel.setObjectName("cancel")
        self.verticalLayout.addWidget(self.cancel)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Was jetzt?"))
        self.done_priority.setText(_translate("Dialog", "Schon erledigt"))
        self.done_priority.setShortcut(_translate("Dialog", "7"))
        self.go_priority.setText(_translate("Dialog", "Go!"))
        self.go_priority.setShortcut(_translate("Dialog", "4"))
        self.skip_priority.setText(_translate("Dialog", "Nicht jetzt"))
        self.skip_priority.setShortcut(_translate("Dialog", "1"))
        self.label_4.setText(_translate("Dialog", "Priority"))
        self.task_space_priority.setText(_translate("Dialog", "test"))
        self.groupBox_2.setTitle(_translate("Dialog", "Weeks        Days          Hours    Minutes   Seconds"))
        self.done_timing.setText(_translate("Dialog", "Schon erledigt"))
        self.done_timing.setShortcut(_translate("Dialog", "8"))
        self.skip_timing.setText(_translate("Dialog", "Nicht jetzt"))
        self.skip_timing.setShortcut(_translate("Dialog", "2"))
        self.go_timing.setText(_translate("Dialog", "Go!"))
        self.go_timing.setShortcut(_translate("Dialog", "5"))
        self.task_space_timing.setText(_translate("Dialog", "test"))
        self.label_2.setText(_translate("Dialog", "Timing"))
        self.done_balanced.setText(_translate("Dialog", "Schon erledigt"))
        self.done_balanced.setShortcut(_translate("Dialog", "9"))
        self.skip_balanced.setText(_translate("Dialog", "Nicht jetzt"))
        self.skip_balanced.setShortcut(_translate("Dialog", "3"))
        self.go_balanced.setText(_translate("Dialog", "Go!"))
        self.go_balanced.setShortcut(_translate("Dialog", "6"))
        self.task_space_balanced.setText(_translate("Dialog", "test"))
        self.label_3.setText(_translate("Dialog", "Balance"))
        self.cancel.setText(_translate("Dialog", "Muss ich mir noch überlegen..."))
        self.cancel.setShortcut(_translate("Dialog", "Esc"))
