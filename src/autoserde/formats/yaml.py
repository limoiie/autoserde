from typing import Any

from autoserde.formats.base import SerdeFormat


class YamlFormat(SerdeFormat, exts=['.yaml', '.yml']):
    def dump(self, obj: Any, fp, **kwargs):
        yaml = __import__('yaml')
        with fp.open('wt+') as f:
            yaml.dump(obj, f, **kwargs)

            if fp.fp is None:
                return fp.read_all()

    def load(self, fp, **kwargs):
        yaml = __import__('yaml')
        with fp.open('rt') as f:
            return yaml.load(f, yaml.Loader, **kwargs)
