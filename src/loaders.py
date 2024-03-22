from itertools import chain
from pathlib import Path

import yaml

from . import DEFAULT_CONFIG, get_logger

logger = get_logger(__name__)


class ResumeLoader(yaml.SafeLoader):
    def __init__(self, stream):
        self._search_paths = [DEFAULT_CONFIG.parent]
        try:
            self._search_paths.append(Path(stream.name).parent)
        except AttributeError:
            pass
        super().__init__(stream)

    def find_configs(self, name):
        name = name.removesuffix(".yaml").removesuffix(".yml")
        globs = [path.rglob(f"{name}.y?ml") for path in self._search_paths]
        yield from chain(*globs)
