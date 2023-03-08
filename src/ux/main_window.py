class MainWindow(QtWidgets.QMainWindow, ui.main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        @self.about.triggered.connect
        def _():
            win = About()
            win.exec()

        @self.actionReadme.triggered.connect
        def _():
            webbrowser.open("https://github.com/amogorkon/watnu/blob/main/README.md")

        @self.attributions.triggered.connect
        def _():
            app.win_attributions = Attributions()
            win_attributions.show()

        @self.button7.clicked.connect
        def _():
            pass

        @self.button8.clicked.connect
        def companions():
            app.win_companions = Companions()
            app.win_companions.show()

        @self.button9.clicked.connect
        def community():
            """Community."""
            webbrowser.open("https://watnu.slack.com/archives/C01HKH7R4AC")

        @self.button4.clicked.connect
        def list_tasks():
            """Task List."""
            win = TaskList()
            win.show()
            app.list_of_task_lists.append(win)

        @self.button5.clicked.connect
        def whatnow():
            """Watnu?!"""
            if app.win_what.lets_check_whats_next():
                app.win_what.show()
                self.hide()

        @self.button6.clicked.connect
        def add_new_task():
            """Add new Task."""
            win = Editor()
            win.exec()

        @self.button1.clicked.connect
        def statistics():
            app.win_statistics = Statistics()
            app.win_statistics.show()

        @self.button2.clicked.connect
        def character():
            app.win_character = Character()
            app.win_character.show()

        @self.button3.clicked.connect
        def inventory():
            app.win_inventory.show()

        @self.actionSupportMe.triggered.connect
        def actionSupportMe_triggered():
            webbrowser.open("paypal.me/amogorkon")

        @self.actionIssue_Tracker.triggered.connect
        def actionIssueTracker():
            webbrowser.open("https://github.com/amogorkon/watnu/issues")

        @self.actionContact.triggered.connect
        def actionContact():
            webbrowser.open("https://calendly.com/d/2fm-27w-njm/office-hours")

        @self.actionSettings.triggered.connect
        def actionSettings():
            app.win_settings.show()

        @self.actionExport.triggered.connect
        def actionExport():
            q("Not Implemented.")
            return

        @self.actionImport.triggered.connect
        def actionImport():
            win = QtWidgets.QDialog()
            options = QtWidgets.QFileDialog.Options()
            # options |= QtWidgets.QFileDialog.DontUseNativeDialog
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                win,
                "Bitte wähle eine .todo Datei zum Importieren",
                "",
                "Todo Files (*.todo);;All Files (*)",
                options=options,
            )
            if filename:
                path = Path(filename)
                with open(path) as f:
                    for d in load(f):
                        d = defaultdict(lambda: None, **d)
                        d["space"] = path.stem
                        if not d["do"]:
                            q(f"Tried to load a task with nothing to 'do': {d.items()}.")
                            continue

                        submit_sql(
                            f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{d["space"]}')
"""
                        )

                        submit_sql(
                            f"""
INSERT INTO tasks (do, space_id, done)
VALUES ('{d["do"]}',
(SELECT space_id from spaces WHERE name='{d["space"]}'),
{int(bool(d["done"]))} 
)
"""
                        )

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to close the window?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            q(config.count)
            if config.autostart and False:  # TODO
                import getpass

                try:
                    link = rf"C:\Users\{getpass.getuser()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Start Watnu.bat"
                    target = Path(sys.executable)
                    with open(Path(link), "w+") as file:
                        file.write(rf'start "" {target}')
                except Exception as e:
                    q(e, link, target)

            config.write()
            tray.setVisible(False)
            event.accept()
        else:
            event.ignore()
