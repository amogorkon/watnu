import pytest
from PyQt6.QtWidgets import QApplication

from src.classes import Task


@pytest.fixture
def app() -> QApplication:
    return QApplication([])


@pytest.fixture
def task() -> Task:
    return Task(id=1, do="Test Task", notes="Test Notes")
