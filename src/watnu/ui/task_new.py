# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\task_new.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(667, 790)
        Wizard.setSizeGripEnabled(True)
        Wizard.setModal(True)
        Wizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        Wizard.setOptions(QtWidgets.QWizard.CancelButtonOnLeft|QtWidgets.QWizard.HaveFinishButtonOnEarlyPages|QtWidgets.QWizard.HaveNextButtonOnLastPage)
        self.page_basics = QtWidgets.QWizardPage()
        self.page_basics.setObjectName("page_basics")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_basics)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.page_basics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.desc = QtWidgets.QPlainTextEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.desc.sizePolicy().hasHeightForWidth())
        self.desc.setSizePolicy(sizePolicy)
        self.desc.setMaximumSize(QtCore.QSize(16777215, 500))
        self.desc.setMouseTracking(True)
        self.desc.setTabletTracking(True)
        self.desc.setAutoFillBackground(True)
        self.desc.setFrameShadow(QtWidgets.QFrame.Plain)
        self.desc.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.desc.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.desc.setTabChangesFocus(True)
        self.desc.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.desc.setBackgroundVisible(False)
        self.desc.setCenterOnScroll(False)
        self.desc.setObjectName("desc")
        self.verticalLayout.addWidget(self.desc)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_7 = QtWidgets.QGroupBox(self.page_basics)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.url = QtWidgets.QLineEdit(self.groupBox_7)
        self.url.setObjectName("url")
        self.verticalLayout_5.addWidget(self.url)
        self.verticalLayout_2.addWidget(self.groupBox_7)
        self.groupBox_5 = QtWidgets.QGroupBox(self.page_basics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.notes = QtWidgets.QPlainTextEdit(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.notes.sizePolicy().hasHeightForWidth())
        self.notes.setSizePolicy(sizePolicy)
        self.notes.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.notes.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.notes.setObjectName("notes")
        self.verticalLayout_3.addWidget(self.notes)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_6.sizePolicy().hasHeightForWidth())
        self.groupBox_6.setSizePolicy(sizePolicy)
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.attachments = QtWidgets.QListView(self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.attachments.sizePolicy().hasHeightForWidth())
        self.attachments.setSizePolicy(sizePolicy)
        self.attachments.setObjectName("attachments")
        self.horizontalLayout.addWidget(self.attachments)
        self.groupBox_9 = QtWidgets.QGroupBox(self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_9.sizePolicy().hasHeightForWidth())
        self.groupBox_9.setSizePolicy(sizePolicy)
        self.groupBox_9.setObjectName("groupBox_9")
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_9)
        self.spinBox.setGeometry(QtCore.QRect(110, 30, 61, 21))
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.groupBox_9)
        self.verticalLayout_3.addWidget(self.groupBox_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        Wizard.addPage(self.page_basics)
        self.page_categories = QtWidgets.QWizardPage()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.page_categories.sizePolicy().hasHeightForWidth())
        self.page_categories.setSizePolicy(sizePolicy)
        self.page_categories.setObjectName("page_categories")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.page_categories)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_3 = QtWidgets.QGroupBox(self.page_categories)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName("groupBox_3")
        self.priority = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.priority.setGeometry(QtCore.QRect(40, 50, 62, 22))
        self.priority.setObjectName("priority")
        self.gridLayout_3.addWidget(self.groupBox_3, 2, 3, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.page_categories)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.level = QtWidgets.QComboBox(self.groupBox_2)
        self.level.setEnabled(True)
        self.level.setGeometry(QtCore.QRect(30, 40, 91, 22))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.level.sizePolicy().hasHeightForWidth())
        self.level.setSizePolicy(sizePolicy)
        self.level.setCurrentText("")
        self.level.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.level.setFrame(True)
        self.level.setObjectName("level")
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 3, 1, 1)
        self.groupBox_11 = QtWidgets.QGroupBox(self.page_categories)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox_11.sizePolicy().hasHeightForWidth())
        self.groupBox_11.setSizePolicy(sizePolicy)
        self.groupBox_11.setObjectName("groupBox_11")
        self.activity = QtWidgets.QComboBox(self.groupBox_11)
        self.activity.setGeometry(QtCore.QRect(30, 20, 69, 22))
        self.activity.setObjectName("activity")
        self.activity.addItem("")
        self.gridLayout_3.addWidget(self.groupBox_11, 2, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.page_categories)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setObjectName("groupBox_4")
        self.space = QtWidgets.QComboBox(self.groupBox_4)
        self.space.setEnabled(True)
        self.space.setGeometry(QtCore.QRect(30, 40, 69, 22))
        self.space.setCurrentText("")
        self.space.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.space.setFrame(True)
        self.space.setModelColumn(0)
        self.space.setObjectName("space")
        self.gridLayout_3.addWidget(self.groupBox_4, 1, 0, 1, 1)
        Wizard.addPage(self.page_categories)
        self.dependencies = QtWidgets.QWizardPage()
        self.dependencies.setObjectName("dependencies")
        self.gridLayout = QtWidgets.QGridLayout(self.dependencies)
        self.gridLayout.setObjectName("gridLayout")
        self.dependency = QtWidgets.QGroupBox(self.dependencies)
        self.dependency.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dependency.sizePolicy().hasHeightForWidth())
        self.dependency.setSizePolicy(sizePolicy)
        self.dependency.setTitle("")
        self.dependency.setObjectName("dependency")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.dependency)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.task_dependency_table = QtWidgets.QTableWidget(self.dependency)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_dependency_table.sizePolicy().hasHeightForWidth())
        self.task_dependency_table.setSizePolicy(sizePolicy)
        self.task_dependency_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.task_dependency_table.setTabKeyNavigation(False)
        self.task_dependency_table.setProperty("showDropIndicator", False)
        self.task_dependency_table.setDragDropOverwriteMode(False)
        self.task_dependency_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.task_dependency_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.task_dependency_table.setWordWrap(False)
        self.task_dependency_table.setObjectName("task_dependency_table")
        self.task_dependency_table.setColumnCount(5)
        self.task_dependency_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.task_dependency_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.task_dependency_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.task_dependency_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.task_dependency_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.task_dependency_table.setHorizontalHeaderItem(4, item)
        self.task_dependency_table.verticalHeader().setVisible(False)
        self.gridLayout_2.addWidget(self.task_dependency_table, 4, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.is_subtask_of = QtWidgets.QRadioButton(self.dependency)
        self.is_subtask_of.setChecked(True)
        self.is_subtask_of.setObjectName("is_subtask_of")
        self.task_dependency = QtWidgets.QButtonGroup(Wizard)
        self.task_dependency.setObjectName("task_dependency")
        self.task_dependency.addButton(self.is_subtask_of)
        self.horizontalLayout_2.addWidget(self.is_subtask_of)
        self.is_depending_on = QtWidgets.QRadioButton(self.dependency)
        self.is_depending_on.setObjectName("is_depending_on")
        self.task_dependency.addButton(self.is_depending_on)
        self.horizontalLayout_2.addWidget(self.is_depending_on)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.dependency, 2, 0, 1, 2)
        self.groupBox_8 = QtWidgets.QGroupBox(self.dependencies)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_8.sizePolicy().hasHeightForWidth())
        self.groupBox_8.setSizePolicy(sizePolicy)
        self.groupBox_8.setTitle("")
        self.groupBox_8.setObjectName("groupBox_8")
        self.deadline = QtWidgets.QDateTimeEdit(self.groupBox_8)
        self.deadline.setEnabled(False)
        self.deadline.setGeometry(QtCore.QRect(50, 30, 241, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deadline.sizePolicy().hasHeightForWidth())
        self.deadline.setSizePolicy(sizePolicy)
        self.deadline.setDate(QtCore.QDate(2021, 1, 1))
        self.deadline.setTime(QtCore.QTime(0, 0, 0))
        self.deadline.setMaximumDateTime(QtCore.QDateTime(QtCore.QDate(9999, 12, 31), QtCore.QTime(23, 59, 59)))
        self.deadline.setCurrentSection(QtWidgets.QDateTimeEdit.YearSection)
        self.deadline.setCalendarPopup(True)
        self.deadline.setObjectName("deadline")
        self.deadline_active = QtWidgets.QCheckBox(self.groupBox_8)
        self.deadline_active.setGeometry(QtCore.QRect(20, 0, 101, 17))
        self.deadline_active.setTristate(False)
        self.deadline_active.setObjectName("deadline_active")
        self.gridLayout.addWidget(self.groupBox_8, 0, 0, 1, 1)
        self.groupBox_12 = QtWidgets.QGroupBox(self.dependencies)
        self.groupBox_12.setObjectName("groupBox_12")
        self.depend_on_group = QtWidgets.QComboBox(self.groupBox_12)
        self.depend_on_group.setGeometry(QtCore.QRect(30, 20, 69, 22))
        self.depend_on_group.setObjectName("depend_on_group")
        self.gridLayout.addWidget(self.groupBox_12, 0, 1, 1, 1)
        Wizard.addPage(self.dependencies)

        self.retranslateUi(Wizard)
        self.level.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Bearbeite Aufgabe"))
        self.page_basics.setTitle(_translate("Wizard", "Beschreibung"))
        self.desc.setPlaceholderText(_translate("Wizard", "Beschreibung der Aufgabe"))
        self.groupBox_7.setTitle(_translate("Wizard", "URL"))
        self.groupBox_5.setTitle(_translate("Wizard", "Notizen"))
        self.notes.setPlaceholderText(_translate("Wizard", "Notizen"))
        self.groupBox_6.setTitle(_translate("Wizard", "Anhänge"))
        self.groupBox_9.setTitle(_translate("Wizard", "Erwarteter Arbeitsaufwand [min]"))
        self.groupBox_3.setTitle(_translate("Wizard", "Priorität"))
        self.groupBox_2.setTitle(_translate("Wizard", "Level"))
        self.groupBox_11.setTitle(_translate("Wizard", "Aktivität"))
        self.activity.setItemText(0, _translate("Wizard", "---"))
        self.groupBox_4.setTitle(_translate("Wizard", "Space"))
        self.task_dependency_table.setSortingEnabled(True)
        item = self.task_dependency_table.horizontalHeaderItem(0)
        item.setText(_translate("Wizard", "do"))
        item = self.task_dependency_table.horizontalHeaderItem(1)
        item.setText(_translate("Wizard", "space"))
        item = self.task_dependency_table.horizontalHeaderItem(2)
        item.setText(_translate("Wizard", "level"))
        item = self.task_dependency_table.horizontalHeaderItem(3)
        item.setText(_translate("Wizard", "activity"))
        item = self.task_dependency_table.horizontalHeaderItem(4)
        item.setText(_translate("Wizard", "deadline"))
        self.is_subtask_of.setText(_translate("Wizard", "ist Subtask von"))
        self.is_depending_on.setText(_translate("Wizard", "hängt von Aufgabe ab"))
        self.deadline_active.setText(_translate("Wizard", "Deadline"))
        self.groupBox_12.setTitle(_translate("Wizard", "Hängt ab von der Gruppe"))
