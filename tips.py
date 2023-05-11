from enum import Enum
from typing import NamedTuple

import use


class Tip(NamedTuple):
    en: str
    de: str
    img_url: str


# Version of the tips
version = use.Version(major=1, minor=0, patch=0)


class tips(Enum):
    main1 = Tip(
        en="The buttons are not arranged into a grid by chance! Use the NumPad Keys to activate them!",
        de="Die Knöpfe sind nicht zufällig in einem Raster angeordnet! Benutze die NumPad Tasten um sie zu aktivieren!",
        img_url=None,
    )
    list1 = Tip(
        en="You can change the columns by rightlicking on the header",
        de="Du kannst die Spalten durch Rechtsklick auf den Header ändern",
        img_url=None,
    )

    @property
    def en(self) -> str:
        return self.value.en

    @property
    def de(self) -> str:
        return self.value.de or self.value.en

    @property
    def img_url(self) -> str:
        return self.value.img_url
