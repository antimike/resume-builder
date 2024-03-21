from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import ClassVar

import yaml


@dataclass(kw_only=True)
class ResumeConfig(yaml.YAMLObject):
    yaml_tag: ClassVar[str] = "!resume-config"

    items: list[dict | ResumeConfig] = field(default_factory=list)

    def format(self, fmt: str) -> str:
        return fmt % asdict(self)


@dataclass(kw_only=True)
class ResumeTheme(ResumeConfig):
    yaml_tag: ClassVar[str] = "!theme"

    color: str
    style: str
    font_size: int = 10


@dataclass(kw_only=True)
class Address(ResumeConfig):
    yaml_tag: ClassVar[str] = "!address"

    street: str
    city: str
    state: str
    zip: str


@dataclass(kw_only=True)
class PersonalData(ResumeConfig):
    yaml_tag: ClassVar[str] = "!personal-data"

    first_name: str
    last_name: str
    desired_title: str
    address: Address
    mobile: str
    email: str


@dataclass(kw_only=True)
class Position(ResumeConfig):
    yaml_tag: ClassVar[str] = "!position"

    start: str
    end: str
    title: str
    company: str
    location: str
    description: str
    items: list[str] = field(default_factory=list)
