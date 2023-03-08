class Companions(QtWidgets.QDialog, ui.companions.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def reject(self):
        super().reject()
        win_companions = None
