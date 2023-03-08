import use

app = "adsfadsf"
db = 23
config = (1,2,3)

initial_globals = {"app": app, "db": db, "config":config}


use(use.Path("ux/__init__.py"), initial_globals=initial_globals)

from ux import test