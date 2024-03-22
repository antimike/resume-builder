import subprocess
from itertools import zip_longest

import yaml

from . import APPLICATIONS, JINJA_ENV, get_logger
from .loaders import ResumeLoader

logger = get_logger(__name__)


def batch(collection, batch_size):
    yield from zip_longest(*(iter(collection),) * batch_size)


def format_as(obj, template_name: str):
    template_name = template_name.removesuffix(".j2").removesuffix(".tex")
    template = JINJA_ENV.get_template(f"{template_name}.tex.j2")
    return template.render(data=obj)


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
