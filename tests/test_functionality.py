import use
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from pytest import fixture, mark, raises, skip

first_start = use(use.Path("../src/first_start.py"))
config = use(use.Path("../src/config.py")).Config()


@fixture
def db():
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    first_start.run(conn, config)
    return conn


def test_breaking():
    assert True
