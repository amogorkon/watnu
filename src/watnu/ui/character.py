# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\character.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(621, 404)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.skills_table = QtWidgets.QTableWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.skills_table.sizePolicy().hasHeightForWidth())
        self.skills_table.setSizePolicy(sizePolicy)
        self.skills_table.setAutoFillBackground(True)
        self.skills_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.skills_table.setTabKeyNavigation(False)
        self.skills_table.setProperty("showDropIndicator", False)
        self.skills_table.setDragDropOverwriteMode(False)
        self.skills_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.skills_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.skills_table.setWordWrap(False)
        self.skills_table.setObjectName("skills_table")
        self.skills_table.setColumnCount(3)
        self.skills_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.skills_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.skills_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.skills_table.setHorizontalHeaderItem(2, item)
        self.skills_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.skills_table)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.skills_table.setSortingEnabled(True)
        item = self.skills_table.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Fähigkeit"))
        item = self.skills_table.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "# Aufgaben"))
        item = self.skills_table.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "∑ Zeit [hours]"))