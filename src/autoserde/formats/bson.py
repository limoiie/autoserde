from typing import Any

from autoserde.formats.base import FlexWrap, SerdeFormat


class BsonFormat(SerdeFormat, exts=['.bson']):
    def dump(self, obj: Any, fp: FlexWrap, **kwargs):
        bson = __import__('bson')
        with fp.open('wb+') as f:
            ser = bson.dumps(obj, **kwargs)
            f.write(ser)

    def load(self, fp: FlexWrap, **kwargs):
        bson = __import__('bson')
        with fp.open('rb') as f:
            ser = f.read()
            return bson.loads(ser, **kwargs)
