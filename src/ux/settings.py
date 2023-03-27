import sqlite3

from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt, QVariant
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import QMessageBox

_translate = QCoreApplication.translate


import q

import ui
from classes import Task, cached_and_invalidated, typed, typed_row

from stuff import __version__, app, db



class Settings(QtWidgets.QDialog, ui.settings.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.build_spaces_table()
        self.space_id = None

        self.skills_table.horizontalHeader().setVisible(True)
        self.skills_table.setColumnHidden(0, True)
        self.skills_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.build_skill_table()

        @self.create_skill.clicked.connect
        def _():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self, "Neue Aktivität", "Name der neuen Aktivität", QtWidgets.QLineEdit.Normal, ""
            )
            if okPressed and text != "":
                db.execute(
                    f"""
INSERT OR IGNORE INTO skills (name)
VALUES ('{text}')
"""
                )
                db.commit()
                self.build_skill_table()

        @self.rename_skill.clicked.connect
        def _():
            try:
                x = self.skills_table.selectedItems()[0].row()
            except IndexError:
                return

            skill_id = self.skills_table.item(x, 1).data(Qt.ItemDataRole.UserRole)
            name = self.skills_table.item(x, 1).text()

            text, okPressed = QtWidgets.QInputDialog.getText(
                self,
                "Fähigkeit umbenennen",
                f"Wie soll die Fähigkeit '{name}' umbenannt werden?",
                QtWidgets.QLineEdit.Normal,
                "",
            )

            if okPressed and text != "":
                db.execute(
                    f"""
UPDATE skills 
SET name = '{text}'
WHERE skill_id == {skill_id};
"""
                )
                db.commit()
                self.build_skill_table()

        @self.clear_unused_resources.clicked.connect
        def _():
            q("sanitizing db..")
            app.sanitize_db()

        @self.clear_all_deleted.clicked.connect
        def _():
            db.execute(
                """
DELETE FROM tasks WHERE deleted == TRUE;
"""
            )
            db.execute(
                """
DELETE FROM sessions 
WHERE NOT EXISTS(SELECT NULL
FROM tasks
WHERE sessions.task_id = tasks.id)
"""
            )

        @self.delete_skill.clicked.connect
        def _():
            try:
                x = self.skills_table.selectedItems()[0].row()
            except IndexError:
                return

            skill_id = self.skills_table.item(x, 1).data(Qt.ItemDataRole.UserRole)
            name = self.skills_table.item(x, 1).text()

            match QMessageBox.question(self, "Bitte bestätigen!", f"Wirklich Fähigkeit '{name}' löschen?"):
                case QMessageBox.StandardButton.Yes:
                    db.execute(
                        f"""
    DELETE FROM skills WHERE skill_id == {skill_id};
    """
                    )
                    self.skills_table.removeRow(x)
                    self.update()

        # SPACES

        @self.create_space.clicked.connect
        def _():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self, "Neuer Space", "Name des neuen Space", QtWidgets.QLineEdit.Normal, ""
            )
            if okPressed and text != "":
                db.execute(
                    f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
                )
                db.commit()
                self.build_spaces_table()

        @self.delete_space.clicked.connect
        def _():
            try:
                x = self.spaces_table.selectedItems()[0].row()
            except IndexError:
                return

            space_id = self.spaces_table.item(x, 0).data(Qt.ItemDataRole.UserRole)
            name = self.spaces_table.item(x, 0).text()

            match QMessageBox.question(self, "Bitte bestätigen!", f"Wirklich Space '{name}' löschen?"):
                case QMessageBox.StandardButton.Yes:
                    db.execute(
                        f"""
    DELETE FROM spaces WHERE space_id == {space_id};
    """
                    )
                    self.spaces_table.removeRow(x)
                    self.update()

        @self.spaces_table.itemSelectionChanged.connect
        def _():
            self.space_name.setEnabled(True)
            self.space_primary_activity.setEnabled(True)
            self.space_secondary_activity.setEnabled(True)
            self.space_priority.setEnabled(True)

            self.space_id = self.spaces_table.item(self.spaces_table.selectedItems()[0].row(), 0).data(
                Qt.ItemDataRole.UserRole
            )
            query = db.execute(
                f"""
SELECT space_id, name, priority, primary_activity_id, secondary_activity_id
FROM spaces 
WHERE space_id = {self.space_id}
"""
            )
            for space_id, name, priority, primary_activity_id, secondary_activity_id in query.fetchall():
                self.space_name.setText(typed(name, str))
                self.space_priority.setValue(typed(priority, float))
                self.space_primary_activity.setCurrentIndex(
                    x
                    if (x := self.space_primary_activity.findData(QVariant(typed(primary_activity_id, int))))
                    != -1
                    else 0
                )
                self.space_secondary_activity.setCurrentIndex(
                    x
                    if (
                        x := self.space_secondary_activity.findData(
                            QVariant(typed(secondary_activity_id, int))
                        )
                    )
                    != -1
                    else 0
                )

        @self.space_name.textChanged.connect
        def space_name_changed():
            db.execute(
                f"""
UPDATE spaces
SET name = '{self.space_name.toPlainText()}'
WHERE space_id = {self.space_id}
            """
            )
            db.commit()
            self.spaces_table.item(self.spaces_table.selectedItems()[0].row(), 0).setText(
                self.space_name.toPlainText()
            )

        @self.space_priority.valueChanged.connect
        def space_priority_changed():
            db.execute(
                f"""
UPDATE spaces
SET priority = {self.space_priority.value()}
WHERE space_id = {self.space_id}
            """,
            )
            db.commit()

        @self.space_primary_activity.currentIndexChanged.connect
        def _():
            x = self.space_primary_activity.itemData(self.space_primary_activity.currentIndex())
            db.execute(
                f"""
UPDATE spaces
SET primary_activity_id = {x if x is not None else "NULL"}
WHERE space_id = {self.space_id}
"""
            )
            db.commit()

        @self.space_secondary_activity.currentIndexChanged.connect
        def _():
            x = self.space_secondary_activity.itemData(self.space_secondary_activity.currentIndex())
            db.execute(
                f"""
UPDATE spaces
SET secondary_activity_id = {x if x is not None else "NULL"}
WHERE space_id = {self.space_id}
"""
            )
            db.commit()

    def build_skill_table(self):
        query = db.execute(
            """
        SELECT skill_id, name FROM skills;
        """
        )
        self.skills_table.setSortingEnabled(False)

        for i, (skill_id, name) in enumerate(query.fetchall()):
            self.skills_table.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(typed(name, str))
            self.skills_table.setItem(i, 1, item)
            item.setText(typed(name, str))
            item.setData(Qt.ItemDataRole.UserRole, typed(skill_id, int))

            inner_query = db.execute(
                f"""
SELECT COUNT(*) FROM task_trains_skill WHERE skill_id == {str(typed(skill_id, int))};
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, 0)))
            self.skills_table.setItem(i, 2, item)

        self.skills_table.setSortingEnabled(True)
        self.skills_table.sortItems(0)  # ? strange
        self.update()

    def build_spaces_table(self):
        query = db.execute(
            """
        SELECT space_id, name FROM spaces;
        """
        )
        self.spaces_table.setSortingEnabled(False)

        for i, (space_id, name) in enumerate(query.fetchall()):
            space_id = typed(space_id, int)
            name = typed(name, str)
            self.spaces_table.setRowCount(i + 1)
            item = QtWidgets.QTableWidgetItem(name)
            self.spaces_table.setItem(i, 0, item)
            item.setData(Qt.ItemDataRole.UserRole, space_id)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            inner_query = db.execute(
                f"""
SELECT COUNT(*) FROM tasks WHERE space_id == {space_id};
"""
            )
            item = QtWidgets.QTableWidgetItem(str(typed_row(inner_query.fetchone(), 0, int, 0)))
            self.spaces_table.setItem(i, 1, item)

        self.spaces_table.setSortingEnabled(True)
        self.spaces_table.sortItems(0)  # ? strange

        query = db.execute(
            """
        SELECT activity_id, name FROM activities;
        """
        )

        for activity_id, name in query.fetchall():
            self.space_primary_activity.addItem(typed(name, str), QVariant(typed(activity_id, int)))
            self.space_secondary_activity.addItem(typed(name, str), QVariant(typed(activity_id, int)))
        self.update()

    def reject(self):
        super().reject()
        self.hide()
        app.win_main.show()
        app.win_main.raise_()
