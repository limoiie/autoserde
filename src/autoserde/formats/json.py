import json
from typing import Any

from autoserde.formats.base import SerdeFormat


class JsonFormat(SerdeFormat, exts=['.json']):
    def dump(self, obj: Any, fp, **kwargs):
        return json.dump(obj, fp, **kwargs)

    def load(self, fp, **kwargs):
        return json.load(fp, **kwargs)
