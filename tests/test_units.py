from unittest.mock import Mock

import use

initial_globals = {"config": Mock(), "app": Mock(), "__version__": use.Version("1.2.3")}
use(use.Path("../src/stuff.py"), initial_globals=initial_globals, import_as="stuff")


def test_foo():
    pass
