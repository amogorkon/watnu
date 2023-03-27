import sqlite3

from PyQt6.QtSql import QSqlDatabase

from configuration import Config

from app import Application

# assigned from main.py by use()

app: Application
config: Config
db: sqlite3.Connection
__version__: tuple[int, int, int]
