from datetime import datetime

from PyQt6.QtCore import QSize, QVariant
from PyQt6.QtWidgets import QComboBox

from src import db
from src.classes import Task, typed, typed_row
from src.helpers import pipes
from src.logic import (
    filter_tasks_by_ilk,
    filter_tasks_by_space,
    filter_tasks_by_status,
)


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
    def build_space_list(self, first_item_text="alle Räume") -> None:
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

        # set the horizontal size of the widget to the size of the longest item in the list
        self.space.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

        self.space.setMinimumSize(QSize(120, 0))
        self.space.adjustSize()
        self.update()


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
