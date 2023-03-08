# Form implementation generated from reading ui file 'ui\landing.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        Wizard.resize(610, 371)
        Wizard.setModal(True)
        Wizard.setWizardStyle(QtWidgets.QWizard.WizardStyle.ModernStyle)
        Wizard.setOptions(QtWidgets.QWizard.WizardOption.HaveFinishButtonOnEarlyPages|QtWidgets.QWizard.WizardOption.IgnoreSubTitles|QtWidgets.QWizard.WizardOption.NoBackButtonOnStartPage|QtWidgets.QWizard.WizardOption.NoCancelButton)
        self.wizardPage1 = QtWidgets.QWizardPage()
        self.wizardPage1.setObjectName("wizardPage1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.wizardPage1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.face = QtWidgets.QLabel(parent=self.wizardPage1)
        self.face.setText("")
        self.face.setPixmap(QtGui.QPixmap("ui\\../extra/faces/alexa.png"))
        self.face.setScaledContents(False)
        self.face.setObjectName("face")
        self.horizontalLayout.addWidget(self.face)
        self.textBrowser = QtWidgets.QTextBrowser(parent=self.wizardPage1)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout.addWidget(self.textBrowser)
        Wizard.addPage(self.wizardPage1)
        self.wizardPage = QtWidgets.QWizardPage()
        self.wizardPage.setObjectName("wizardPage")
        self.textBrowser_2 = QtWidgets.QTextBrowser(parent=self.wizardPage)
        self.textBrowser_2.setGeometry(QtCore.QRect(270, 10, 330, 271))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.pushButton = QtWidgets.QPushButton(parent=self.wizardPage)
        self.pushButton.setGeometry(QtCore.QRect(50, 210, 181, 51))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.wizardPage)
        self.pushButton_2.setGeometry(QtCore.QRect(90, 270, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.db_file_name = QtWidgets.QLabel(parent=self.wizardPage)
        self.db_file_name.setGeometry(QtCore.QRect(50, 140, 181, 41))
        self.db_file_name.setText("")
        self.db_file_name.setObjectName("db_file_name")
        Wizard.addPage(self.wizardPage)

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
        self.textBrowser_2.setHtml(_translate("Wizard", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Auswahl der Datenbank</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Willst du eine bestimmte existierende Datenbank für deine Aufgaben verwenden? Hier kannst du zum Beispiel auch eine Datei wählen, die in deiner Dropbox liegt. Wählst du nichts aus, wird eine neue Datenbank angelegt.</p></body></html>"))
        self.pushButton.setText(_translate("Wizard", "Existierende Datenbank auswählen"))
        self.pushButton_2.setText(_translate("Wizard", "Mach neu!"))