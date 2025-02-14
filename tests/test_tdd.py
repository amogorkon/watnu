import sqlite3
import sys
from pathlib import Path
from beartype import beartype
from pytest import fixture

# fucking hate this, but it's the only way to make tests work properly with python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# set up a test DB connection, in memory as fixture
@fixture
@beartype
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE my_table (id INTEGER PRIMARY KEY, value TEXT)")
    yield conn
    conn.close()


# to get type hints in IDEs

print()  # prevent import reshuffling

# now the rest
# import src.classes as classes

# from src.first_start import setUp

# @mark.xfail(message="tdd")
# def test_db_creation(db):
#     # setUp(db)
#     # db.execute("INSERT INTO my_table (value) VALUES (?)", ("test_value",))
#     query = db.execute("SELECT * FROM tasks")
#     result = query.fetchone()


@beartype
def test_pass():
    pass
