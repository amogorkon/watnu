class About(QtWidgets.QDialog, ui.about.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.version.setText(str(__version__))
