from ast import literal_eval
from pathlib import Path
from typing import Callable

import use

attrs = use(
    "attrs",
    version="22.2.0",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "K䍨瞃尰抧衤臤㘧鋚醘㸕㫧摄䇖Ƙ䥤買賔",  # py3-any
    },
    import_as="attrs",
)
import attrs

stay = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/stay/master/src/stay/stay.py"),
    hash_algo=use.Hash.sha256,
    hash_value="47e11e8de6b07f24c95233fba1e7281c385b049f771f74c5647a837b51bd7ff4",
    import_as="stay",
)

from typing import Any, cast

load = cast(Callable[[], dict[Any, Any]], stay.Decoder())
dump = cast(Callable[[], None], stay.Encoder())


class ConfigurationError(Exception):
    pass


def write(config):
    Path("config.stay").write_text(dump(attrs.asdict(config)))


class boolean:
    def __init__(self, x):
        if isinstance(x, str):
            try:
                self.x = bool(literal_eval(x))
            except ValueError as e:
                raise ConfigurationError(f"{x} is not a Value of True or False!") from e
        if isinstance(x, bool):
            self.x = x

    def __str__(self):
        return str(self.x)

    def __repr__(self):
        return repr(self.x)

    def __bool__(self):
        return self.x


# use.apply_aspect(attrs, use.woody_logger)  # BUG


def print_attr(self, attribute, value):
    print(f"config: setting {attribute.name} to {value!r}")
    return value


@attrs.define(
    auto_attribs=True,
    on_setattr=[attrs.setters.convert, print_attr],
    field_transformer=lambda cls, fields: [field.evolve(converter=field.type) for field in fields],
)
class Config:
    # bool("False") is a non-empty string -> True :|
    config_path: Path = Path("config.stay")
    first_start: boolean = True
    db_path: str = "watnu.sqlite"
    mantras: Path = "mantras.stay"
    coin: int = 0b1
    lucky_num: int = 1
    count: int = 1
    telegram_user: int = 0
    telegram_token: str = None
    tictoc_volume: int = 50
    activity_color_body: str = "darkred"
    activity_color_mind: str = "darkblue"
    activity_color_soul: str = "indigo"
    generated_faces_token: str = None
    tutorial_active: boolean = True
    run_sql_stuff: boolean = False
    icon: str = "./extra/feathericons/watnu1.png"
    debugging: boolean = False
    autostart: boolean = False
    call_name: str = ""
    last_selected_space: str = ""
    last_edited_space: str = ""
    base_path: Path = Path(__file__).parent
    read_totds: list[str] = []

    def save(self):
        print("saving config")
        self.config_path.write_text(dump(attrs.asdict(self)))


def read(file) -> Config:
    D = {}
    with open(file) as f:
        D = {}
        for D in load(f):
            pass
    return Config(**D)
