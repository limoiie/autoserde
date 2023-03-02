from typing import Any, Optional

from autoserde.formats.base import FlexWrap, SerdeFormat


class BsonFormat(SerdeFormat, exts=['.bson']):
    def dump(self, obj: Any, fp: FlexWrap, **kwargs):
        bson = __import__('bson')

        ser = bson.dumps(obj, **kwargs)
        if fp.fp is None:
            return ser

        with fp.open('wb+') as f:
            f.write(ser)

    def load(self, fp: FlexWrap, **kwargs):
        bson = __import__('bson')
        with fp.open('rb') as f:
            ser = f.read()

        return bson.loads(ser, **kwargs)
