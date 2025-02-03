# Form implementation generated from reading ui file 'src\ui\choose_repeats.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(parent=Dialog)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.x_every = QtWidgets.QSpinBox(parent=self.groupBox)
        self.x_every.setMinimum(1)
        self.x_every.setObjectName("x_every")
        self.horizontalLayout.addWidget(self.x_every)
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.every_minute = QtWidgets.QRadioButton(parent=self.groupBox)
        self.every_minute.setObjectName("every_minute")
        self.every_ilk = QtWidgets.QButtonGroup(Dialog)
        self.every_ilk.setObjectName("every_ilk")
        self.every_ilk.addButton(self.every_minute)
        self.verticalLayout_2.addWidget(self.every_minute)
        self.every_hour = QtWidgets.QRadioButton(parent=self.groupBox)
        self.every_hour.setObjectName("every_hour")
        self.every_ilk.addButton(self.every_hour)
        self.verticalLayout_2.addWidget(self.every_hour)
        self.every_day = QtWidgets.QRadioButton(parent=self.groupBox)
        self.every_day.setChecked(True)
        self.every_day.setObjectName("every_day")
        self.every_ilk.addButton(self.every_day)
        self.verticalLayout_2.addWidget(self.every_day)
        self.every_week = QtWidgets.QRadioButton(parent=self.groupBox)
        self.every_week.setObjectName("every_week")
        self.every_ilk.addButton(self.every_week)
        self.verticalLayout_2.addWidget(self.every_week)
        self.every_year = QtWidgets.QRadioButton(parent=self.groupBox)
        self.every_year.setObjectName("every_year")
        self.every_ilk.addButton(self.every_year)
        self.verticalLayout_2.addWidget(self.every_year)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.x_per = QtWidgets.QSpinBox(parent=self.groupBox_2)
        self.x_per.setObjectName("x_per")
        self.verticalLayout_3.addWidget(self.x_per)
        self.per_minute = QtWidgets.QRadioButton(parent=self.groupBox_2)
        self.per_minute.setObjectName("per_minute")
        self.per_ilk = QtWidgets.QButtonGroup(Dialog)
        self.per_ilk.setObjectName("per_ilk")
        self.per_ilk.addButton(self.per_minute)
        self.verticalLayout_3.addWidget(self.per_minute)
        self.per_hour = QtWidgets.QRadioButton(parent=self.groupBox_2)
        self.per_hour.setObjectName("per_hour")
        self.per_ilk.addButton(self.per_hour)
        self.verticalLayout_3.addWidget(self.per_hour)
        self.per_day = QtWidgets.QRadioButton(parent=self.groupBox_2)
        self.per_day.setObjectName("per_day")
        self.per_ilk.addButton(self.per_day)
        self.verticalLayout_3.addWidget(self.per_day)
        self.per_week = QtWidgets.QRadioButton(parent=self.groupBox_2)
        self.per_week.setObjectName("per_week")
        self.per_ilk.addButton(self.per_week)
        self.verticalLayout_3.addWidget(self.per_week)
        self.per_year = QtWidgets.QRadioButton(parent=self.groupBox_2)
        self.per_year.setObjectName("per_year")
        self.per_ilk.addButton(self.per_year)
        self.verticalLayout_3.addWidget(self.per_year)
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Discard|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Reset)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Wähle Wiederholungen"))
        self.groupBox.setTitle(_translate("Dialog", "Wiederhole diese Aufgabe "))
        self.label.setText(_translate("Dialog", "-mal pro.."))
        self.every_minute.setText(_translate("Dialog", "Minute"))
        self.every_hour.setText(_translate("Dialog", "Stunde"))
        self.every_day.setText(_translate("Dialog", "Tag"))
        self.every_week.setText(_translate("Dialog", "Woche"))
        self.every_year.setText(_translate("Dialog", "Jahr"))
        self.groupBox_2.setTitle(_translate("Dialog", "mit mindestens jeweils"))
        self.per_minute.setText(_translate("Dialog", "Minuten"))
        self.per_hour.setText(_translate("Dialog", "Stunden"))
        self.per_day.setText(_translate("Dialog", "Tag"))
        self.per_week.setText(_translate("Dialog", "Woche"))
        self.per_year.setText(_translate("Dialog", "Jahr"))
        self.label_2.setText(_translate("Dialog", "Abstand"))
