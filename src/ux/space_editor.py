from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, QVariant

import src.ui as ui
import src.ux as ux
from src import app, db
from src.classes import ACTIVITY

_translate = QCoreApplication.translate


class SpaceEditor(QtWidgets.QDialog, ui.space_editor.Ui_Dialog):
    def __init__(self, space_name: str):
        super().__init__()
        self.setupUi(self)

        # defaults

        for item in ACTIVITY:
            if item == ACTIVITY.unspecified:
                continue
            self.primary_activity.addItem(item.name, QVariant(item.value))
            self.secondary_activity.addItem(item.name, QVariant(item.value))

        query = db.execute(
            "SELECT primary_activity_id, secondary_activity_id FROM spaces WHERE name=?",
            (space_name,),
        ).fetchone()

        primary_activity_id, secondary_activity_id = query
        if primary_activity_id is not None:
            self.primary_activity.setCurrentIndex(
                self.primary_activity.findData(QVariant(primary_activity_id))
            )
        else:
            self.primary_activity.setCurrentIndex(0)
        if secondary_activity_id is not None:
            self.secondary_activity.setCurrentIndex(
                self.secondary_activity.findData(QVariant(secondary_activity_id))
            )
        else:
            self.secondary_activity.setCurrentIndex(0)

        self.former_name = space_name
        self.name_edit.setText(space_name)
        self.priority.setValue(
            db.execute(
                "SELECT priority FROM spaces WHERE name=?",
                (space_name,),
            ).fetchone()[0]
        )

    def accept(self):
        if self.name_edit.text() != self.former_name:
            db.execute(
                "UPDATE spaces SET name=? WHERE name=?",
                (self.name_edit.text(), self.former_name),
            )
            for win in app.list_of_task_lists:
                ux.task_list.ux.task_list.build_space_list(win)
                if win.space.currentText() == self.name_edit.text():
                    win.space.setCurrentText(self.name_edit.text())
            for win in app.list_of_task_editors:
                ux.task_list.ux.task_list.build_space_list(win)
                if win.space.currentText() == self.name_edit.text():
                    win.space.setCurrentText(self.name_edit.text())

            for win in app.list_of_task_organizers:
                ux.task_list.ux.task_list.build_space_list(win)
                if win.space.currentText() == self.name_edit.text():
                    win.space.setCurrentText(self.name_edit.text())

        # update details
        db.execute(
            "UPDATE spaces SET priority=?, primary_activity_id=?, secondary_activity_id=? WHERE name=?",
            (
                self.priority.value(),
                self.primary_activity.currentData(),
                self.secondary_activity.currentData(),
                self.name_edit.text(),
            ),
        )
        db.commit()

        super().accept()
