import logging
from pathlib import Path

import jinja2
from rich.logging import RichHandler

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES = PROJECT_ROOT.joinpath("templates")
DATA = PROJECT_ROOT.joinpath("data")
APPLICATIONS = PROJECT_ROOT.joinpath("applications")
DEFAULT_CONFIG = DATA.joinpath("default_config.yaml")

template_loader = jinja2.loaders.ChoiceLoader(
    [jinja2.loaders.FileSystemLoader(TEMPLATES)]
)
config_loader = jinja2.loaders.ChoiceLoader([jinja2.loaders.FileSystemLoader(DATA)])

JINJA_ENV = jinja2.Environment(
    block_start_string="<&",
    block_end_string="&>",
    variable_start_string="<@",
    variable_end_string="@>",
    comment_start_string="<#",
    comment_end_string="#>",
    trim_blocks=True,
    lstrip_blocks=True,
    loader=template_loader,
    extensions=["jinja2.ext.do"],
)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = RichHandler()
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
