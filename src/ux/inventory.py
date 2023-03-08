class Inventory(QtWidgets.QDialog, ui.inventory.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def reject(self):
        super().reject()
        win_inventory = None
