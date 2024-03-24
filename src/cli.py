import argparse
import os
import sys
from pathlib import Path
from shutil import copyfile

import yaml

from . import (APPLICATIONS, PROJECT_ROOT, get_logger, set_log_level,
               set_verbosity)
from .tags import add_resume_tags
from .utils import (build_pdflatex, display_pdf, edit_file, find_resumes,
                    get_config, get_template, render_to_file)

logger = get_logger(__name__)

RESUME_BASE = Path("resume")


class AmbiguousSearchError(Exception):
    pass


def get_cli_opts(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        help="print debug output",
        action="store_true",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="increase verbosity",
        action="count",
        default=0,
    )
    commands = parser.add_subparsers(title="commands", required=True, dest="command")
    add = commands.add_parser(
        "add",
        help="add subdirectories and config files for new resumes",
    )
    edit = commands.add_parser(
        "edit",
        help="edit and rebuild resume (uses $EDITOR)",
    )
    build = commands.add_parser(
        "build",
        help="build resumes from the config files",
    )
    view = commands.add_parser("view", help="view resume PDF")
    add.add_argument(
        "name",
        help="name of resume to add",
        nargs="+",
    )
    add.add_argument(
        "--from",
        "-f",
        help="source to copy config and template files from",
    )
    edit.add_argument(
        "--config",
        "-c",
        help="edit a configuration file",
        action="append",
        default=[],
    )
    edit.add_argument(
        "--template",
        "-t",
        help="edit a template file",
        action="append",
        default=[],
    )
    edit.add_argument("name", help="resume or application identifier", action="append")
    build.add_argument(
        "name",
        help="name of resume to build (if not provided, the current directory will be built)",
        nargs="*",
    )
    view.add_argument("name", help="resume or application identifier", action="append")

    return parser.parse_args(args)


def _cd_to_application_dir(dest):
    logger.debug("Changing working dir to %r", dest)
    if not dest.exists():
        logger.info("Creating application directory %s", dest)
        dest.mkdir()
    os.chdir(dest)


def _create_texfile(
    dest=RESUME_BASE.with_suffix(".tex"), template_name="resume", config_name="resume"
):
    template = get_template(template_name)
    config_yaml, _, _ = get_config(config_name)
    logger.debug("Using template %s", template)
    config = yaml.load(config_yaml, yaml.SafeLoader)
    logger.debug("Using resume config %s", config)
    dest = Path(dest)
    if dest.exists():
        logger.info(
            "Updating source file %s", dest.absolute().relative_to(PROJECT_ROOT)
        )
    else:
        logger.info(
            "Creating source file %s", dest.absolute().relative_to(PROJECT_ROOT)
        )
    render_to_file(template, dest.name, exists_ok=True, config=config)


def _locate_working_dir(search_term, fuzzy=True):
    if fuzzy:
        resumes = find_resumes(search_term)
        if not resumes:
            raise FileNotFoundError(search_term)
        if len(resumes) > 1:
            raise AmbiguousSearchError(search_term)
        return resumes.pop()
    else:
        return APPLICATIONS.joinpath(search_term)


def _localize_file(path: Path | str) -> Path:
    path = Path(path).absolute()
    pwd = Path.cwd()
    logger.debug("Localizing path %s to working dir %s", path, pwd)
    if pwd not in path.parents:
        logger.info("Localizing file %s to working dir", path)
        copyfile(path, pwd.joinpath(path.name))
        path = pwd.joinpath(path.name)
    return path


def run_cli(args: list[str]):
    add_resume_tags()

    opts = get_cli_opts(args)

    set_verbosity(opts.verbose)
    if opts.debug:
        set_log_level("DEBUG")

    status = 0
    logger.debug(opts)
    for name in opts.name:
        try:
            path = _locate_working_dir(name, fuzzy=(not opts.command == "add"))
            logger.debug("Working dir: %s", path)
            _cd_to_application_dir(path)
            if opts.command == "add" and getattr(opts, "from", None) is not None:
                raise NotImplementedError()
            if opts.command == "edit":
                doc_paths = []
                for config in opts.config:
                    _, doc_path, _ = get_config(config)
                    doc_paths.append(_localize_file(doc_path))
                for template in opts.template:
                    doc_path = get_template(template).filename
                    doc_paths.append(_localize_file(doc_path))
                logger.debug(doc_paths)
                for doc_path in doc_paths:
                    edit_file(doc_path)
            elif opts.command == "build":
                _create_texfile(RESUME_BASE.with_suffix(".tex"))
                logger.info("Building resume %r...", name)
                result = build_pdflatex(RESUME_BASE.with_suffix(".tex"))
                if result.returncode == 0:
                    logger.info("Build successful")
                else:
                    logger.error("Build failed with error code %s", result.returncode)
                    logger.debug(result.stdout.decode())
                    status += result.returncode
            elif opts.command == "view":
                pdf = RESUME_BASE.with_suffix(".pdf")
                logger.info(
                    "Displaying resume PDF: %s",
                    pdf.absolute().relative_to(PROJECT_ROOT),
                )
                display_pdf(pdf)

        except AmbiguousSearchError:
            logger.warning("Resume search_term %r is ambiguous", name)
            status += 1
        except FileNotFoundError:
            logger.error("Could not find resume %r", name)
            status += 8
        except Exception:
            logger.exception("Unknown exception", exc_info=True)
            status += 64

    sys.exit(status)
