from config import Config
from PyQt6.QtSql import QSqlDatabase
from .app import Application


app: Application
db: QSqlDatabase
config: Config
__version__: tuple[int, int, int]