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
        config.database = self.db_file_name.text() or "watnu.sqlite"
        import first_start

        first_start.run(db, config)

        super().done(status)
