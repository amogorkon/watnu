# assigned from main.py via use()


import sqlite3

from src.app import Application
from src.configuration import Config

app: Application
config: Config
db: sqlite3.Connection
__version__: tuple[int, int, int]
