from typing import Any

from autoserde.formats.base import SerdeFormat


class YamlFormat(SerdeFormat, exts=['.yaml', '.yml']):
    def dump(self, obj: Any, fp, **kwargs):
        yaml = __import__('yaml')
        return yaml.dump(obj, fp, **kwargs)

    def load(self, fp, **kwargs):
        yaml = __import__('yaml')
        return yaml.load(fp, yaml.Loader, **kwargs)
