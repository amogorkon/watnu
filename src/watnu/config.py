import logging
from ast import literal_eval

import attr

from lib.stay import Decoder, Encoder

print("attrs:", attr.__version__)

load = Decoder()
dump = Encoder()


def read(file):
    D = {}
    with open(file) as f:
        for D in load(f):
            pass
        return Config(**D)


class boolean:
    def __init__(self, x):
        self.x = x

    def __call__(self, x):
        if isinstance(x, str):
            return bool(literal_eval(x))
        if isinstance(x, bool):
            return x


@attr.s(
    auto_attribs=True,
    on_setattr=attr.setters.convert,
    field_transformer=lambda cls, fields: [
        field.evolve(converter=field.type) for field in fields
    ],
)
class Config:
    # "False" is a non-empty string -> True :|
    first_start: boolean = True
    database: str = "watnu.sqlite"
    coin: int = 0b1
    lucky_num: int = 1
    count: int = 1
    time_program_quit_last: int = 0
    telegram_user: int = None
    telegram_token: str = None
    tictoc_volume: int = 50
    activity_color_body: str = "darkred"
    activity_color_mind: str = "darkblue"
    activity_color_spirit: str = "indigo"
    generated_faces_token: str = None
    tutorial_active: boolean = True

    def write(self):
        with open("config.stay", "w") as f:
            try:
                f.write(dump(attr.asdict(self)))
            except Exception as e:
                logging.critical("COULD NOT WRITE CONFIG!")
                logging.critical(e)
