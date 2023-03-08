
import os
import sys

here = os.path.split(os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here[0], "src/watnu")
sys.path.append(src)

from unittest.mock import Mock

import classes
import first_start
import hypothesis as hypo
import main
import PyQt5 as qt
import pytest as pyt
from classes import set_globals

classes.config = Mock()
classes.config.debugging = False
main.state = Mock()


@pyt.fixture
def db():
    conn = qt.QtSql.QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    first_start.run(conn, classes.config)
    return conn
    
@pyt.fixture
def app():
    return main.Application([])

def test_db(db):
    assert len(db.tables()) == 15

def test_new_task(db, app):
    main.last_edited_space = 0
    edit = main.Editor(app)
    #edit.desc.setText("test")

def test_breaking():
    assert False

def test_breaking2():
    assert False
