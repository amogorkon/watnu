import logging

from ast import literal_eval

import attr

from lib.stay import Decoder
from lib.stay import Encoder

print("attrs:", attr.__version__)

load = Decoder()
dump = Encoder()


class ConfigurationError(Exception):
    pass


def read(file):
    D = {}
    with open(file) as f:
        for D in load(f):
            pass
        return Config(**D)


class boolean:
    def __init__(self, x):
        if isinstance(x, str):
            try:
                self.x = bool(literal_eval(x))
            except ValueError:
                raise ConfigurationError(f"{x} is not a Value of True or False!")
        if isinstance(x, bool):
            self.x = x

    def __str__(self):
        return str(self.x)

    def __repr__(self):
        return repr(self.x)

    def __bool__(self):
        return self.x


@attr.s(
    auto_attribs=True,
    on_setattr=attr.setters.convert,
    field_transformer=lambda cls, fields: [
        field.evolve(converter=field.type) for field in fields
    ],
)
class Config:
    # "False" is a non-empty string -> True :|
    first_start: boolean = True  # TODO
    database: str = "watnu.sqlite"
    coin: int = 0b1
    lucky_num: int = 1
    count: int = 1
    telegram_user: int = 0
    telegram_token: str = None
    tictoc_volume: int = 50
    activity_color_body: str = "darkred"
    activity_color_mind: str = "darkblue"
    activity_color_spirit: str = "indigo"
    generated_faces_token: str = None
    tutorial_active: boolean = True
    run_sql_stuff: boolean = False
    icon: str = "./extra/feathericons/watnu1.png"

    def write(self):
        with open("config.stay", "w") as f:
            try:
                f.write(dump(attr.asdict(self)))
            except Exception as e:
                logging.critical("COULD NOT WRITE CONFIG!")
                logging.critical(e)
