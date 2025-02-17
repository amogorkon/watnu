import sqlite3

from PyQt6.QtWidgets import QApplication
from pytest import fixture

from src.classes import Task


@fixture
def app() -> QApplication:
    return QApplication([])


@fixture
def task() -> Task:
    return Task(id=1, do="Test Task", notes="Test Notes")


@fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE my_table (id INTEGER PRIMARY KEY, value TEXT)")
    yield conn
    conn.close()
