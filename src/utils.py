import subprocess
from itertools import zip_longest

import yaml
from addict import Addict

from . import JINJA_ENV, TEMPLATE, get_logger

logger = get_logger(__name__)


def batch(collection, batch_size):
    yield from zip_longest(*(iter(collection),) * batch_size)


def find_resumes(search_str):
    return [
        p
        for p in TEMPLATE.parent.rglob("resume.yaml")
        if p.parent.name.lower().startswith(search_str.lower())
    ]


def build_resume(path):
    resume = path.parent.joinpath("resume.tex")
    logger.info(
        "Rendering %s from template %s and configuration %s",
        resume,
        TEMPLATE,
        path,
    )
    tmpl = JINJA_ENV.get_template(TEMPLATE.name)
    with path.open("r") as file:
        config = Addict(yaml.unsafe_load(file))
    resume.write_text(tmpl.render(config=config))
    logger.info("Compiling TeX file %s using %s", resume, "pdflatex")
    subprocess.run(
        ["pdflatex", str(resume)],
        cwd=path.parent,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
