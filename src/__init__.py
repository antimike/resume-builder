import logging
from pathlib import Path

import jinja2
from rich.logging import RichHandler

DEFAULT_CONFIG = Path(__file__).parent.parent.joinpath("default_config.yaml")
TEMPLATE = Path(__file__).parent.parent.joinpath("resume.tex.j2")

JINJA_ENV = jinja2.Environment(
    block_start_string="<&",
    block_end_string="&>",
    variable_start_string="<@",
    variable_end_string="@>",
    comment_start_string="<#",
    comment_end_string="#>",
    trim_blocks=True,
    lstrip_blocks=True,
    loader=jinja2.FileSystemLoader(TEMPLATE.parent),
    extensions=["jinja2.ext.do"],
)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = RichHandler()
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
