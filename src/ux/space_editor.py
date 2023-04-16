from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication

import ui
from stuff import __version__

_translate = QCoreApplication.translate

import ux
from stuff import app, db


class Space_Editor(QtWidgets.QDialog, ui.space_editor.Ui_Dialog):
    def __init__(self, space_name: str):
        super().__init__()
        self.setupUi(self)
        self.former_name = space_name
        self.name.setText(space_name)
        self.priority.setValue(
            db.execute("SELECT priority FROM spaces WHERE name=?", (space_name,)).fetchone()[0]
        )
        # self.primary_activity.setCurrentIndex(
        #     self.primary_activity.findText(
        #         db.execute("SELECT primary_activity FROM spaces WHERE name=?", (space_name,)).fetchone()[0]
        #     )
        # )
        # self.secondary_activity.setCurrentIndex(
        #     self.secondary_activity.findText(
        #         db.execute("SELECT secondary_activity FROM spaces WHERE name=?", (space_name,)).fetchone()[0]
        #     )
        # )

    def accept(self):
        db.execute("UPDATE spaces SET name=? WHERE name=?", (self.name.text(), self.former_name))
        for win in app.list_of_task_lists:
            ux.task_list.build_space_list(win)
            if win.space.currentText() == self.name.text():
                win.space.setCurrentText(self.name.text())
        for win in app.list_of_task_editors:
            ux.task_list.build_space_list(win)
            if win.space.currentText() == self.name.text():
                win.space.setCurrentText(self.name.text())

        for win in app.list_of_task_organizers:
            ux.task_list.build_space_list(win)
            if win.space.currentText() == self.name.text():
                win.space.setCurrentText(self.name.text())

        # update priority in db
        db.execute("UPDATE spaces SET priority=? WHERE name=?", (self.priority.value(), self.name.text()))

        # update priority and activities in db
        # db.execute(
        #     "UPDATE spaces SET priority=?, primary_activity=?, secondary_activity=? WHERE name=?",
        #     (
        #         self.priority.value(),
        #         self.primary_activity.currentText(),
        #         self.secondary_activity.currentText(),
        #         self.name.text(),
        #     ),
        # )
        db.commit()

        super().accept()
