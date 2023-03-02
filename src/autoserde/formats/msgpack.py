from typing import Any

from autoserde.formats.base import FlexWrap, SerdeFormat


class MsgpackFormat(SerdeFormat, exts=['.msgpack']):
    def dump(self, obj: Any, fp: FlexWrap, **kwargs):
        msgpack = __import__('msgpack')
        with fp.open('wb+') as f:
            return msgpack.dump(obj, f, **kwargs)

    def load(self, fp: FlexWrap, **kwargs):
        msgpack = __import__('msgpack')
        with fp.open('rb') as f:
            return msgpack.load(f, **kwargs)
