from functools import reduce
from typing import Sequence

import yaml

from .utils import get_config

_resume_prefix = "!resume-"
_resume_tags = {}
_list_tags = {}


def add_resume_tag(tag_suffix, func):
    if not callable(func):
        raise ValueError("Resume tag processor must be callable")
    _resume_tags[tag_suffix] = func


def add_list_tag(tag_suffix, func):
    if not callable(func):
        raise ValueError("List tag processor must be callable")
    _list_tags[tag_suffix] = func


def add_style_tag(tag, template, Loader=yaml.SafeLoader):
    Loader.add_constructor(
        f"!{tag.removeprefix('!')}",
        lambda loader, node: template % loader.construct_scalar(node),
    )


def _process_resume_tag(loader, tag_suffix, node):
    return _resume_tags[tag_suffix](loader, node)


def _process_list_tag(loader, tag_suffix, node):
    return _list_tags[tag_suffix](loader, node)


def _process_latex(loader, tag_suffix, node):
    args = loader.construct_sequence(node)
    return "".join([r"\%s" % tag_suffix, *[r"{%s}" % arg for arg in args]])


for tag in ("bf", "textbf", "bold"):
    add_style_tag(tag, r"\textbf{%s}")

for tag in ("it", "italic", "italics", "emph"):
    add_style_tag(tag, r"\emph{%s}")


def include(loader: yaml.Loader, node: yaml.Node):
    name = loader.construct_scalar(node)
    content, _, _ = get_config(name)
    return yaml.load(content, loader.__class__)


def add_resume_tags():
    from .listitems import add_list_tags

    yaml.SafeLoader.add_multi_constructor(_resume_prefix, _process_resume_tag)
    yaml.SafeLoader.add_multi_constructor("!tex-", _process_latex)
    yaml.SafeLoader.add_multi_constructor("!items-", _process_list_tag)
    yaml.SafeLoader.add_constructor("!include", include)

    add_list_tags()
