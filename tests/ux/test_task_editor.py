import pytest
from beartype import beartype
from PyQt6.QtGui import QShortcut
from PyQt6.QtWidgets import QApplication, QWizard

from src.classes import Task
from src.ux.task_editor import Editor


@pytest.fixture
@beartype
def app():
    return QApplication([])


@pytest.fixture
@beartype
def task():
    return Task(id=1, do="Test Task", notes="Test Notes")


@beartype
def test_initialize_attributes(task):
    editor = Editor(task=task)
    assert editor.task == task
    assert editor.cloning is False
    assert editor.templating is False
    assert editor.as_sup == 0
    assert editor.current_space is None
    assert editor.draft is False
    assert editor.deadline == float("inf")
    assert editor.repeats is None
    assert (editor.constraints == 0).all()
    assert editor.subtasks == []
    assert editor.supertasks == []
    assert editor.skill_ids == []


@beartype
def test_setup_ui_elements(app, task):
    editor = Editor(task=task)
    assert editor.statusBar is not None
    assert editor.do.font() == app.fira_font
    assert editor.notes.font() == app.fira_font
    assert editor.button(QWizard.WizardButton.HelpButton).text() == "Help"
    assert editor.button(QWizard.WizardButton.CustomButton2).text() == "löschen"


@beartype
def test_setup_shortcuts(app, task):
    editor = Editor(task=task)
    assert editor.findChild(QShortcut, "F11") is not None
    assert editor.findChild(QShortcut, "Ctrl+Return") is not None


@beartype
def test_setup_signals(app, task):
    editor = Editor(task=task)
    assert editor.priority.valueChanged is not None
    assert editor.button(QWizard.WizardButton.CustomButton1).clicked is not None
    assert editor.button1.clicked is not None
    assert editor.button2.clicked is not None
    assert editor.button3.clicked is not None
    assert editor.organize_subtasks.clicked is not None
    assert editor.organize_supertasks.clicked is not None
    assert editor.choose_constraints_button.clicked is not None
    assert editor.choose_deadline_button.clicked is not None
    assert editor.button4.clicked is not None
    assert editor.button5.clicked is not None
    assert editor.button6.clicked is not None
    assert editor.button7.clicked is not None
    assert editor.button8.clicked is not None
    assert editor.space.currentIndexChanged is not None


@beartype
def test_initialize_task(app, task):
    editor = Editor(task=task)
    assert editor.task == task
    assert editor.do.toPlainText() == task.do
    assert editor.notes.toPlainText() == task.notes


@beartype
def test_setup_gui_timer(app, task):
    editor = Editor(task=task)
    assert editor.gui_timer is not None
    assert editor.gui_timer.interval() == 100


@beartype
def test_setup_menus(app, task):
    editor = Editor(task=task)
    assert editor.button9a.menu() is not None
    assert editor.button1.menu() is not None
