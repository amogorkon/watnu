import json
from datetime import datetime
from typing import Iterable

from PyQt6.QtCore import QSize, QVariant
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QComboBox, QDialog, QInputDialog, QLineEdit, QMessageBox

from src import app, config, db
from src.classes import Task, typed, typed_row
from src.helpers import pipes
from src.logic import (
    filter_tasks_by_ilk,
    filter_tasks_by_space,
    filter_tasks_by_status,
)

from . import choose_space, skill_editor, space_editor


def get_space_id(name, index) -> int | None:
    return (
        typed_row(
            db.execute(
                """
                SELECT space_id FROM spaces WHERE name=?;
                """,
                (name,),
            ).fetchone(),
            0,
            int | None,
        )
        if index
        else None
    )


def deadline_as_str(deadline: float) -> str:
    if deadline == float("inf"):
        return ""
    try:
        return str(datetime.fromtimestamp(deadline))
    except OSError:
        print(deadline, type(deadline))
        return ""


class SpaceMixin:
    def build_space_list(self, first_item_text="alle Räume", first_time=False) -> None:
        if first_time:
            selected_space = config.last_selected_space or config.last_edited_space

        self.space: QComboBox

        self.space.clear()
        self.space.addItem(first_item_text, QVariant(None))
        # set first item bold
        font = self.space.font()
        font.setBold(True)
        # self.space.item(0).setFont(font)
        self.space.insertSeparator(1)

        query = db.execute(
            """
        SELECT space_id, name FROM spaces;
        """
        )
        spaces = query.fetchall()

        def number_of_tasks_in_space(item):
            space_id = item[0]
            return db.execute(
                """
                SELECT COUNT(*) FROM tasks WHERE space_id=?;
                """,
                (space_id,),
            ).fetchone()[0]

        sorted_spaces_by_number = sorted(spaces, key=number_of_tasks_in_space, reverse=True)

        for space_id, name in sorted_spaces_by_number[:3]:
            self.space.addItem(typed(name, str), QVariant(typed(space_id, int)))

        self.space.insertSeparator(5)

        sorted_spaces_by_name = sorted(sorted_spaces_by_number[3:], key=lambda x: x[1].casefold())
        for space_id, name in sorted_spaces_by_name:
            self.space.addItem(typed(name, str), QVariant(typed(space_id, int)))

        if first_time:
            self.space.setCurrentIndex(self.space.findText(selected_space))

        # set the horizontal size of the widget to the size of the longest item in the list
        self.space.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

        self.space.setMinimumSize(QSize(120, 0))
        self.space.adjustSize()
        self.space.update()
        config.last_selected_space = self.space.currentText() or ""
        config.save()

    def _space_delete(self):
        space_name = self.space.currentText()
        if [task for task in app.tasks.values() if task.space.name == space_name]:
            QMessageBox.information(
                self,
                "Sorry..",
                f"Der Raum '{space_name}' ist nicht leer und kann daher nicht gelöscht werden.",
            )
        else:
            match QMessageBox.question(
                self,
                "Wirklich den ausgewählten Raum löschen?",
                f"Soll der Raum '{space_name}' wirklich gelöscht werden?",
            ):
                case QMessageBox.StandardButton.Yes:
                    db.execute(
                        f"""
DELETE FROM spaces where name=='{space_name}'
"""
                    )
                    db.commit()
                    self.statusBar.showMessage(f"Raum '{space_name}' gelöscht.", 5000)
                    for win in (
                        app.list_of_task_lists + app.list_of_task_editors + app.list_of_task_organizers
                    ):
                        win.build_space_list()
                        if win.space.currentText() == space_name:
                            win.space.setCurrentIndex(0)

    def _space_set(self):
        match (win := choose_space.SpaceSelection()).exec():
            case QDialog.DialogCode.Accepted:
                space = get_space_id(
                    win.space.currentText(),
                    win.space.currentIndex(),
                )
            case _:  # Cancelled
                return
        for task in (selected := self.get_selected_tasks()):
            task.set_("space_id", space)
        self.build_task_table()
        self.statusBar.showMessage(
            f"Raum für {len(selected)} Aufgabe{'' if len(selected) == 1 else 'n'} gesetzt.",
            5000,
        )

    def _space_add(self):
        text, okPressed = QInputDialog.getText(
            self,
            "Neuer Space",
            "Name des neuen Space",
            QLineEdit.EchoMode.Normal,
            "",
        )
        if okPressed and text != "":
            db.execute(
                f"""
INSERT OR IGNORE INTO spaces (name)
VALUES ('{text}')
"""
            )
            db.commit()
            space_editor.SpaceEditor(text).exec()
            self.statusBar.showMessage(f"Raum '{text}' hinzugefügt.", 5000)
            for win in app.list_of_task_editors + app.list_of_task_organizers:
                win.build_space_list()


def get_space_priority(space_id) -> float:
    try:
        return float(
            db.execute(
                "SELECT priority FROM spaces WHERE space_id = ?",
                (space_id,),
            ).fetchone()[0]
        )
    except TypeError:
        return 0


class SkillMixin:
    def _skill_add(self):
        text, okPressed = QInputDialog.getText(
            self,
            "Neuer Skill",
            "Name des neuen Skills",
            QLineEdit.EchoMode.Normal,
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
            skill_editor.SkillEditor(text).exec()
            self.statusBar.showMessage(f"Skill '{text}' hinzugefügt.", 5000)
            for win in app.list_of_task_editors + app.list_of_task_lists:
                win.build_skill_list()

    def _skill_delete(self):
        skill_name = self.space.currentText()
        if [task for task in app.tasks.values() if task.skills.name == skill_name]:
            QMessageBox.information(
                self,
                "Sorry..",
                f"Der Raum '{skill_name}' ist nicht leer und kann daher nicht gelöscht werden.",
            )
        else:
            match QMessageBox.question(
                self,
                "Wirklich den ausgewählten Skill löschen?",
                f"Soll der Skill '{skill_name}' wirklich gelöscht werden?",
            ):
                case QMessageBox.StandardButton.Yes:
                    db.execute(
                        f"""
DELETE FROM skills where name=='{skill_name}'
"""
                    )
                    db.commit()
                    self.statusBar.showMessage(f"Skill '{skill_name}' gelöscht.", 5000)
                    for win in (
                        app.list_of_task_lists + app.list_of_task_editors + app.list_of_task_organizers
                    ):
                        win.build_space_list()
                        if win.skill.currentText() == skill_name:
                            win.skill.setCurrentIndex(0)


@pipes
def filter_tasks(widget, tasks: list[Task]) -> list[Task]:
    """Filter tasks according to the current filter settings."""
    return (
        tasks
        >> filter_tasks_by_space(
            get_space_id(
                widget.space.currentText(),
                widget.space.currentIndex(),
            )
        )
        >> filter_tasks_by_status(widget.status.currentIndex())
        >> filter_tasks_by_ilk(widget.ilk.currentIndex())
        >> list
    )


def to_clipboard(text: str) -> None:
    clipboard = QGuiApplication.clipboard()
    clipboard.setText(text)


def tasks_to_json(tasks: Iterable[Task]) -> str:
    return json.dumps([task.to_dict() for task in tasks if task is not None], indent=2)


def turn_tasks_into_text(tasks: list[Task]) -> str:
    return "\n\n".join(
        f"=== Task {task.id} {task.printable_deadline} {task.printable_percentage} ===\n{task.do}"
        for task in tasks
    )
