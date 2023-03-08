from pytest import fixture, mark, raises, skip
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel

import use


first_start = use(use.Path("../src/first_start.py"))
config = use(use.Path("../src/config.py")).Config()


def test_config():
   assert config