# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\companions.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(660, 349)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.face_left = QtWidgets.QLabel(Dialog)
        self.face_left.setText("")
        self.face_left.setPixmap(QtGui.QPixmap("ui\\../extra/faces/face1.png"))
        self.face_left.setObjectName("face_left")
        self.horizontalLayout.addWidget(self.face_left)
        self.face_right = QtWidgets.QLabel(Dialog)
        self.face_right.setText("")
        self.face_right.setPixmap(QtGui.QPixmap("ui\\../extra/faces/face3.png"))
        self.face_right.setObjectName("face_right")
        self.horizontalLayout.addWidget(self.face_right)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
