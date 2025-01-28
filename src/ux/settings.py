from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QMessageBox

import q
import src.ui as ui
from src.classes import typed, typed_row
from src.stuff import app, db

_translate = QCoreApplication.translate


class Settings(QtWidgets.QDialog, ui.settings.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.skills_table.horizontalHeader().setVisible(True)
        self.skills_table.setColumnHidden(0, True)
        self.skills_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.build_skill_table()

        @self.create_skill.clicked.connect
        def _():
            text, okPressed = QtWidgets.QInputDialog.getText(
                self,
                "Neue Aktivität",
                "Name der neuen Aktivität",
                QtWidgets.QLineEdit.Normal,
                "",
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

            match QMessageBox.question(
                self,
                "Bitte bestätigen!",
                f"Wirklich Fähigkeit '{name}' löschen?",
            ):
                case QMessageBox.StandardButton.Yes:
                    db.execute(
                        f"""
    DELETE FROM skills WHERE skill_id == {skill_id};
    """
                    )
                    self.skills_table.removeRow(x)
                    self.update()

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

    def reject(self):
        super().reject()
        self.hide()
        app.win_main.show()
        app.win_main.raise_()
