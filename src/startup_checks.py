from datetime import datetime

from PyQt6.QtWidgets import QMessageBox

from src.classes import Task
from src.stuff import app
from src.ux import task_editor


def _clean_up_empty_tasks(tasks: list[Task]) -> None:
    # first, let's clean up empty ones (no do and no notes) - shouldn't exist but just in case
    for task in tasks:
        if task.do == "" and task.notes in ("", None):
            task.really_delete()


def _check_for_drafts(tasks: list[Task]) -> None:
    # let's check for drafts
    if drafts := [t for t in tasks if t.draft]:
        match QMessageBox.question(
            app.win_main,
            "Jetzt bearbeiten?",
            f"Es gibt {f'{len(drafts)} Entwürfe' if len(drafts) > 1 else 'einen Entwurf'} - jetzt bearbeiten?",  # noqa: E501
        ):
            case QMessageBox.StandardButton.Yes:
                for task in drafts:
                    win = task_editor.Editor(task)
                    win.show()


def _check_for_cycles(tasks: list[Task]) -> None:
    while cycle := _cycle_in_task_dependencies(tasks):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Jetzt bearbeiten?")
        msgBox.setText(
            "Zyklus in Sub/Super-Tasks gefunden! Aufgaben wurden als Entwurf markiert! Jetzt bearbeiten?"
        )
        for task in cycle:
            task.set_("draft", True)
        msgBox.addButton("Edit now", QMessageBox.ButtonRole.AcceptRole)
        msgBox.addButton(QMessageBox.StandardButton.Ignore)

        match msgBox.exec():
            case QMessageBox.ButtonRole.AcceptRole.value:
                for task in cycle:
                    win = task_editor.Editor(task)
                    win.show()


def _check_for_duplicates(tasks: list[Task]) -> None:
    # let's check for duplicates

    for task1 in tasks:
        duplicates = set()
        for task2 in tasks:
            if task1 == task2:
                continue
            if task1.do == task2.do and task1.space == task2.space:
                duplicates.add(task1)
                duplicates.add(task2)

        if duplicates:
            match QMessageBox.question(
                app.win_main,
                "Jetzt bearbeiten?",
                "Es gibt Duplikate - jetzt bearbeiten/löschen?",
            ):
                case QMessageBox.StandardButton.Yes:
                    for task in duplicates:
                        win = task_editor.Editor(task)
                        win.show()
                        app.list_of_task_editors.append(win)
                        app.list_of_windows.append(win)


def _check_for_deadline_without_workload(tasks: list[Task]) -> None:
    # let's check if tasks have a deadline without workload
    if bads := [
        task
        for task in tasks
        if task.own_deadline != float("inf")
        and task.workload == 0
        and not task.done
        and not task.deleted
        and not task.draft
        and not task.inactive
    ]:
        match QMessageBox.question(
            app.win_main,
            "Jetzt bearbeiten?",
            f"""Es gibt {f'{len(bads)} Aufgaben ohne Arbeitsaufwand' if len(bads) > 1 else
            'eine Aufgabe ohne Arbeitsaufwand'} aber mit Deadline - jetzt bearbeiten?""",
        ):
            case QMessageBox.StandardButton.Yes:
                for task in bads:
                    win = task_editor.Editor(task)
                    win.show()


def _check_for_overdue_tasks(tasks: list[Task], now: datetime) -> None:
    # let's check for overdue tasks
    if overdue := [task for task in tasks if task.is_overdue(now=now)]:
        match QMessageBox.question(
            app.win_main,
            "Jetzt bearbeiten?",
            f"""Es gibt {f'{len(overdue)} überfällige Aufgaben' if len(overdue) > 1
            else 'eine überfällige Aufgabe'} - jetzt bearbeiten?""",
        ):
            case QMessageBox.StandardButton.Yes:
                for task in overdue:
                    win = task_editor.Editor(task)
                    win.show()


def _check_for_incompletable_tasks(tasks: list[Task], now: datetime) -> None:
    # let's check for tasks that are not yet overdue but incompleatable according to workload
    if incompleteable := [
        task for task in tasks if task.time_buffer <= 0 and not task.is_overdue(now=now) and task.is_doable
    ]:
        match QMessageBox.question(
            app.win_main,
            "Jetzt bearbeiten?",
            f"""Es gibt {
            f'{len(incompleteable)} Aufgaben, die nicht in der gegebenen Zeit abgeschlossen werden können'
            if len(incompleteable) > 1 else
            'eine Aufgabe, die nach derzeitigem Stand nicht abschließbar ist'
            } - jetzt bearbeiten?""",
        ):
            case QMessageBox.StandardButton.Yes:
                for task in incompleteable:
                    win = task_editor.Editor(task)
                    win.show()


def _cycle_in_task_dependencies(tasks: list[Task]) -> list[Task]:
    """Return a list of tasks that are involved in a cycle in their dependencies."""
    visited = set()
    path = []

    def _visit(task: Task) -> bool:
        if task in visited:
            return False
        visited.add(task)
        path.append(task)
        for subtask in task.doable_supertasks:
            if subtask in path or _visit(subtask):
                return True
        path.pop()
        return False

    return [task for task in tasks if _visit(task)]
