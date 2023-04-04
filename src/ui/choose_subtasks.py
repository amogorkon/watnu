# Form implementation generated from reading ui file 'ui\choose_subtasks.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(624, 502)
        Dialog.setSizeGripEnabled(True)
        self.layout = QtWidgets.QVBoxLayout(Dialog)
        self.layout.setObjectName("layout")
        self.groupBox = QtWidgets.QGroupBox(parent=Dialog)
        self.groupBox.setObjectName("groupBox")
        self.statusLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.statusLayout.setContentsMargins(-1, 10, -1, -1)
        self.statusLayout.setObjectName("statusLayout")
        self.field_filter = QtWidgets.QLineEdit(parent=self.groupBox)
        self.field_filter.setToolTip("")
        self.field_filter.setInputMask("")
        self.field_filter.setText("")
        self.field_filter.setMaxLength(32767)
        self.field_filter.setFrame(True)
        self.field_filter.setDragEnabled(True)
        self.field_filter.setCursorMoveStyle(QtCore.Qt.CursorMoveStyle.LogicalMoveStyle)
        self.field_filter.setClearButtonEnabled(True)
        self.field_filter.setObjectName("field_filter")
        self.statusLayout.addWidget(self.field_filter)
        self.space = QtWidgets.QComboBox(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.space.sizePolicy().hasHeightForWidth())
        self.space.setSizePolicy(sizePolicy)
        self.space.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.space.setFont(font)
        self.space.setEditable(False)
        self.space.setMaxVisibleItems(12)
        self.space.setObjectName("space")
        self.space.addItem("")
        self.statusLayout.addWidget(self.space)
        self.status = QtWidgets.QComboBox(parent=self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.status.setFont(font)
        self.status.setObjectName("status")
        self.status.addItem("")
        self.status.addItem("")
        self.status.addItem("")
        self.status.addItem("")
        self.status.addItem("")
        self.status.addItem("")
        self.statusLayout.addWidget(self.status)
        self.ilk = QtWidgets.QComboBox(parent=self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.ilk.setFont(font)
        self.ilk.setObjectName("ilk")
        self.ilk.addItem("")
        self.ilk.addItem("")
        self.ilk.addItem("")
        self.ilk.addItem("")
        self.ilk.addItem("")
        self.statusLayout.addWidget(self.ilk)
        self.layout.addWidget(self.groupBox)
        self.horizontalGroupBox = QtWidgets.QGroupBox(parent=Dialog)
        self.horizontalGroupBox.setObjectName("horizontalGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        self.horizontalLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.check_level = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_level.setObjectName("check_level")
        self.horizontalLayout.addWidget(self.check_level)
        self.check_priority = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_priority.setObjectName("check_priority")
        self.horizontalLayout.addWidget(self.check_priority)
        self.check_space = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_space.setObjectName("check_space")
        self.horizontalLayout.addWidget(self.check_space)
        self.check_deadline = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_deadline.setObjectName("check_deadline")
        self.horizontalLayout.addWidget(self.check_deadline)
        self.check_done = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_done.setObjectName("check_done")
        self.horizontalLayout.addWidget(self.check_done)
        self.check_draft = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_draft.setObjectName("check_draft")
        self.horizontalLayout.addWidget(self.check_draft)
        self.check_inactive = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_inactive.setObjectName("check_inactive")
        self.horizontalLayout.addWidget(self.check_inactive)
        self.check_deleted = QtWidgets.QCheckBox(parent=self.horizontalGroupBox)
        self.check_deleted.setObjectName("check_deleted")
        self.horizontalLayout.addWidget(self.check_deleted)
        self.layout.addWidget(self.horizontalGroupBox)
        self.task_list = QtWidgets.QTableWidget(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_list.sizePolicy().hasHeightForWidth())
        self.task_list.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setBold(True)
        font.setWeight(75)
        self.task_list.setFont(font)
        self.task_list.setAutoFillBackground(False)
        self.task_list.setStyleSheet("")
        self.task_list.setMidLineWidth(0)
        self.task_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.task_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.task_list.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.task_list.setAutoScroll(True)
        self.task_list.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.task_list.setTabKeyNavigation(False)
        self.task_list.setProperty("showDropIndicator", False)
        self.task_list.setDragDropOverwriteMode(False)
        self.task_list.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.task_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.task_list.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self.task_list.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.task_list.setShowGrid(False)
        self.task_list.setWordWrap(False)
        self.task_list.setCornerButtonEnabled(True)
        self.task_list.setColumnCount(0)
        self.task_list.setObjectName("task_list")
        self.task_list.setRowCount(0)
        self.task_list.horizontalHeader().setCascadingSectionResizes(True)
        self.task_list.horizontalHeader().setDefaultSectionSize(100)
        self.task_list.horizontalHeader().setMinimumSectionSize(5)
        self.task_list.horizontalHeader().setStretchLastSection(True)
        self.task_list.verticalHeader().setVisible(True)
        self.task_list.verticalHeader().setCascadingSectionResizes(False)
        self.task_list.verticalHeader().setHighlightSections(True)
        self.task_list.verticalHeader().setSortIndicatorShown(False)
        self.task_list.verticalHeader().setStretchLastSection(False)
        self.layout.addWidget(self.task_list)
        self.buttonLayout = QtWidgets.QGridLayout()
        self.buttonLayout.setContentsMargins(-1, 0, -1, -1)
        self.buttonLayout.setObjectName("buttonLayout")
        self.button6 = QtWidgets.QPushButton(parent=Dialog)
        self.button6.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button6.sizePolicy().hasHeightForWidth())
        self.button6.setSizePolicy(sizePolicy)
        self.button6.setObjectName("button6")
        self.buttonLayout.addWidget(self.button6, 2, 3, 1, 1)
        self.button4 = QtWidgets.QPushButton(parent=Dialog)
        self.button4.setAutoDefault(True)
        self.button4.setDefault(True)
        self.button4.setObjectName("button4")
        self.buttonLayout.addWidget(self.button4, 2, 1, 1, 1)
        self.button2 = QtWidgets.QPushButton(parent=Dialog)
        self.button2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button2.sizePolicy().hasHeightForWidth())
        self.button2.setSizePolicy(sizePolicy)
        self.button2.setObjectName("button2")
        self.buttonLayout.addWidget(self.button2, 3, 2, 1, 1)
        self.button5 = QtWidgets.QPushButton(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button5.sizePolicy().hasHeightForWidth())
        self.button5.setSizePolicy(sizePolicy)
        self.button5.setObjectName("button5")
        self.buttonLayout.addWidget(self.button5, 2, 2, 1, 1)
        self.button1 = QtWidgets.QPushButton(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button1.sizePolicy().hasHeightForWidth())
        self.button1.setSizePolicy(sizePolicy)
        self.button1.setObjectName("button1")
        self.buttonLayout.addWidget(self.button1, 3, 1, 1, 1)
        self.button7 = QtWidgets.QPushButton(parent=Dialog)
        self.button7.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button7.sizePolicy().hasHeightForWidth())
        self.button7.setSizePolicy(sizePolicy)
        self.button7.setObjectName("button7")
        self.buttonLayout.addWidget(self.button7, 1, 1, 1, 1)
        self.button8 = QtWidgets.QPushButton(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button8.sizePolicy().hasHeightForWidth())
        self.button8.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui\\../extra/feathericons/coin.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.button8.setIcon(icon)
        self.button8.setObjectName("button8")
        self.buttonLayout.addWidget(self.button8, 1, 2, 1, 1)
        self.button9 = QtWidgets.QPushButton(parent=Dialog)
        self.button9.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button9.sizePolicy().hasHeightForWidth())
        self.button9.setSizePolicy(sizePolicy)
        self.button9.setCheckable(False)
        self.button9.setObjectName("button9")
        self.buttonLayout.addWidget(self.button9, 1, 3, 1, 1)
        self.button3 = QtWidgets.QPushButton(parent=Dialog)
        self.button3.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button3.sizePolicy().hasHeightForWidth())
        self.button3.setSizePolicy(sizePolicy)
        self.button3.setObjectName("button3")
        self.buttonLayout.addWidget(self.button3, 3, 3, 1, 1)
        self.layout.addLayout(self.buttonLayout)

        self.retranslateUi(Dialog)
        self.space.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Aufgaben"))
        self.groupBox.setTitle(_translate("Dialog", "Auswahl"))
        self.field_filter.setPlaceholderText(_translate("Dialog", "filter..."))
        self.space.setToolTip(_translate("Dialog", "Raum"))
        self.space.setCurrentText(_translate("Dialog", "alle Räume"))
        self.space.setItemText(0, _translate("Dialog", "alle Räume"))
        self.status.setToolTip(_translate("Dialog", "Status"))
        self.status.setItemText(0, _translate("Dialog", "offen"))
        self.status.setItemText(1, _translate("Dialog", "Entwurf"))
        self.status.setItemText(2, _translate("Dialog", "inaktiv"))
        self.status.setItemText(3, _translate("Dialog", "erledigt"))
        self.status.setItemText(4, _translate("Dialog", "gelöscht"))
        self.status.setItemText(5, _translate("Dialog", "-- alles --"))
        self.ilk.setToolTip(_translate("Dialog", "Art"))
        self.ilk.setItemText(0, _translate("Dialog", "-- alle Arten--"))
        self.ilk.setItemText(1, _translate("Dialog", "Aufgabe"))
        self.ilk.setItemText(2, _translate("Dialog", "Gewohnheit"))
        self.ilk.setItemText(3, _translate("Dialog", "Tradition"))
        self.ilk.setItemText(4, _translate("Dialog", "Routine"))
        self.horizontalGroupBox.setTitle(_translate("Dialog", "Spalten"))
        self.check_level.setText(_translate("Dialog", "Level"))
        self.check_priority.setText(_translate("Dialog", "Priorität"))
        self.check_space.setText(_translate("Dialog", "Raum"))
        self.check_deadline.setText(_translate("Dialog", "Deadline"))
        self.check_done.setText(_translate("Dialog", "erledigt"))
        self.check_draft.setText(_translate("Dialog", "Entwurf"))
        self.check_inactive.setText(_translate("Dialog", "inactiv"))
        self.check_deleted.setText(_translate("Dialog", "gelöscht"))
        self.task_list.setSortingEnabled(True)
        self.button6.setText(_translate("Dialog", "erstelle neue Aufgabe"))
        self.button6.setShortcut(_translate("Dialog", "6"))
        self.button4.setText(_translate("Dialog", "bearbeite Aufgabe(n)"))
        self.button4.setShortcut(_translate("Dialog", "4"))
        self.button2.setText(_translate("Dialog", "Erledigt!"))
        self.button5.setText(_translate("Dialog", "starte Aufgabe"))
        self.button5.setShortcut(_translate("Dialog", "5"))
        self.button1.setText(_translate("Dialog", "setze Aufgabe(n) als..."))
        self.button1.setShortcut(_translate("Dialog", "1"))
        self.button7.setText(_translate("Dialog", "Raum..."))
        self.button7.setShortcut(_translate("Dialog", "7"))
        self.button8.setText(_translate("Dialog", "Wirf Münze"))
        self.button8.setShortcut(_translate("Dialog", "8"))
        self.button9.setText(_translate("Dialog", "klone Aufgabe ..."))
        self.button9.setShortcut(_translate("Dialog", "9"))
        self.button3.setText(_translate("Dialog", "organisiere Aufgaben"))
        self.button3.setShortcut(_translate("Dialog", "3"))
