from json import dumps, load
from pathlib import Path

import attrs


class ConfigurationError(Exception):
    pass


def write(config):
    Path("config.json").write_text(dumps(attrs.asdict(config), indent=4))


def print_attr(self, attribute, value):
    print(f"config: setting {attribute.name} to {value!r}")
    return value


@attrs.define(
    auto_attribs=True,
    on_setattr=[attrs.setters.convert, print_attr],
    field_transformer=lambda cls, fields: [field.evolve(converter=field.type) for field in fields],
)
class Config:
    config_path: Path = Path("config.json")
    first_start: bool = True
    db_path: str = "watnu.sqlite"
    coin: int = 0b1
    lucky_num: int = 1
    count: int = 1
    telegram_user: int = 0
    telegram_token: str | None = None
    tictoc_volume: int = 50
    activity_color_body: str = "darkred"
    activity_color_mind: str = "darkblue"
    activity_color_soul: str = "indigo"
    generated_faces_token: str | None = None
    tutorial_active: bool = True
    run_sql_stuff: bool = False
    icon: str = "./extra/feathericons/watnu1.png"
    debugging: bool = False
    autostart: bool = False
    call_name: str = ""
    last_selected_space: str = ""
    last_edited_space: str = ""
    base_path: Path = Path(__file__).parent
    read_totds: list[str] = []
    language: str = "en"
    show_totd: bool = True
    db_write_count: int = 0
    db_write_plaintext: bool = False
    db_cipher_path: Path = Path("watnu.cipher")

    def save(self):
        self.config_path.write_text(dumps(attrs.asdict(self), indent=4, default=str))


def read(file) -> Config:
    try:
        with open(file, "r") as f:
            config_dict = load(f)
    except FileNotFoundError:
        return Config()  # Return default config if file not found

    default_config = Config()
    return attrs.evolve(default_config, **config_dict)
