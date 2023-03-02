import json
from typing import Any

from autoserde.formats.base import FlexWrap, SerdeFormat


class JsonFormat(SerdeFormat, exts=['.json']):
    def dump(self, obj: Any, fp: FlexWrap, **kwargs):
        with fp.open('wt+') as f:
            return json.dump(obj, f, **kwargs)

    def load(self, fp: FlexWrap, **kwargs):
        with fp.open('rt') as f:
            return json.load(f, **kwargs)
