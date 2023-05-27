# Form implementation generated from reading ui file 'src\ui\task_editor.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(567, 700)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Wizard.sizePolicy().hasHeightForWidth())
        Wizard.setSizePolicy(sizePolicy)
        Wizard.setMinimumSize(QtCore.QSize(500, 700))
        Wizard.setSizeGripEnabled(True)
        Wizard.setModal(False)
        Wizard.setWizardStyle(QtWidgets.QWizard.WizardStyle.ModernStyle)
        Wizard.setOptions(QtWidgets.QWizard.WizardOption.CancelButtonOnLeft|QtWidgets.QWizard.WizardOption.HaveCustomButton1|QtWidgets.QWizard.WizardOption.HaveCustomButton2|QtWidgets.QWizard.WizardOption.HaveFinishButtonOnEarlyPages|QtWidgets.QWizard.WizardOption.HaveHelpButton|QtWidgets.QWizard.WizardOption.IgnoreSubTitles|QtWidgets.QWizard.WizardOption.NoBackButtonOnStartPage)
        self.page = QtWidgets.QWizardPage()
        self.page.setObjectName("page")
        self.page_layout = QtWidgets.QVBoxLayout(self.page)
        self.page_layout.setObjectName("page_layout")
        self.groupBox = QtWidgets.QGroupBox(parent=self.page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.do = QtWidgets.QTextEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.do.sizePolicy().hasHeightForWidth())
        self.do.setSizePolicy(sizePolicy)
        self.do.setMaximumSize(QtCore.QSize(16777215, 500))
        self.do.setMouseTracking(True)
        self.do.setTabletTracking(True)
        self.do.setAutoFillBackground(True)
        self.do.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.do.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.do.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.do.setAutoFormatting(QtWidgets.QTextEdit.AutoFormattingFlag.AutoAll)
        self.do.setTabChangesFocus(True)
        self.do.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextBrowserInteraction|QtCore.Qt.TextInteractionFlag.TextEditable|QtCore.Qt.TextInteractionFlag.TextEditorInteraction|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.do.setObjectName("do")
        self.verticalLayout.addWidget(self.do)
        self.task_type = QtWidgets.QGroupBox(parent=self.groupBox)
        self.task_type.setObjectName("task_type")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.task_type)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.is_task = QtWidgets.QRadioButton(parent=self.task_type)
        self.is_task.setChecked(True)
        self.is_task.setObjectName("is_task")
        self.kind_of = QtWidgets.QButtonGroup(Wizard)
        self.kind_of.setObjectName("kind_of")
        self.kind_of.addButton(self.is_task)
        self.horizontalLayout_5.addWidget(self.is_task)
        self.is_tradition = QtWidgets.QRadioButton(parent=self.task_type)
        self.is_tradition.setObjectName("is_tradition")
        self.kind_of.addButton(self.is_tradition)
        self.horizontalLayout_5.addWidget(self.is_tradition)
        self.is_routine = QtWidgets.QRadioButton(parent=self.task_type)
        self.is_routine.setObjectName("is_routine")
        self.kind_of.addButton(self.is_routine)
        self.horizontalLayout_5.addWidget(self.is_routine)
        self.is_habit = QtWidgets.QRadioButton(parent=self.task_type)
        self.is_habit.setObjectName("is_habit")
        self.kind_of.addButton(self.is_habit)
        self.horizontalLayout_5.addWidget(self.is_habit)
        self.verticalLayout.addWidget(self.task_type)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.resources = QtWidgets.QComboBox(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resources.sizePolicy().hasHeightForWidth())
        self.resources.setSizePolicy(sizePolicy)
        self.resources.setCurrentText("")
        self.resources.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAlphabetically)
        self.resources.setObjectName("resources")
        self.horizontalLayout_4.addWidget(self.resources)
        self.resource_remove = QtWidgets.QPushButton(parent=self.groupBox_2)
        self.resource_remove.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("src\\ui\\../extra/feathericons/minus.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.resource_remove.setIcon(icon)
        self.resource_remove.setObjectName("resource_remove")
        self.horizontalLayout_4.addWidget(self.resource_remove)
        self.resource_add = QtWidgets.QPushButton(parent=self.groupBox_2)
        self.resource_add.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("src\\ui\\../extra/feathericons/plus.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.resource_add.setIcon(icon1)
        self.resource_add.setObjectName("resource_add")
        self.horizontalLayout_4.addWidget(self.resource_add)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.page_layout.addWidget(self.groupBox)
        self.notes = QtWidgets.QPlainTextEdit(parent=self.page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.notes.sizePolicy().hasHeightForWidth())
        self.notes.setSizePolicy(sizePolicy)
        self.notes.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.notes.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextBrowserInteraction|QtCore.Qt.TextInteractionFlag.TextEditable|QtCore.Qt.TextInteractionFlag.TextEditorInteraction|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.notes.setObjectName("notes")
        self.page_layout.addWidget(self.notes)
        self.groupBox_6 = QtWidgets.QGroupBox(parent=self.page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_6.sizePolicy().hasHeightForWidth())
        self.groupBox_6.setSizePolicy(sizePolicy)
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(-1, -1, 0, -1)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox_6)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_3)
        self.space = QtWidgets.QComboBox(parent=self.groupBox_6)
        self.space.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.space.sizePolicy().hasHeightForWidth())
        self.space.setSizePolicy(sizePolicy)
        self.space.setMinimumSize(QtCore.QSize(120, 0))
        self.space.setSizeIncrement(QtCore.QSize(0, 0))
        self.space.setCurrentText("")
        self.space.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.space.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.space.setFrame(True)
        self.space.setModelColumn(0)
        self.space.setObjectName("space")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.space)
        self.label = QtWidgets.QLabel(parent=self.groupBox_6)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.priority = QtWidgets.QDoubleSpinBox(parent=self.groupBox_6)
        self.priority.setDecimals(3)
        self.priority.setMinimum(0.0)
        self.priority.setMaximum(99999.99)
        self.priority.setObjectName("priority")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.priority)
        self.label_7 = QtWidgets.QLabel(parent=self.groupBox_6)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_7)
        self.total_priority = QtWidgets.QDoubleSpinBox(parent=self.groupBox_6)
        self.total_priority.setEnabled(True)
        self.total_priority.setReadOnly(True)
        self.total_priority.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.total_priority.setDecimals(3)
        self.total_priority.setMaximum(99999.99)
        self.total_priority.setObjectName("total_priority")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.total_priority)
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox_6)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_4)
        self.level = QtWidgets.QComboBox(parent=self.groupBox_6)
        self.level.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.level.sizePolicy().hasHeightForWidth())
        self.level.setSizePolicy(sizePolicy)
        self.level.setCurrentText("")
        self.level.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.level.setFrame(True)
        self.level.setObjectName("level")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.level)
        self.label_6 = QtWidgets.QLabel(parent=self.groupBox_6)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_6)
        self.secondary_activity = QtWidgets.QComboBox(parent=self.groupBox_6)
        self.secondary_activity.setObjectName("secondary_activity")
        self.secondary_activity.addItem("")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.secondary_activity)
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.workload_hours = QtWidgets.QSpinBox(parent=self.groupBox_6)
        self.workload_hours.setMaximum(9999)
        self.workload_hours.setObjectName("workload_hours")
        self.horizontalLayout_2.addWidget(self.workload_hours)
        self.workload_minutes = QtWidgets.QSpinBox(parent=self.groupBox_6)
        self.workload_minutes.setObjectName("workload_minutes")
        self.horizontalLayout_2.addWidget(self.workload_minutes)
        self.formLayout.setLayout(10, QtWidgets.QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)
        self.primary_activity = QtWidgets.QComboBox(parent=self.groupBox_6)
        self.primary_activity.setObjectName("primary_activity")
        self.primary_activity.addItem("")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.primary_activity)
        self.label_5 = QtWidgets.QLabel(parent=self.groupBox_6)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_5)
        self.horizontalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, -1, 10, -1)
        self.gridLayout_2.setHorizontalSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.choose_skills_button = QtWidgets.QPushButton(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_skills_button.sizePolicy().hasHeightForWidth())
        self.choose_skills_button.setSizePolicy(sizePolicy)
        self.choose_skills_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("src\\ui\\../extra/skills.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.choose_skills_button.setIcon(icon2)
        self.choose_skills_button.setObjectName("choose_skills_button")
        self.gridLayout_2.addWidget(self.choose_skills_button, 3, 0, 1, 1)
        self.organize_subtasks = QtWidgets.QPushButton(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.organize_subtasks.sizePolicy().hasHeightForWidth())
        self.organize_subtasks.setSizePolicy(sizePolicy)
        self.organize_subtasks.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("src\\ui\\../extra/chevrons-down.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.organize_subtasks.setIcon(icon3)
        self.organize_subtasks.setObjectName("organize_subtasks")
        self.gridLayout_2.addWidget(self.organize_subtasks, 5, 0, 1, 1)
        self.choose_repeats_button = QtWidgets.QPushButton(parent=self.groupBox_6)
        self.choose_repeats_button.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_repeats_button.sizePolicy().hasHeightForWidth())
        self.choose_repeats_button.setSizePolicy(sizePolicy)
        self.choose_repeats_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("src\\ui\\../extra/repeats.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.choose_repeats_button.setIcon(icon4)
        self.choose_repeats_button.setObjectName("choose_repeats_button")
        self.gridLayout_2.addWidget(self.choose_repeats_button, 1, 0, 1, 1)
        self.organize_supertasks = QtWidgets.QPushButton(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.organize_supertasks.sizePolicy().hasHeightForWidth())
        self.organize_supertasks.setSizePolicy(sizePolicy)
        self.organize_supertasks.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("src\\ui\\../extra/chevrons-up.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.organize_supertasks.setIcon(icon5)
        self.organize_supertasks.setObjectName("organize_supertasks")
        self.gridLayout_2.addWidget(self.organize_supertasks, 4, 0, 1, 1)
        self.primary_activity_button = QtWidgets.QPushButton(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.primary_activity_button.sizePolicy().hasHeightForWidth())
        self.primary_activity_button.setSizePolicy(sizePolicy)
        self.primary_activity_button.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("src\\ui\\../extra/mind.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.primary_activity_button.setIcon(icon6)
        self.primary_activity_button.setObjectName("primary_activity_button")
        self.gridLayout_2.addWidget(self.primary_activity_button, 0, 0, 1, 1)
        self.choose_constraints_button = QtWidgets.QPushButton(parent=self.groupBox_6)
        self.choose_constraints_button.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_constraints_button.sizePolicy().hasHeightForWidth())
        self.choose_constraints_button.setSizePolicy(sizePolicy)
        self.choose_constraints_button.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("src\\ui\\../extra/constraints.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.choose_constraints_button.setIcon(icon7)
        self.choose_constraints_button.setObjectName("choose_constraints_button")
        self.gridLayout_2.addWidget(self.choose_constraints_button, 1, 2, 1, 1)
        self.choose_deadline_button = QtWidgets.QPushButton(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_deadline_button.sizePolicy().hasHeightForWidth())
        self.choose_deadline_button.setSizePolicy(sizePolicy)
        self.choose_deadline_button.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("src\\ui\\../extra/feathericons/log-in.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.choose_deadline_button.setIcon(icon8)
        self.choose_deadline_button.setCheckable(False)
        self.choose_deadline_button.setChecked(False)
        self.choose_deadline_button.setObjectName("choose_deadline_button")
        self.gridLayout_2.addWidget(self.choose_deadline_button, 1, 3, 1, 1)
        self.secondary_activity_button = QtWidgets.QPushButton(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.secondary_activity_button.sizePolicy().hasHeightForWidth())
        self.secondary_activity_button.setSizePolicy(sizePolicy)
        self.secondary_activity_button.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("src\\ui\\../extra/soul.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.secondary_activity_button.setIcon(icon9)
        self.secondary_activity_button.setObjectName("secondary_activity_button")
        self.gridLayout_2.addWidget(self.secondary_activity_button, 0, 3, 1, 1)
        self.pushButton = QtWidgets.QPushButton(parent=self.groupBox_6)
        self.pushButton.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("src\\ui\\../extra/body.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton.setIcon(icon10)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 0, 2, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, -1, 10, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_9 = QtWidgets.QGroupBox(parent=self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_9.sizePolicy().hasHeightForWidth())
        self.groupBox_9.setSizePolicy(sizePolicy)
        self.groupBox_9.setTitle("")
        self.groupBox_9.setFlat(False)
        self.groupBox_9.setObjectName("groupBox_9")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_9)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(-1, -1, 10, -1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.fear_label = QtWidgets.QLabel(parent=self.groupBox_9)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fear_label.sizePolicy().hasHeightForWidth())
        self.fear_label.setSizePolicy(sizePolicy)
        self.fear_label.setText("")
        self.fear_label.setPixmap(QtGui.QPixmap("src\\ui\\../extra/fear.png"))
        self.fear_label.setScaledContents(False)
        self.fear_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.fear_label.setObjectName("fear_label")
        self.verticalLayout_4.addWidget(self.fear_label)
        self.fear = QtWidgets.QSlider(parent=self.groupBox_9)
        self.fear.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.fear.setObjectName("fear")
        self.verticalLayout_4.addWidget(self.fear)
        self.horizontalLayout_6.addLayout(self.verticalLayout_4)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(-1, -1, 10, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.difficulty_label = QtWidgets.QLabel(parent=self.groupBox_9)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.difficulty_label.sizePolicy().hasHeightForWidth())
        self.difficulty_label.setSizePolicy(sizePolicy)
        self.difficulty_label.setText("")
        self.difficulty_label.setPixmap(QtGui.QPixmap("src\\ui\\../extra/complexity.png"))
        self.difficulty_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.difficulty_label.setObjectName("difficulty_label")
        self.verticalLayout_5.addWidget(self.difficulty_label)
        self.difficulty = QtWidgets.QSlider(parent=self.groupBox_9)
        self.difficulty.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.difficulty.setObjectName("difficulty")
        self.verticalLayout_5.addWidget(self.difficulty)
        self.horizontalLayout_6.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setContentsMargins(-1, -1, 10, -1)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.embarrassment_label = QtWidgets.QLabel(parent=self.groupBox_9)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.embarrassment_label.sizePolicy().hasHeightForWidth())
        self.embarrassment_label.setSizePolicy(sizePolicy)
        self.embarrassment_label.setText("")
        self.embarrassment_label.setPixmap(QtGui.QPixmap("src\\ui\\../extra/feathericons/eye.svg"))
        self.embarrassment_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.embarrassment_label.setObjectName("embarrassment_label")
        self.verticalLayout_6.addWidget(self.embarrassment_label)
        self.embarrassment = QtWidgets.QSlider(parent=self.groupBox_9)
        self.embarrassment.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.embarrassment.setObjectName("embarrassment")
        self.verticalLayout_6.addWidget(self.embarrassment)
        self.horizontalLayout_6.addLayout(self.verticalLayout_6)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_6)
        self.verticalLayout_3.addWidget(self.groupBox_9)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.page_layout.addWidget(self.groupBox_6)
        self.num_buttons = QtWidgets.QGridLayout()
        self.num_buttons.setContentsMargins(-1, 9, -1, -1)
        self.num_buttons.setObjectName("num_buttons")
        self.button6 = QtWidgets.QPushButton(parent=self.page)
        self.button6.setEnabled(True)
        self.button6.setObjectName("button6")
        self.num_buttons.addWidget(self.button6, 4, 2, 1, 1)
        self.button5 = QtWidgets.QPushButton(parent=self.page)
        self.button5.setObjectName("button5")
        self.num_buttons.addWidget(self.button5, 4, 1, 1, 1)
        self.button2 = QtWidgets.QPushButton(parent=self.page)
        self.button2.setEnabled(True)
        self.button2.setObjectName("button2")
        self.num_buttons.addWidget(self.button2, 6, 1, 1, 1)
        self.button4 = QtWidgets.QPushButton(parent=self.page)
        self.button4.setEnabled(False)
        self.button4.setText("")
        self.button4.setObjectName("button4")
        self.num_buttons.addWidget(self.button4, 4, 0, 1, 1)
        self.button3 = QtWidgets.QPushButton(parent=self.page)
        self.button3.setEnabled(True)
        self.button3.setObjectName("button3")
        self.num_buttons.addWidget(self.button3, 6, 2, 1, 1)
        self.button7 = QtWidgets.QPushButton(parent=self.page)
        self.button7.setEnabled(True)
        self.button7.setObjectName("button7")
        self.num_buttons.addWidget(self.button7, 2, 0, 1, 1)
        self.button1 = QtWidgets.QPushButton(parent=self.page)
        self.button1.setObjectName("button1")
        self.num_buttons.addWidget(self.button1, 6, 0, 1, 1)
        self.button8 = QtWidgets.QPushButton(parent=self.page)
        self.button8.setEnabled(True)
        self.button8.setObjectName("button8")
        self.num_buttons.addWidget(self.button8, 2, 1, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.button9a = QtWidgets.QPushButton(parent=self.page)
        self.button9a.setEnabled(True)
        self.button9a.setObjectName("button9a")
        self.horizontalLayout_8.addWidget(self.button9a)
        self.button9b = QtWidgets.QPushButton(parent=self.page)
        self.button9b.setObjectName("button9b")
        self.horizontalLayout_8.addWidget(self.button9b)
        self.num_buttons.addLayout(self.horizontalLayout_8, 2, 2, 1, 1)
        self.page_layout.addLayout(self.num_buttons)
        Wizard.addPage(self.page)
        self.label_3.setBuddy(self.space)
        self.label.setBuddy(self.priority)
        self.label_4.setBuddy(self.level)
        self.label_6.setBuddy(self.secondary_activity)
        self.label_2.setBuddy(self.workload_hours)
        self.label_5.setBuddy(self.primary_activity)

        self.retranslateUi(Wizard)
        self.level.setCurrentIndex(-1)
        self.secondary_activity.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Bearbeite Aufgabe"))
        self.page.setTitle(_translate("Wizard", "Beschreibung"))
        self.do.setPlaceholderText(_translate("Wizard", "Was es zu tun gibt..."))
        self.task_type.setTitle(_translate("Wizard", "Art"))
        self.is_task.setText(_translate("Wizard", "Aufgabe"))
        self.is_tradition.setText(_translate("Wizard", "Tradition"))
        self.is_routine.setText(_translate("Wizard", "Routine"))
        self.is_habit.setText(_translate("Wizard", "Gewohnheit"))
        self.groupBox_2.setTitle(_translate("Wizard", "Resourcen"))
        self.notes.setPlaceholderText(_translate("Wizard", "Notizen"))
        self.groupBox_6.setTitle(_translate("Wizard", "Details"))
        self.label_3.setText(_translate("Wizard", "Raum"))
        self.label.setText(_translate("Wizard", "Priorität"))
        self.label_7.setText(_translate("Wizard", "Totale Priorität"))
        self.label_4.setText(_translate("Wizard", "Level"))
        self.label_6.setText(_translate("Wizard", "Sekundäre Aktivität"))
        self.secondary_activity.setCurrentText(_translate("Wizard", "---"))
        self.secondary_activity.setItemText(0, _translate("Wizard", "---"))
        self.label_2.setText(_translate("Wizard", "Arbeitsaufwand"))
        self.workload_hours.setToolTip(_translate("Wizard", "hours"))
        self.workload_minutes.setToolTip(_translate("Wizard", "minutes"))
        self.primary_activity.setItemText(0, _translate("Wizard", "---"))
        self.label_5.setText(_translate("Wizard", "Primäre Aktivität "))
        self.choose_skills_button.setToolTip(_translate("Wizard", "Fähigkeiten"))
        self.choose_skills_button.setShortcut(_translate("Wizard", "9"))
        self.choose_repeats_button.setToolTip(_translate("Wizard", "Wiederholungen"))
        self.choose_repeats_button.setShortcut(_translate("Wizard", "8"))
        self.primary_activity_button.setToolTip(_translate("Wizard", "Geist"))
        self.choose_constraints_button.setToolTip(_translate("Wizard", "Zeitliche Beschränkungen"))
        self.choose_constraints_button.setShortcut(_translate("Wizard", "2"))
        self.choose_deadline_button.setToolTip(_translate("Wizard", "Deadline"))
        self.choose_deadline_button.setShortcut(_translate("Wizard", "7"))
        self.secondary_activity_button.setToolTip(_translate("Wizard", "Seele"))
        self.pushButton.setToolTip(_translate("Wizard", "Körper"))
        self.embarrassment_label.setToolTip(_translate("Wizard", "Peinlichkeit bei Nicht-Erledigung"))
        self.button6.setText(_translate("Wizard", "erstelle neue Aufgabe..."))
        self.button6.setShortcut(_translate("Wizard", "6"))
        self.button5.setText(_translate("Wizard", "beende Bearbeitung und starte Aufgabe"))
        self.button5.setShortcut(_translate("Wizard", "5"))
        self.button2.setText(_translate("Wizard", "Aufgabe erledigt!"))
        self.button2.setShortcut(_translate("Wizard", "2"))
        self.button4.setShortcut(_translate("Wizard", "4"))
        self.button3.setText(_translate("Wizard", "organisiere Aufgaben"))
        self.button3.setShortcut(_translate("Wizard", "3"))
        self.button7.setText(_translate("Wizard", "Wann, Wo, Wer,..."))
        self.button7.setShortcut(_translate("Wizard", "7"))
        self.button1.setText(_translate("Wizard", "setze Aufgabe als..."))
        self.button1.setShortcut(_translate("Wizard", "1"))
        self.button8.setText(_translate("Wizard", "Aufgabe vornehmen für..."))
        self.button8.setShortcut(_translate("Wizard", "8"))
        self.button9a.setText(_translate("Wizard", "Raum..."))
        self.button9a.setShortcut(_translate("Wizard", "9"))
        self.button9b.setText(_translate("Wizard", "Fähigkeiten..."))
        self.button9b.setShortcut(_translate("Wizard", "Ctrl+9"))
