from abc import abstractmethod
from typing import Any, IO

from registry import SubclassRegistry


class UnknownSerdeFormat(Exception):
    def __init__(self, fmt):
        super().__init__()
        self.msg = (
            f'no Format registered in `:py:class:SerdeFormat` for format {fmt}.'
        )

    def __str__(self):
        return self.msg


class SerdeFormat(SubclassRegistry):
    """
    Formatter of serialization/deserialization.

    Derive :py:class:`SerdeFormat` for supporting more kinds of serde formats.
    """

    @abstractmethod
    def dump(self, obj: Any, fp: IO[str], **kwargs):
        """
        Dump the given object to a file-like.
        """
        pass

    @abstractmethod
    def load(self, fp: IO[str], **kwargs):
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
