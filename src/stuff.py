import sqlite3
from src.configuration import Config
from src.app import Application

# assigned from main.py by use()

app: Application
config: Config
db: sqlite3.Connection
__version__: tuple[int, int, int]
