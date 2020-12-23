# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/task_list.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(977, 499)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.toolBox_2 = QtWidgets.QToolBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBox_2.sizePolicy().hasHeightForWidth())
        self.toolBox_2.setSizePolicy(sizePolicy)
        self.toolBox_2.setMinimumSize(QtCore.QSize(90, 0))
        self.toolBox_2.setObjectName("toolBox_2")
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setGeometry(QtCore.QRect(0, 0, 106, 377))
        self.page_4.setObjectName("page_4")
        self.formLayout = QtWidgets.QFormLayout(self.page_4)
        self.formLayout.setObjectName("formLayout")
        self.throw_heads = QtWidgets.QPushButton(self.page_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.throw_heads.sizePolicy().hasHeightForWidth())
        self.throw_heads.setSizePolicy(sizePolicy)
        self.throw_heads.setFlat(False)
        self.throw_heads.setObjectName("throw_heads")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.throw_heads)
        self.throw_tails = QtWidgets.QPushButton(self.page_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.throw_tails.sizePolicy().hasHeightForWidth())
        self.throw_tails.setSizePolicy(sizePolicy)
        self.throw_tails.setObjectName("throw_tails")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.throw_tails)
        self.toss_coin = QtWidgets.QPushButton(self.page_4)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui/../extra/feathericons/coin.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toss_coin.setIcon(icon)
        self.toss_coin.setObjectName("toss_coin")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.toss_coin)
        self.toolBox_2.addItem(self.page_4, "")
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setGeometry(QtCore.QRect(0, 0, 90, 394))
        self.page_5.setObjectName("page_5")
        self.toolBox_2.addItem(self.page_5, "")
        self.horizontalLayout_4.addWidget(self.toolBox_2)
        self.horizontalLayout_3.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setInputMask("")
        self.lineEdit.setText("")
        self.lineEdit.setMaxLength(32767)
        self.lineEdit.setFrame(True)
        self.lineEdit.setDragEnabled(True)
        self.lineEdit.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_3.addWidget(self.lineEdit)
        self.toolBox = QtWidgets.QToolBox(self.groupBox)
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 728, 341))
        self.page.setObjectName("page")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.page)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeView = QtWidgets.QTreeView(self.page)
        self.treeView.setObjectName("treeView")
        self.horizontalLayout.addWidget(self.treeView)
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 728, 341))
        self.page_2.setObjectName("page_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.page_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.listView = QtWidgets.QTableView(self.page_2)
        self.listView.setAutoFillBackground(False)
        self.listView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.listView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.listView.setTabKeyNavigation(False)
        self.listView.setDragDropOverwriteMode(False)
        self.listView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.listView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.listView.setSortingEnabled(True)
        self.listView.setObjectName("listView")
        self.listView.verticalHeader().setSortIndicatorShown(True)
        self.horizontalLayout_5.addWidget(self.listView)
        self.groupBox_3 = QtWidgets.QGroupBox(self.page_2)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.delete_tasks = QtWidgets.QPushButton(self.groupBox_3)
        self.delete_tasks.setObjectName("delete_tasks")
        self.verticalLayout.addWidget(self.delete_tasks)
        self.start_task = QtWidgets.QPushButton(self.groupBox_3)
        self.start_task.setObjectName("start_task")
        self.verticalLayout.addWidget(self.start_task)
        self.edit_selection = QtWidgets.QPushButton(self.groupBox_3)
        self.edit_selection.setAutoDefault(True)
        self.edit_selection.setDefault(True)
        self.edit_selection.setObjectName("edit_selection")
        self.verticalLayout.addWidget(self.edit_selection)
        self.horizontalLayout_5.addWidget(self.groupBox_3)
        self.toolBox.addItem(self.page_2, "")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 728, 341))
        self.page_3.setObjectName("page_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.page_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tableView = QtWidgets.QTableView(self.page_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_2.addWidget(self.tableView)
        self.toolBox.addItem(self.page_3, "")
        self.verticalLayout_3.addWidget(self.toolBox)
        self.horizontalLayout_3.addWidget(self.groupBox)
        self.filter_dock = QtWidgets.QDockWidget(Dialog)
        self.filter_dock.setObjectName("filter_dock")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.filter_dock.setWidget(self.dockWidgetContents)
        self.horizontalLayout_3.addWidget(self.filter_dock)

        self.retranslateUi(Dialog)
        self.toolBox_2.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox_2.setTitle(_translate("Dialog", "Werkzeuge"))
        self.throw_heads.setText(_translate("Dialog", "Kopf"))
        self.throw_tails.setText(_translate("Dialog", "Zahl"))
        self.toss_coin.setText(_translate("Dialog", "Wirf Münze"))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_4), _translate("Dialog", "Münzwurf"))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_5), _translate("Dialog", "<deine Idee>"))
        self.groupBox.setTitle(_translate("Dialog", "Aufgaben"))
        self.lineEdit.setPlaceholderText(_translate("Dialog", "filter..."))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Dialog", "Baum"))
        self.groupBox_3.setTitle(_translate("Dialog", "GroupBox"))
        self.delete_tasks.setText(_translate("Dialog", "Lösche alle \n"
"angezeigten"))
        self.start_task.setText(_translate("Dialog", "starte Aufgabe"))
        self.edit_selection.setText(_translate("Dialog", "bearbeite Details"))
        self.edit_selection.setShortcut(_translate("Dialog", "Return, Space"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("Dialog", "Liste"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("Dialog", "Tabelle"))
