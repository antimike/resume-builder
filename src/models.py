from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import ClassVar

import yaml


def resume_model(cls):
    decorated = dataclass(kw_only=True)(cls)

    def constructor(loader: yaml.Loader, node: yaml.Node):
        content = loader.construct_mapping(node)
        return decorated(**content)

    yaml.SafeLoader.add_constructor(cls.yaml_tag, constructor)
    return decorated


@resume_model
class ResumeConfig:
    yaml_tag: ClassVar[str] = "!resume-config"

    items: list[dict | ResumeConfig] = field(default_factory=list)

    def format(self, fmt: str, style="%") -> str:
        if style == "%":
            return fmt % asdict(self)
        elif style == "{}":
            return fmt.format(**asdict(self))
        else:
            raise ValueError(f"Unknown format {style!r}")

    def to_dict(self):
        return asdict(self)


@resume_model
class ResumeTheme(ResumeConfig):
    yaml_tag: ClassVar[str] = "!theme"

    color: str
    style: str
    font_size: int = 10


@resume_model
class Address(ResumeConfig):
    yaml_tag: ClassVar[str] = "!address"

    street: str
    city: str
    state: str
    zip: str


@resume_model
class PersonalData(ResumeConfig):
    yaml_tag: ClassVar[str] = "!personal-data"

    first_name: str
    last_name: str
    desired_title: str
    address: Address
    mobile: str
    email: str


@resume_model
class Position(ResumeConfig):
    yaml_tag: ClassVar[str] = "!position"

    start: str
    end: str
    title: str
    company: str
    location: str
    description: str = None
    items: list[str] = field(default_factory=list)
