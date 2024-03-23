import os
import subprocess
from itertools import zip_longest
from pathlib import Path
from typing import Iterable

import jinja2
import yaml
from jinja2 import TemplateError, TemplateNotFound

from . import APPLICATIONS, JINJA_ENV, config_loader, get_logger
from .loaders import ResumeLoader

logger = get_logger(__name__)

EXTENSIONS = {"DATA": ("yml", "yaml", "json"), "MARKUP": ("tex",)}
EDITOR = os.getenv("EDITOR", "vim")


def _load_first(loader: jinja2.loaders.BaseLoader, filenames: Iterable):
    for filename in filenames:
        try:
            return loader.get_source(JINJA_ENV, filename)
        except TemplateNotFound:
            continue


def _get_template_filenames(name: str, extensions: Iterable[str]) -> str:
    path = Path(name.removesuffix(".j2"))
    yield from map(lambda ext: str(path.with_suffix(f".{ext}")), extensions)


def get_config(name: str):
    config = _load_first(
        config_loader, _get_template_filenames(name, EXTENSIONS["DATA"])
    )
    if config is None:
        raise TemplateNotFound(name)
    return config


def get_template(name: str):
    return JINJA_ENV.select_template(
        list(_get_template_filenames(name, [f"{e}.j2" for e in EXTENSIONS["MARKUP"]]))
    )


def batch(collection, batch_size):
    yield from zip_longest(*(iter(collection),) * batch_size)


def render(template, **template_vars):
    def format_as(obj, template_name: str):
        return render(get_template(template_name), data=obj)

    return template.render(**template_vars, format_as=format_as)


def render_to_file(template, filename: str, exists_ok=False, **template_vars):
    dest = Path(filename)
    if dest.exists() and not exists_ok:
        logger.error("Rendering destination %s already exists", dest)
        return
    with dest.open("w") as outfile:
        outfile.write(render(template, **template_vars))


def find_resumes(search_str):
    resumes = [
        p
        for p in APPLICATIONS.iterdir()
        if p.name.lower().startswith(search_str.lower().strip())
    ]
    logger.debug("Search term %r yielded resume paths %s", search_str, resumes)
    return resumes


def edit_file(file):
    logger.info("Editing file %s")
    subprocess.run([EDITOR, "--", str(file)])


def display_pdf(file):
    viewer = "zathura"
    logger.info("Opening PDF %s with %s", file, viewer)
    subprocess.run([viewer, "--", file])


def build_pdflatex(filename):
    logger.info("Compiling LaTeX file %s using %s", filename, "pdflatex")
    return subprocess.run(
        ["pdflatex", "-halt-on-error", "--", filename],
        capture_output=True,
    )
