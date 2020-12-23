from typing import NamedTuple

from lib.stay import Decoder
from lib.stay import Encoder

import logging

load = Decoder()
dump = Encoder()


def read(file):
    with open(file) as f:
        for D in load(f):
            pass
        return Config(**D)


class Config:
    def __init__(self, first_start: bool = True,
                database: str = "watnu.sqlite",
                coin: int = 0b1,
                lucky_num: int = 1,
                count: int = 1
                 ):

        self.first_start = bool(first_start)
        self.database = str(database)
        self.coin = int(coin)
        self.lucky_num = int(lucky_num)
        self.count = int(count)

    def write(self):
        with open("config.stay", "w") as f:
            try:
                f.write(dump(self))
            except:
                logging.critical("COULD NOT WRITE CONFIG!")
