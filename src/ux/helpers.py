import json
from datetime import datetime
from typing import Iterable

from PyQt6.QtGui import QGuiApplication

from src import db
from src.classes import Task, typed_row


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


def to_italic(text):
    """
    Convert text to italic."
    """

    def _gen_map(start, base_char):
        return {chr(ord(base_char) + i): chr(start + i) for i in range(26)}

    combined_map = {
        **_gen_map(0x1D44E, "a"),  # Lowercase
        **_gen_map(0x1D434, "A"),  # Uppercase
    }

    return "".join([combined_map.get(c, c) for c in text])
