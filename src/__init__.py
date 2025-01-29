import sqlite3
import sys
from pathlib import Path
from time import time

import src.configuration as configuration
from src.app import Application
from src.configuration import Config

app: Application = Application(sys.argv)

path = Path(__file__).resolve().parent
# touch, just in case user killed the config or first start

config_path = path / "config.json"
config_path.touch()
config: Config = configuration.read(config_path)
config.config_path = config_path
print("using config:", config_path)
config.base_path = path


class DB(sqlite3.Connection):
    def commit(self):
        super().commit()
        app.db_last_modified = time()

    def is_connected(self):
        try:
            self.cursor()
            return True
        except Exception:
            return False


db = sqlite3.connect(config.db_path, factory=DB)


def initialize_globals(db_, app_, config_):
    global db, app, config
    db = db_
    app = app_
    config = config_
