from dataclasses import asdict
from functools import reduce
from typing import ClassVar, Mapping

import yaml

from .models import ResumeConfig
from .tags import add_list_tag


class ResumeListProcessor:
    ARGS_KV: ClassVar[list[tuple[str]]]
    ARGS_SCALAR: ClassVar[tuple[str]]
    BATCH_SIZE: ClassVar[int] = 1
    LATEX_MACRO: ClassVar[str]

    @classmethod
    def process_sequence(cls, loader: yaml.Loader, node: yaml.SequenceNode):
        items = loader.construct_sequence(node, deep=True)
        inst = cls(items)
        return inst.get_lines()

    def __init__(self, items):
        self._items = items
        self._subitems = []
        self._lines = []
        self._batch = []

    def get_lines(self):
        while self._items:
            self._process_item(self._items.pop(0))
        while self._batch and len(self._batch) < self.BATCH_SIZE:
            self._process_item(None)
        self._flush_batch()
        return self._lines

    def _stringify(self, val):
        if val is None:
            return ""
        elif isinstance(val, list):
            return ", ".join([str(elem) for elem in val])
        else:
            return str(val)

    def _format_arg(self, arg, val):
        if arg is None:
            return ""
        elif isinstance(val, Mapping):
            return arg % {k: self._stringify(v) for k, v in val.items()}
        else:
            return arg % self._stringify(val)

    def _push_onto_batch(self, args):
        if len(self._batch) >= self.BATCH_SIZE:
            self._flush_batch()
        self._batch.append(args)

    def _flush_batch(self):
        if self._batch:
            self._lines.append(
                reduce(
                    lambda ret, tup: ret + "".join(["{%s}" % arg for arg in tup]),
                    self._batch,
                    r"\%s" % self.LATEX_MACRO,
                )
            )
            self._lines.extend(self._subitems)
            self._batch.clear()
            self._subitems.clear()

    def _get_subitems(self, item):
        if isinstance(item, ResumeConfig):
            return getattr(item, "items", [])
        elif isinstance(item, dict):
            return item.get("items", [])
        elif hasattr(item, "items"):
            return item.items
        else:
            return []

    def _format_kv(self, mapping):
        for arg_tuple in self.ARGS_KV:
            try:
                args = tuple(self._format_arg(arg, mapping) for arg in arg_tuple)
                self._push_onto_batch(args)
                break
            except KeyError:
                continue
        self._subitems.extend(self._get_subitems(mapping))

    def _process_item(self, item):
        if isinstance(item, Mapping):
            self._format_kv(item)
        elif isinstance(item, ResumeConfig):
            self._process_item(asdict(item))
        elif item is None:
            self._push_onto_batch(tuple("" for _ in self.ARGS_SCALAR))
        else:
            self._push_onto_batch(
                tuple(
                    self._format_arg(arg, self._stringify(item))
                    for arg in self.ARGS_SCALAR
                )
            )


class ResumeListItemProcessor(ResumeListProcessor):
    ARGS_KV: ClassVar[list[tuple[str]]] = [
        ("%(title)s: %(description)s",),
        ("%(title)s",),
    ]
    ARGS_SCALAR: ClassVar[tuple[str]] = ("%s",)
    LATEX_MACRO: ClassVar[str] = "cvlistitem"
    BATCH_SIZE: ClassVar[int] = 1


add_list_tag("single", ResumeListItemProcessor.process_sequence)


class ResumeDoubleListItemProcessor(ResumeListProcessor):
    ARGS_KV: ClassVar[list[tuple[str]]] = [
        ("%(title)s: %(description)s",),
        ("%(title)s",),
    ]
    ARGS_SCALAR: ClassVar[tuple[str]] = ("%s",)
    LATEX_MACRO: ClassVar[str] = "cvlistdoubleitem"
    BATCH_SIZE: ClassVar[int] = 2


add_list_tag("double", ResumeDoubleListItemProcessor.process_sequence)


class ResumeComputerListItemProcessor(ResumeListProcessor):
    ARGS_KV: ClassVar[list[tuple[str]]] = [("%(title)s", "%(description)s")]
    ARGS_SCALAR: ClassVar[tuple[str]] = (None, "%s")
    LATEX_MACRO: ClassVar[str] = "cvcomputer"
    BATCH_SIZE: ClassVar[int] = 2


add_list_tag("computer", ResumeComputerListItemProcessor.process_sequence)


class ResumeLineListItemProcessor(ResumeListProcessor):
    ARGS_KV: ClassVar[list[tuple[str]]] = [
        ("%(title)s", "%(description)s"),
        ("%(title)s", None),
    ]
    ARGS_SCALAR: ClassVar[tuple[str]] = ("%s", None)
    LATEX_MACRO: ClassVar[str] = "cvline"
    BATCH_SIZE: ClassVar[int] = 1


add_list_tag("line", ResumeLineListItemProcessor.process_sequence)
