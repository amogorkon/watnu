import main, classes
from unittest.mock import Mock

app = main.Application([])
main.state = Mock()
classes.config = Mock
classes.config.debugging = False
main.Editor(parent=app)