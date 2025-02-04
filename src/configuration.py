from __future__ import annotations

from json import JSONDecodeError, dumps, load
from pathlib import Path
from typing import get_args, get_origin, get_type_hints

import attrs


class ConfigurationError(Exception):
    pass


def write(config):
    Path("config.json").write_text(dumps(attrs.asdict(config), indent=4))


def print_attr(self, attribute, value):
    print(f"config: setting {attribute.name} to {value!r}")
    return value


def field_transformer(cls, fields):
    resolved_types = get_type_hints(cls)
    new_fields = []

    for field in fields:
        field_name = field.name
        field_type = resolved_types[field_name]
        origin = get_origin(field_type)
        args = get_args(field_type)

        match origin:
            case UnionType if type(None) in args:  # noqa: F841
                # Handle (Path | None)
                non_none_type = next(a for a in args if a is not type(None))

                def converter(x, t=non_none_type):
                    return t(x) if x is not None else None

            case _:
                # Direct type conversion for concrete types
                converter = field_type

        new_fields.append(field.evolve(converter=converter))
    return new_fields


@attrs.define(
    auto_attribs=True,
    on_setattr=[attrs.setters.convert, print_attr],
    field_transformer=field_transformer,
)
class Config:
    config_path: Path | None = None
    telegram_token: str | None = None
    generated_faces_token: str | None = None
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


def read(config_path: Path) -> Config:
    try:
        with config_path.open("r") as f:
            config_dict = load(f)
    except (FileNotFoundError, JSONDecodeError):
        config_dict = {}

    default_config = Config()
    x = attrs.evolve(default_config, **config_dict)
    assert isinstance(x.base_path, Path)
    return x
