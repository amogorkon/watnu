from itertools import product

from PyQt6.QtGui import QIcon, QPixmap

from src import config

OK = QIcon(str(config.base_path / "extra/check.svg"))
NOK = QIcon(str(config.base_path / "extra/cross.svg"))

ARROW_DOWN = QIcon()
ARROW_DOWN.addPixmap(
    QPixmap("ui\\../extra/arrow-down.svg"),
    QIcon.Mode.Normal,
    QIcon.State.Off,
)
ARROW_UP = QIcon()
ARROW_UP.addPixmap(
    QPixmap("ui\\../extra/arrow-up.svg"),
    QIcon.Mode.Normal,
    QIcon.State.Off,
)

status_icons = {
    C: QIcon(str(config.base_path / f"extra/status_icons/{''.join(str(int(x)) for x in C)}.svg"))
    for C in list(product([True, False], repeat=4))
}
