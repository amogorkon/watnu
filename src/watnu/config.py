import attr

from ast import literal_eval

from lib.stay import Decoder
from lib.stay import Encoder

import logging

print("attrs:", attr.__version__)

load = Decoder()
dump = Encoder()


def read(file):
    with open(file) as f:
        for D in load(f):
            pass
        return Config(**D)


@attr.s(auto_attribs=True, 
        on_setattr=attr.setters.convert, 
        field_transformer=lambda cls, fields: [field.evolve(converter=field.type) for field in fields])
class Config:
    # "False" is a non-empty string -> True :|
    first_start: literal_eval = True
    database: str = "watnu.sqlite"
    coin: int = 0b1
    lucky_num: int = 1
    count: int = 1
    time_program_quit_last: int = 0

    def write(self):
        with open("config.stay", "w") as f:
            try:
                f.write(dump(attr.asdict(self)))
            except Exception as e:
                logging.critical("COULD NOT WRITE CONFIG!")
                logging.critical(e)
