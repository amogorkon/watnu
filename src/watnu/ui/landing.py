# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\landing.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.setWindowModality(QtCore.Qt.ApplicationModal)
        Wizard.resize(610, 365)
        Wizard.setModal(True)
        Wizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        Wizard.setOptions(QtWidgets.QWizard.HaveFinishButtonOnEarlyPages|QtWidgets.QWizard.IgnoreSubTitles|QtWidgets.QWizard.NoBackButtonOnStartPage|QtWidgets.QWizard.NoCancelButton)
        self.wizardPage1 = QtWidgets.QWizardPage()
        self.wizardPage1.setObjectName("wizardPage1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.wizardPage1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.face = QtWidgets.QLabel(self.wizardPage1)
        self.face.setText("")
        self.face.setPixmap(QtGui.QPixmap("ui\\../extra/faces/alexa.png"))
        self.face.setScaledContents(False)
        self.face.setObjectName("face")
        self.horizontalLayout.addWidget(self.face)
        self.textBrowser = QtWidgets.QTextBrowser(self.wizardPage1)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout.addWidget(self.textBrowser)
        Wizard.addPage(self.wizardPage1)

        self.retranslateUi(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Watnu - Einstieg"))
        self.textBrowser.setHtml(_translate("Wizard", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Willkommen zu Watnu!</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Auf den folgenden Seiten wirst du die wichtigsten Funktionen kennenlernen um Watnu effektiv einsetzen zu können.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Lass uns anfangen!</p></body></html>"))
