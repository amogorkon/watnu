# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\choose_deadline.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(928, 409)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.before_deadline = QtWidgets.QWidget()
        self.before_deadline.setObjectName("before_deadline")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.before_deadline)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(self.before_deadline)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tableWidget_3 = QtWidgets.QTableWidget(self.groupBox_2)
        self.tableWidget_3.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tableWidget_3.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.verticalLayout_4.addWidget(self.tableWidget_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.tableWidget_2 = QtWidgets.QTableWidget(self.groupBox_2)
        self.tableWidget_2.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tableWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.verticalLayout_4.addWidget(self.tableWidget_2)
        self.horizontalLayout_3.addWidget(self.groupBox_2)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 9, -1, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_4 = QtWidgets.QGroupBox(self.before_deadline)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_2.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../extra/feathericons/minus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("ui\\../extra/feathericons/plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon1)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.groupBox_5 = QtWidgets.QGroupBox(self.before_deadline)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_4.setText("")
        self.pushButton_4.setIcon(icon1)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 0, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_3.setText("")
        self.pushButton_3.setIcon(icon)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 1, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.before_deadline, "")
        self.deadline_details = QtWidgets.QWidget()
        self.deadline_details.setObjectName("deadline_details")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.deadline_details)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.deadline = QtWidgets.QDateTimeEdit(self.deadline_details)
        self.deadline.setAccelerated(False)
        self.deadline.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.deadline.setCalendarPopup(True)
        self.deadline.setObjectName("deadline")
        self.verticalLayout_6.addWidget(self.deadline)
        self.tabWidget.addTab(self.deadline_details, "")
        self.after_deadline = QtWidgets.QWidget()
        self.after_deadline.setObjectName("after_deadline")
        self.groupBox = QtWidgets.QGroupBox(self.after_deadline)
        self.groupBox.setGeometry(QtCore.QRect(60, 20, 380, 345))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tableWidget_4 = QtWidgets.QTableWidget(self.groupBox)
        self.tableWidget_4.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tableWidget_4.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setColumnCount(0)
        self.tableWidget_4.setRowCount(0)
        self.verticalLayout_3.addWidget(self.tableWidget_4)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_3.addWidget(self.tableWidget)
        self.pushButton_6 = QtWidgets.QPushButton(self.after_deadline)
        self.pushButton_6.setGeometry(QtCore.QRect(590, 160, 28, 24))
        self.pushButton_6.setText("")
        self.pushButton_6.setIcon(icon)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_5 = QtWidgets.QPushButton(self.after_deadline)
        self.pushButton_5.setGeometry(QtCore.QRect(590, 130, 28, 24))
        self.pushButton_5.setText("")
        self.pushButton_5.setIcon(icon1)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_7 = QtWidgets.QPushButton(self.after_deadline)
        self.pushButton_7.setGeometry(QtCore.QRect(690, 60, 28, 24))
        self.pushButton_7.setText("")
        self.pushButton_7.setIcon(icon1)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QtWidgets.QPushButton(self.after_deadline)
        self.pushButton_8.setGeometry(QtCore.QRect(690, 90, 28, 24))
        self.pushButton_8.setText("")
        self.pushButton_8.setIcon(icon)
        self.pushButton_8.setObjectName("pushButton_8")
        self.tabWidget.addTab(self.after_deadline, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Discard|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox_2.setTitle(_translate("Dialog", "Vor dem Stichtag"))
        self.groupBox_4.setTitle(_translate("Dialog", "Dringlichkeit"))
        self.groupBox_5.setTitle(_translate("Dialog", "Wert bei Erledigung"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.before_deadline), _translate("Dialog", "vor Deadline"))
        self.deadline.setSpecialValueText(_translate("Dialog", "\"Never\""))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.deadline_details), _translate("Dialog", "Deadline Details"))
        self.groupBox.setTitle(_translate("Dialog", "Nach dem Stichtag"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.after_deadline), _translate("Dialog", "nach Deadline"))
