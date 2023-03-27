import use
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication

import ui
from stuff import app, config, db

_translate = QCoreApplication.translate

class Landing(QtWidgets.QWizard, ui.landing.Ui_Wizard):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        def def_db():
            path, check = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Bitte wähle eine sqlite Datenbank aus",
                "",
                "*.sqlite",
            )
            if not check:
                return
            else:
                self.db_file_name.setText(path)

        self.pushButton.clicked.connect(def_db)
        self.pushButton_2.clicked.connect(lambda: self.db_file_name.setText(""))

    def done(self, status):
        config.db_path = self.db_file_name.text() or "watnu.sqlite"

        use(use.Path("first_start.py"), initial_globals={"db": db, "config": config}).run()
        config.first_start = False
        config.save()

        super().done(status)
