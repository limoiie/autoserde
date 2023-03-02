import dataclasses
from abc import abstractmethod
from pathlib import Path
from typing import Any, IO, Optional, Union

import flexio
from flexio import FilePointer
from flexio.flexio import is_file_pointer
from registry import SubclassRegistry

from autoserde.errors import UnknownSerdeFormat


@dataclasses.dataclass
class FlexWrap:
    fp: Union[IO, FilePointer, None] = None
    init: Union[str, bytes, None] = None
    close_io: Optional[bool] = None
    flexio = None

    @property
    def filepath(self):
        if self.fp is None:
            return Path()

        if is_file_pointer(self.fp):
            return Path(self.fp) if not isinstance(self.fp, int) else Path()

        return Path(getattr(self.fp, 'name'))

    def open(self, mode):
        close_io = False if self.fp is None else self.close_io
        self.flexio = flexio.flex_open(f=self.fp, mode=mode, init=self.init,
                                       close_io=close_io)
        return self.flexio

    def read_all(self):
        self.flexio.seek(0)
        return self.flexio.read()


class SerdeFormat(SubclassRegistry):
    """
    Formatter of serialization/deserialization.

    Derive :py:class:`SerdeFormat` for supporting more kinds of serde formats.
    """

    @abstractmethod
    def dump(self, obj: Any, fp: FlexWrap, **kwargs):
        """
        Dump the given object to a file-like.
        """
        pass

    @abstractmethod
    def load(self, fp: FlexWrap, **kwargs):
        """
        Load from a file-like.
        """
        pass

    @staticmethod
    def instance_by(fmt: str, **kwargs) -> 'SerdeFormat':
        """
        Find a registered format class and instantiate.

        :param fmt: file extension with or without prefix dot.
        :return: the matched formatter instance
        :raises UnknownSerdeFormat: if not matched
        """
        if not fmt.startswith('.'):
            fmt = '.' + fmt

        for cls, meta in SerdeFormat.center().items():
            if fmt in meta['exts']:
                return cls(**kwargs)

        raise UnknownSerdeFormat(fmt)
