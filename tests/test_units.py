import use
from pytest import fixture, mark, raises, skip

use(
    use.URL("https://raw.githubusercontent.com/amogorkon/q/main/q.py"), modes=use.recklessness, import_as="q"
)  # otherwise imports from modules won't work

initial_globals = {"db": None, "app": None, "config": None}

use(use.Path("stuff.py"), initial_globals=initial_globals, import_as="stuff")

Task = use(use.Path("classes.py"), initial_globals=initial_globals).Task


def test_task():
    d = {}
    t = Task(*[0] * 19)
    assert t
