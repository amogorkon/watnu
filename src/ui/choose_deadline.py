# Form implementation generated from reading ui file 'src\ui\choose_deadline.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(388, 409)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=Dialog)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setObjectName("tabWidget")
        self.deadline_details = QtWidgets.QWidget()
        self.deadline_details.setObjectName("deadline_details")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.deadline_details)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(parent=self.deadline_details)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self.deadline_details)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_3)
        self.formLayout.setObjectName("formLayout")
        self.in_days = QtWidgets.QSpinBox(parent=self.groupBox_3)
        self.in_days.setMinimum(-999)
        self.in_days.setMaximum(999)
        self.in_days.setObjectName("in_days")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.in_days)
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.label_3)
        self.in_weeks = QtWidgets.QSpinBox(parent=self.groupBox_3)
        self.in_weeks.setMinimum(-999)
        self.in_weeks.setMaximum(999)
        self.in_weeks.setObjectName("in_weeks")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.in_weeks)
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.label_4)
        self.in_months = QtWidgets.QSpinBox(parent=self.groupBox_3)
        self.in_months.setMinimum(-999)
        self.in_months.setMaximum(999)
        self.in_months.setObjectName("in_months")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.in_months)
        self.enter_date = QtWidgets.QPushButton(parent=self.groupBox_3)
        self.enter_date.setObjectName("enter_date")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.enter_date)
        self.gridLayout_3.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.reference_date = QtWidgets.QDateTimeEdit(parent=self.deadline_details)
        self.reference_date.setAccelerated(False)
        self.reference_date.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.reference_date.setCalendarPopup(True)
        self.reference_date.setObjectName("reference_date")
        self.gridLayout_3.addWidget(self.reference_date, 0, 1, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout_3)
        self.tabWidget.addTab(self.deadline_details, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Discard|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Reset)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Wähle Deadline"))
        self.label.setText(_translate("Dialog", "Bezugsdatum"))
        self.groupBox_3.setTitle(_translate("Dialog", "setze"))
        self.label_2.setText(_translate("Dialog", "Tage"))
        self.label_3.setText(_translate("Dialog", "Wochen"))
        self.label_4.setText(_translate("Dialog", "Monate"))
        self.enter_date.setText(_translate("Dialog", "davor/danach als neuen Bezug"))
        self.reference_date.setSpecialValueText(_translate("Dialog", "\"Never\""))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.deadline_details), _translate("Dialog", "Deadline Details"))
