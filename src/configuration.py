from json import JSONDecodeError, dumps, load
from pathlib import Path
from typing import Optional, get_args, get_origin

import attrs


class ConfigurationError(Exception):
    pass


def write(config):
    Path("config.json").write_text(dumps(attrs.asdict(config), indent=4))


def print_attr(self, attribute, value):
    print(f"config: setting {attribute.name} to {value!r}")
    return value


def field_transformer(cls, fields):
    new_fields = []
    for field in fields:
        field_type = field.type
        origin = get_origin(field_type)
        args = get_args(field_type)

        match (origin, args):
            case (Union, _) if type(None) in args:  # noqa: F841
                # Handle Optional[T] (Union[T, None])
                non_none_type = next(a for a in args if a is not type(None))

                def converter(x, t=non_none_type):
                    return t(x) if x is not None else None

            case _:
                converter = field_type

        new_fields.append(field.evolve(converter=converter))
    return new_fields


@attrs.define(
    auto_attribs=True,
    on_setattr=[attrs.setters.convert, print_attr],
    field_transformer=field_transformer,
)
class Config:
    config_path: Optional[Path] = None
    telegram_token: str | None = None
    generated_faces_token: Optional[str] = None
    first_start: bool = True
    db_path: Path = Path("watnu.sqlite")
    coin: int = 0b1
    lucky_num: int = 1
    count: int = 1
    telegram_user: int = 0
    tictoc_volume: int = 50
    activity_color_body: str = "darkred"
    activity_color_mind: str = "darkblue"
    activity_color_soul: str = "indigo"
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
    except (FileNotFoundError, JSONDecodeError):
        config_dict = {}

    default_config = Config()
    return attrs.evolve(default_config, **config_dict)
