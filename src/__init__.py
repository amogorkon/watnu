import sqlite3
import sys
from pathlib import Path
from time import time
from unittest.mock import Mock

import src.configuration as configuration
from src.app import Application
from src.configuration import Config

app: Application = Application(sys.argv)

home_path = Path.home() / "watnu"
home_path.mkdir(parents=True, exist_ok=True)

if not hasattr(sys, "args"):
    # if watnu.py wasn't the entrypoint, like with tests, sys.args isn't defined, so let's mock
    sys.args = Mock()
config_path = home_path / "config_experimental.json" if sys.args.experimental else home_path / "config.json"
config_path.touch(exist_ok=True)
config: Config = configuration.read(config_path)
config.config_path = config_path


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


def initialize_globals(db_: DB, app_: Application, config_: Config):
    global db, app, config
    db = db_
    app = app_
    config = config_
