import subprocess
from itertools import zip_longest
from pathlib import Path
from typing import Iterable

import yaml
from jinja2 import TemplateError

from . import APPLICATIONS, JINJA_ENV, get_logger
from .loaders import ResumeLoader

logger = get_logger(__name__)

EXTENSIONS = {"DATA": ("yml", "yaml", "json"), "MARKUP": ("tex",)}


def get_template_filenames(name: str, extensions: Iterable[str]) -> str:
    path = Path(name.removesuffix(".j2"))
    yield from map(lambda ext: path.with_suffix(f".{ext}.j2"), extensions)


def batch(collection, batch_size):
    yield from zip_longest(*(iter(collection),) * batch_size)


def format_as(obj, template_name: str):
    for template in get_template_filenames(template_name, EXTENSIONS["MARKUP"]):
        try:
            return template.render(data=obj)
        except Exception:
            logger.exception(
                "Failed to format object %s using template %s",
                obj,
                template,
                exc_info=True,
            )
            continue
    raise TemplateError(
        "Could not format object %s with template %r", obj, template_name
    )


def find_resumes(search_str):
    return [
        p
        for p in APPLICATIONS.rglob("resume.yaml")
        if p.parent.name.lower().startswith(search_str.lower())
    ]


def build_resume(path):
    template = JINJA_ENV.get_template("resume.tex.j2")
    resume = path.parent.joinpath("resume.tex")
    logger.info(
        "Rendering %s from template %s and configuration %s",
        resume,
        template,
        path,
    )
    with path.open("r") as file:
        config = yaml.load(file, ResumeLoader)
    resume.write_text(template.render(config=config, format_as=format_as))
    logger.info("Compiling TeX file %s using %s", resume, "pdflatex")
    subprocess.run(
        ["pdflatex", str(resume)],
        cwd=path.parent,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
