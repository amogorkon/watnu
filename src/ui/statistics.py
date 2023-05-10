# Form implementation generated from reading ui file 'src\ui\statistics.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(460, 274)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabs = QtWidgets.QTabWidget(parent=Dialog)
        self.tabs.setObjectName("tabs")
        self.general_tab = QtWidgets.QWidget()
        self.general_tab.setObjectName("general_tab")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.general_tab)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.today_finished_label = QtWidgets.QLabel(parent=self.general_tab)
        self.today_finished_label.setObjectName("today_finished_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.today_finished_label)
        self.today_finished_outlabel = QtWidgets.QLabel(parent=self.general_tab)
        self.today_finished_outlabel.setText("")
        self.today_finished_outlabel.setObjectName("today_finished_outlabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.today_finished_outlabel)
        self.total_finished_label = QtWidgets.QLabel(parent=self.general_tab)
        self.total_finished_label.setObjectName("total_finished_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.total_finished_label)
        self.total_finished_outlabel = QtWidgets.QLabel(parent=self.general_tab)
        self.total_finished_outlabel.setText("")
        self.total_finished_outlabel.setObjectName("total_finished_outlabel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.total_finished_outlabel)
        self.total_num_tasks_label = QtWidgets.QLabel(parent=self.general_tab)
        self.total_num_tasks_label.setObjectName("total_num_tasks_label")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.total_num_tasks_label)
        self.total_num_tasks_outlabel = QtWidgets.QLabel(parent=self.general_tab)
        self.total_num_tasks_outlabel.setText("")
        self.total_num_tasks_outlabel.setObjectName("total_num_tasks_outlabel")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.total_num_tasks_outlabel)
        self.today_added_label = QtWidgets.QLabel(parent=self.general_tab)
        self.today_added_label.setObjectName("today_added_label")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.today_added_label)
        self.today_added_outlabel = QtWidgets.QLabel(parent=self.general_tab)
        self.today_added_outlabel.setText("")
        self.today_added_outlabel.setObjectName("today_added_outlabel")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.today_added_outlabel)
        self.yesterday_added_label = QtWidgets.QLabel(parent=self.general_tab)
        self.yesterday_added_label.setObjectName("yesterday_added_label")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.yesterday_added_label)
        self.yesterday_added_outlabel = QtWidgets.QLabel(parent=self.general_tab)
        self.yesterday_added_outlabel.setText("")
        self.yesterday_added_outlabel.setObjectName("yesterday_added_outlabel")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.yesterday_added_outlabel)
        self.yesterday_finished_label = QtWidgets.QLabel(parent=self.general_tab)
        self.yesterday_finished_label.setObjectName("yesterday_finished_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.yesterday_finished_label)
        self.yesterday_finished_outlabel = QtWidgets.QLabel(parent=self.general_tab)
        self.yesterday_finished_outlabel.setText("")
        self.yesterday_finished_outlabel.setObjectName("yesterday_finished_outlabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.yesterday_finished_outlabel)
        self.verticalLayout_7.addLayout(self.formLayout)
        self.tabs.addTab(self.general_tab, "")
        self.spaces_tab = QtWidgets.QWidget()
        self.spaces_tab.setObjectName("spaces_tab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.spaces_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.space_stats = QtWidgets.QTableWidget(parent=self.spaces_tab)
        self.space_stats.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.space_stats.setAlternatingRowColors(True)
        self.space_stats.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.space_stats.setObjectName("space_stats")
        self.space_stats.setColumnCount(4)
        self.space_stats.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.space_stats.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.space_stats.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.space_stats.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.space_stats.setHorizontalHeaderItem(3, item)
        self.space_stats.horizontalHeader().setHighlightSections(False)
        self.space_stats.verticalHeader().setVisible(False)
        self.space_stats.verticalHeader().setHighlightSections(False)
        self.verticalLayout_4.addWidget(self.space_stats)
        self.tabs.addTab(self.spaces_tab, "")
        self.level_tab = QtWidgets.QWidget()
        self.level_tab.setObjectName("level_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.level_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.level_stats = QtWidgets.QTableWidget(parent=self.level_tab)
        self.level_stats.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.level_stats.setAlternatingRowColors(True)
        self.level_stats.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.level_stats.setObjectName("level_stats")
        self.level_stats.setColumnCount(4)
        self.level_stats.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.level_stats.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.level_stats.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.level_stats.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.level_stats.setHorizontalHeaderItem(3, item)
        self.level_stats.horizontalHeader().setHighlightSections(False)
        self.level_stats.verticalHeader().setVisible(False)
        self.level_stats.verticalHeader().setHighlightSections(False)
        self.verticalLayout_2.addWidget(self.level_stats)
        self.tabs.addTab(self.level_tab, "")
        self.sessions_tab = QtWidgets.QWidget()
        self.sessions_tab.setObjectName("sessions_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.sessions_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.session_stats = QtWidgets.QTableWidget(parent=self.sessions_tab)
        self.session_stats.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.session_stats.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.session_stats.setDragDropOverwriteMode(False)
        self.session_stats.setAlternatingRowColors(True)
        self.session_stats.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.session_stats.setObjectName("session_stats")
        self.session_stats.setColumnCount(6)
        self.session_stats.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.session_stats.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.session_stats.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.session_stats.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.session_stats.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.session_stats.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.session_stats.setHorizontalHeaderItem(5, item)
        self.session_stats.horizontalHeader().setCascadingSectionResizes(True)
        self.session_stats.horizontalHeader().setDefaultSectionSize(120)
        self.session_stats.horizontalHeader().setHighlightSections(True)
        self.session_stats.horizontalHeader().setMinimumSectionSize(120)
        self.session_stats.horizontalHeader().setSortIndicatorShown(True)
        self.session_stats.horizontalHeader().setStretchLastSection(True)
        self.session_stats.verticalHeader().setVisible(False)
        self.session_stats.verticalHeader().setHighlightSections(False)
        self.verticalLayout_3.addWidget(self.session_stats)
        self.tabs.addTab(self.sessions_tab, "")
        self.verticalLayout.addWidget(self.tabs)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, 0, 0, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.button7 = QtWidgets.QPushButton(parent=Dialog)
        self.button7.setEnabled(False)
        self.button7.setText("")
        self.button7.setObjectName("button7")
        self.gridLayout.addWidget(self.button7, 0, 0, 1, 1)
        self.button2 = QtWidgets.QPushButton(parent=Dialog)
        self.button2.setEnabled(False)
        self.button2.setText("")
        self.button2.setObjectName("button2")
        self.gridLayout.addWidget(self.button2, 3, 1, 1, 1)
        self.button5 = QtWidgets.QPushButton(parent=Dialog)
        self.button5.setEnabled(False)
        self.button5.setText("")
        self.button5.setObjectName("button5")
        self.gridLayout.addWidget(self.button5, 2, 1, 1, 1)
        self.button9 = QtWidgets.QPushButton(parent=Dialog)
        self.button9.setEnabled(False)
        self.button9.setText("")
        self.button9.setObjectName("button9")
        self.gridLayout.addWidget(self.button9, 0, 2, 1, 1)
        self.button4 = QtWidgets.QPushButton(parent=Dialog)
        self.button4.setEnabled(False)
        self.button4.setText("")
        self.button4.setObjectName("button4")
        self.gridLayout.addWidget(self.button4, 2, 0, 1, 1)
        self.button6 = QtWidgets.QPushButton(parent=Dialog)
        self.button6.setEnabled(False)
        self.button6.setText("")
        self.button6.setObjectName("button6")
        self.gridLayout.addWidget(self.button6, 2, 2, 1, 1)
        self.button3 = QtWidgets.QPushButton(parent=Dialog)
        self.button3.setEnabled(False)
        self.button3.setText("")
        self.button3.setObjectName("button3")
        self.gridLayout.addWidget(self.button3, 3, 2, 1, 1)
        self.button1 = QtWidgets.QPushButton(parent=Dialog)
        self.button1.setEnabled(False)
        self.button1.setText("")
        self.button1.setObjectName("button1")
        self.gridLayout.addWidget(self.button1, 3, 0, 1, 1)
        self.button8 = QtWidgets.QPushButton(parent=Dialog)
        self.button8.setEnabled(False)
        self.button8.setText("")
        self.button8.setObjectName("button8")
        self.gridLayout.addWidget(self.button8, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Dialog)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Statistiken"))
        self.today_finished_label.setText(_translate("Dialog", "Heute erledigt"))
        self.total_finished_label.setText(_translate("Dialog", "Gesamtanzahl aller erledigten Aufgaben"))
        self.total_num_tasks_label.setText(_translate("Dialog", "Gesamtanzahl aller zugefügten Aufgaben"))
        self.today_added_label.setText(_translate("Dialog", "Heute hinzugefügt"))
        self.yesterday_added_label.setText(_translate("Dialog", "Gestern hinzugefügt"))
        self.yesterday_finished_label.setText(_translate("Dialog", "Gestern erledigt"))
        self.tabs.setTabText(self.tabs.indexOf(self.general_tab), _translate("Dialog", "Allgemein"))
        item = self.space_stats.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Raum"))
        item = self.space_stats.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "erledigt"))
        item = self.space_stats.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "unerledigt"))
        item = self.space_stats.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "total"))
        self.tabs.setTabText(self.tabs.indexOf(self.spaces_tab), _translate("Dialog", "Räume"))
        item = self.level_stats.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Level"))
        item = self.level_stats.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "erledigt"))
        item = self.level_stats.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "unerledigt"))
        item = self.level_stats.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "total"))
        self.tabs.setTabText(self.tabs.indexOf(self.level_tab), _translate("Dialog", "Level"))
        self.session_stats.setSortingEnabled(True)
        item = self.session_stats.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Aufgabe"))
        item = self.session_stats.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "angefangen"))
        item = self.session_stats.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "aufgehört"))
        item = self.session_stats.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "beendet"))
        item = self.session_stats.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Länge (mit Pausen)"))
        item = self.session_stats.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "Pufferzeit (Pausen)"))
        self.tabs.setTabText(self.tabs.indexOf(self.sessions_tab), _translate("Dialog", "Sitzungen"))
