# Form implementation generated from reading ui file 'src\ui\task_organizer.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(540, 580)
        Dialog.setSizeGripEnabled(False)
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
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
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
        self.groupBox_2 = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 150))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tasks_table = QtWidgets.QTableWidget(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.tasks_table.sizePolicy().hasHeightForWidth())
        self.tasks_table.setSizePolicy(sizePolicy)
        self.tasks_table.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setBold(True)
        font.setWeight(75)
        self.tasks_table.setFont(font)
        self.tasks_table.setAutoFillBackground(False)
        self.tasks_table.setStyleSheet("")
        self.tasks_table.setMidLineWidth(0)
        self.tasks_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tasks_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tasks_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tasks_table.setAutoScroll(True)
        self.tasks_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tasks_table.setTabKeyNavigation(True)
        self.tasks_table.setProperty("showDropIndicator", True)
        self.tasks_table.setDragEnabled(True)
        self.tasks_table.setDragDropOverwriteMode(False)
        self.tasks_table.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.tasks_table.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tasks_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tasks_table.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self.tasks_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tasks_table.setShowGrid(False)
        self.tasks_table.setWordWrap(False)
        self.tasks_table.setCornerButtonEnabled(False)
        self.tasks_table.setColumnCount(0)
        self.tasks_table.setObjectName("tasks_table")
        self.tasks_table.setRowCount(0)
        self.tasks_table.horizontalHeader().setCascadingSectionResizes(True)
        self.tasks_table.horizontalHeader().setDefaultSectionSize(100)
        self.tasks_table.horizontalHeader().setMinimumSectionSize(5)
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.verticalHeader().setVisible(True)
        self.tasks_table.verticalHeader().setCascadingSectionResizes(False)
        self.tasks_table.verticalHeader().setHighlightSections(True)
        self.tasks_table.verticalHeader().setSortIndicatorShown(False)
        self.tasks_table.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.tasks_table)
        self.layout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QtCore.QSize(0, 200))
        self.groupBox_3.setFlat(False)
        self.groupBox_3.setCheckable(False)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.concerned_task_table = QtWidgets.QTableWidget(parent=self.groupBox_3)
        self.concerned_task_table.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.concerned_task_table.sizePolicy().hasHeightForWidth())
        self.concerned_task_table.setSizePolicy(sizePolicy)
        self.concerned_task_table.setMaximumSize(QtCore.QSize(16777215, 30))
        self.concerned_task_table.setAutoFillBackground(False)
        self.concerned_task_table.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.concerned_task_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.concerned_task_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow
        )
        self.concerned_task_table.setAutoScroll(False)
        self.concerned_task_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.concerned_task_table.setTabKeyNavigation(False)
        self.concerned_task_table.setProperty("showDropIndicator", False)
        self.concerned_task_table.setDragDropOverwriteMode(False)
        self.concerned_task_table.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.NoDragDrop)
        self.concerned_task_table.setAlternatingRowColors(False)
        self.concerned_task_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.concerned_task_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.concerned_task_table.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self.concerned_task_table.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.concerned_task_table.setShowGrid(False)
        self.concerned_task_table.setWordWrap(False)
        self.concerned_task_table.setCornerButtonEnabled(False)
        self.concerned_task_table.setRowCount(1)
        self.concerned_task_table.setColumnCount(1)
        self.concerned_task_table.setObjectName("concerned_task_table")
        self.concerned_task_table.horizontalHeader().setVisible(False)
        self.concerned_task_table.horizontalHeader().setDefaultSectionSize(0)
        self.concerned_task_table.horizontalHeader().setHighlightSections(False)
        self.concerned_task_table.horizontalHeader().setMinimumSectionSize(0)
        self.concerned_task_table.horizontalHeader().setSortIndicatorShown(False)
        self.concerned_task_table.verticalHeader().setVisible(False)
        self.concerned_task_table.verticalHeader().setDefaultSectionSize(30)
        self.concerned_task_table.verticalHeader().setHighlightSections(False)
        self.concerned_task_table.verticalHeader().setMinimumSectionSize(0)
        self.verticalLayout.addWidget(self.concerned_task_table)
        self.relationship_button = QtWidgets.QPushButton(parent=self.groupBox_3)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src\\ui\\../extra/arrow-down.svg"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.relationship_button.setIcon(icon)
        self.relationship_button.setCheckable(False)
        self.relationship_button.setAutoExclusive(False)
        self.relationship_button.setObjectName("relationship_button")
        self.verticalLayout.addWidget(self.relationship_button)
        self.sub_sup_tasks_table = QtWidgets.QTableWidget(parent=self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.sub_sup_tasks_table.sizePolicy().hasHeightForWidth())
        self.sub_sup_tasks_table.setSizePolicy(sizePolicy)
        self.sub_sup_tasks_table.setMinimumSize(QtCore.QSize(0, 20))
        self.sub_sup_tasks_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sub_sup_tasks_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.sub_sup_tasks_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sub_sup_tasks_table.setDragEnabled(True)
        self.sub_sup_tasks_table.setDragDropOverwriteMode(False)
        self.sub_sup_tasks_table.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.sub_sup_tasks_table.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.sub_sup_tasks_table.setAlternatingRowColors(True)
        self.sub_sup_tasks_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.sub_sup_tasks_table.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self.sub_sup_tasks_table.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.sub_sup_tasks_table.setShowGrid(False)
        self.sub_sup_tasks_table.setWordWrap(False)
        self.sub_sup_tasks_table.setCornerButtonEnabled(False)
        self.sub_sup_tasks_table.setObjectName("sub_sup_tasks_table")
        self.sub_sup_tasks_table.setColumnCount(0)
        self.sub_sup_tasks_table.setRowCount(0)
        self.sub_sup_tasks_table.horizontalHeader().setVisible(True)
        self.sub_sup_tasks_table.horizontalHeader().setCascadingSectionResizes(True)
        self.sub_sup_tasks_table.horizontalHeader().setHighlightSections(True)
        self.sub_sup_tasks_table.horizontalHeader().setMinimumSectionSize(5)
        self.sub_sup_tasks_table.horizontalHeader().setSortIndicatorShown(True)
        self.sub_sup_tasks_table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.sub_sup_tasks_table)
        self.layout.addWidget(self.groupBox_3)
        self.buttonLayout = QtWidgets.QGridLayout()
        self.buttonLayout.setContentsMargins(-1, 0, -1, -1)
        self.buttonLayout.setObjectName("buttonLayout")
        self.button4 = QtWidgets.QPushButton(parent=Dialog)
        self.button4.setEnabled(True)
        self.button4.setAutoDefault(True)
        self.button4.setDefault(True)
        self.button4.setObjectName("button4")
        self.buttonLayout.addWidget(self.button4, 2, 1, 1, 1)
        self.button2 = QtWidgets.QPushButton(parent=Dialog)
        self.button2.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button2.sizePolicy().hasHeightForWidth())
        self.button2.setSizePolicy(sizePolicy)
        self.button2.setText("")
        self.button2.setObjectName("button2")
        self.buttonLayout.addWidget(self.button2, 3, 2, 1, 1)
        self.button5 = QtWidgets.QPushButton(parent=Dialog)
        self.button5.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button5.sizePolicy().hasHeightForWidth())
        self.button5.setSizePolicy(sizePolicy)
        self.button5.setObjectName("button5")
        self.buttonLayout.addWidget(self.button5, 2, 2, 1, 1)
        self.button1 = QtWidgets.QPushButton(parent=Dialog)
        self.button1.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button1.sizePolicy().hasHeightForWidth())
        self.button1.setSizePolicy(sizePolicy)
        self.button1.setText("")
        self.button1.setObjectName("button1")
        self.buttonLayout.addWidget(self.button1, 3, 1, 1, 1)
        self.button7 = QtWidgets.QPushButton(parent=Dialog)
        self.button7.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button7.sizePolicy().hasHeightForWidth())
        self.button7.setSizePolicy(sizePolicy)
        self.button7.setObjectName("button7")
        self.buttonLayout.addWidget(self.button7, 1, 1, 1, 1)
        self.button8 = QtWidgets.QPushButton(parent=Dialog)
        self.button8.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button8.sizePolicy().hasHeightForWidth())
        self.button8.setSizePolicy(sizePolicy)
        self.button8.setObjectName("button8")
        self.buttonLayout.addWidget(self.button8, 1, 2, 1, 1)
        self.button9 = QtWidgets.QPushButton(parent=Dialog)
        self.button9.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button9.sizePolicy().hasHeightForWidth())
        self.button9.setSizePolicy(sizePolicy)
        self.button9.setText("")
        self.button9.setCheckable(False)
        self.button9.setObjectName("button9")
        self.buttonLayout.addWidget(self.button9, 1, 3, 1, 1)
        self.button3 = QtWidgets.QPushButton(parent=Dialog)
        self.button3.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button3.sizePolicy().hasHeightForWidth())
        self.button3.setSizePolicy(sizePolicy)
        self.button3.setObjectName("button3")
        self.buttonLayout.addWidget(self.button3, 3, 3, 1, 1)
        self.button6 = QtWidgets.QPushButton(parent=Dialog)
        self.button6.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button6.sizePolicy().hasHeightForWidth())
        self.button6.setSizePolicy(sizePolicy)
        self.button6.setObjectName("button6")
        self.buttonLayout.addWidget(self.button6, 2, 3, 1, 1)
        self.layout.addLayout(self.buttonLayout)

        self.retranslateUi(Dialog)
        self.space.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Organisation"))
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
        self.groupBox_2.setTitle(_translate("Dialog", "alle Aufgaben"))
        self.tasks_table.setSortingEnabled(True)
        self.groupBox_3.setTitle(_translate("Dialog", "bearbeite aktuell:"))
        self.concerned_task_table.setSortingEnabled(True)
        self.relationship_button.setText(_translate("Dialog", "hängt ab von"))
        self.sub_sup_tasks_table.setSortingEnabled(True)
        self.button4.setText(_translate("Dialog", "bearbeite Aufgabe(n)"))
        self.button4.setShortcut(_translate("Dialog", "4"))
        self.button5.setText(_translate("Dialog", "Bezug auswählen"))
        self.button5.setShortcut(_translate("Dialog", "5"))
        self.button1.setShortcut(_translate("Dialog", "1"))
        self.button7.setText(_translate("Dialog", "Wann, Wo, Wer,..."))
        self.button7.setShortcut(_translate("Dialog", "7"))
        self.button8.setText(_translate("Dialog", "Visualisierung..."))
        self.button8.setShortcut(_translate("Dialog", "8"))
        self.button9.setShortcut(_translate("Dialog", "9"))
        self.button3.setText(_translate("Dialog", "organisiere Aufgaben"))
        self.button3.setShortcut(_translate("Dialog", "3"))
        self.button6.setText(_translate("Dialog", "neue Aufgabe"))
        self.button6.setShortcut(_translate("Dialog", "6"))
