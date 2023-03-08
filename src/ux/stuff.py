from config import Config
from PyQt6.QtSql import QSqlDatabase
from .app import Application

# assigned from main.py by use()

app: Application
db: QSqlDatabase
config: Config
__version__: tuple[int, int, int]