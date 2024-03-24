import logging
from pathlib import Path

import jinja2
from rich.logging import RichHandler

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES = PROJECT_ROOT.joinpath("templates")
DATA = PROJECT_ROOT.joinpath("data")
APPLICATIONS = PROJECT_ROOT.joinpath("applications")

template_loader = jinja2.loaders.ChoiceLoader(
    [jinja2.loaders.FileSystemLoader(d) for d in (".", TEMPLATES)]
)
config_loader = jinja2.loaders.ChoiceLoader(
    [jinja2.loaders.FileSystemLoader(d) for d in (".", DATA)]
)

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


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = RichHandler()
    logger.addHandler(handler)
    return logger


def set_log_level(level: str | int):
    logging.getLogger().setLevel(level)


def set_verbosity(level: int):
    levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
    if level < 0:
        set_log_level(logging.CRITICAL + 1)
    elif level >= len(levels):
        set_log_level(logging.DEBUG - 1)
    else:
        set_log_level(levels[level])
