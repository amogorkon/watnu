from datetime import datetime


class Date:
    def __init__(
        self,
        year: int = 0,
        month: int = 0,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def from_datetime(self, dt):
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hour = dt.hour
        self.minute = dt.minute
        self.second = dt.second
        return self

    def __call__(self):
        return datetime(
            self.year, self.month, self.day, self.hour, self.minute, self.second
        )

    def __repr__(self):
        return f"Date({self.year}, {self.month}, {self.day}, {self.hour}, {self.minute}, {self.second})"

    def __eq__(self, other):
        return self() == other()


class Modifier:
    def __init__(self, kind: str, amount: int = 1):
        self.amount = amount

    def __mul__(self, other):
        if isinstance(other, Date):
            pass

    def __repr__(self):
        return "Modifier"


class Day(Modifier):
    kind = "day"


class Month(Modifier):
    kind = "month"


class Year(Modifier):
    kind = "year"


class Week(Modifier):
    kind = "week"
