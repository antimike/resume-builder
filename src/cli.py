import argparse
import sys

from . import DEFAULT_CONFIG, TEMPLATE, get_logger
from .utils import build_resume, find_resumes

logger = get_logger(__name__)


def get_cli_opts(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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
    add.add_argument(
        "name",
        help="name of resume to add",
        nargs="+",
    )
    edit.add_argument("name", help="name of resume to edit")
    build.add_argument(
        "name",
        help="name of resume to build (if not provided, the current directory will be built)",
        nargs="*",
    )
    return parser.parse_args(args)


def run_cli(args: list[str]):
    opts = get_cli_opts(args)
    status = 0
    logger.debug(opts)
    if opts.command == "add":
        for name in opts.name:
            logger.info("Creating subdirectory and config file for resume %r", name)
            try:
                dest = TEMPLATE.parent.joinpath(name)
                dest.mkdir(exist_ok=False)
                dest.joinpath("resume.yaml").write_text(DEFAULT_CONFIG.read_text())
            except FileExistsError:
                logger.error("Target %r already exists!", name)
    elif opts.command == "build":
        for name in opts.name:
            logger.info("Building resume %r", name)
            try:
                resumes = find_resumes(name)
                if not resumes:
                    raise FileNotFoundError(name)
                if len(resumes) > 1:
                    logger.warning("Resume name %r is ambiguous", name)
                    status += 1
                else:
                    build_resume(resumes.pop())
            except FileNotFoundError:
                logger.error("Could not find resume %r", name)
                status += 1
            except Exception:
                raise
    elif opts.command == "edit":
        raise NotImplementedError()

    sys.exit(status)
