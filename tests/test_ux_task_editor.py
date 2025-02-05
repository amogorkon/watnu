import pytest
from PyQt6.QtWidgets import QApplication

import src
from src.classes import Task
from src.ux.task_editor import Editor


@pytest.fixture
def app(qtbot):
    """Fixture to create a QApplication instance."""
    return QApplication([])


@pytest.fixture
def task():
    """Fixture to create a mock Task instance."""
    return Task(id=1, do="Test Task", notes="Test Notes", priority=5)


def test_editor_initialization(app, qtbot, task):
    """Test the initialization of the Editor."""
    editor = Editor(task=task)
    qtbot.addWidget(editor)

    assert editor.task == task
    assert editor.priority.value() == task.priority
    assert editor.do.toPlainText() == task.do
    assert editor.notes.toPlainText() == task.notes


def test_editor_save_task_details(app, qtbot, task, mocker):
    """Test saving task details."""
    editor = Editor(task=task)
    qtbot.addWidget(editor)

    mocker.patch("src.ux.task_editor.db.execute")
    mocker.patch("src.ux.task_editor.db.commit")

    editor.do.setPlainText("Updated Task")
    editor.notes.setPlainText("Updated Notes")
    editor.priority.setValue(10)

    editor._save_task_details()

    # Check if the database update was called with the correct parameters
    src.ux.task_editor.db.execute.assert_called_once()
    src.ux.task_editor.db.commit.assert_called_once()


def test_editor_delete_task(app, qtbot, task, mocker):
    """Test deleting a task."""
    editor = Editor(task=task)
    qtbot.addWidget(editor)

    mocker.patch.object(task, "delete")
    mocker.patch.object(editor, "reject")

    editor.delete_task()

    task.delete.assert_called_once()
    editor.reject.assert_called_once()
