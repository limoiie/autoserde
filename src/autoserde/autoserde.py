from typing import Any, IO, Optional, Type, TypeVar, Union

import autodict
from autodict import AutoDict, Options
from autodict.errors import UnableFromDict, UnableToDict
from flexio import FilePointer

from autoserde.errors import NotDeserializable, NotSerializable, \
    UnknownSerdeFormat
from autoserde.formats.base import FlexWrap, SerdeFormat

T = TypeVar('T')


class Serdeable:
    """
    The base class for serdeable class.

    Derive :py:class:`Serdeable` will be automatically marked as dictable.
    """

    def __init_subclass__(cls, **kwargs):
        autodict.dictable(cls, **kwargs)

    def serialize(self, dst: Union[IO, FilePointer, None] = None, *,
                  fmt: Optional[str] = None, options: Optional[Options] = None,
                  close_io: Optional[bool] = None, **kwargs):
        """
        Dump obj into target in the specific serialization format.

        :param dst: Either a file-like object, or a file pointer-like object. If
          `None`, return the serialized bytes directly.
        :param fmt: Target serialization format, can be 'json', 'yaml', etc. If
          `None`, try to infer the format from file extension if there is.
        :param options: AutoDict options.
        :param close_io: A boolean value indicating if closing file before
          return or not. If `None`, default enabled if file was created by this
          method; otherwise, default as False.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: serialized string.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotSerializable: when some (nested) obj is not to-dictable
        :raises UnknownSerdeFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        return AutoSerde.serialize(self, dst=dst, fmt=fmt, options=options,
                                   close_io=close_io, **kwargs)

    @classmethod
    def deserialize(cls, src: Union[IO, FilePointer, None] = None, *,
                    body: Union[str, bytes, None] = None,
                    fmt: Optional[str] = None,
                    options: Optional[Options] = None,
                    close_io: Optional[bool] = None, **kwargs):
        """
        Load obj in the specific deserialization format.

        :param src: Either a file-like object, or a file pointer-like object. If
          `None`, taken body as deserializing source.
        :param body: If src is `None`, this will be used as the source.
        :param fmt: Target deserialization format, can be 'json', 'yaml', etc.
          If `None`, try to infer the format from file extension if there is.
        :param options: AutoDict options.
        :param close_io: A boolean value indicating if closing file before
          return or not. If `None`, default enabled if file was created by this
          method; otherwise, default as False.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: the instance deserialized as the given class `cls`.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotDeserializable: when some (nested) obj is not from-dictable
        :raises UnknownSerdeFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        return AutoSerde.deserialize(src=src, body=body, cls=cls, fmt=fmt,
                                     options=options, close_io=close_io,
                                     **kwargs)


class AutoSerde:
    """
    A lightweight framework of serialization and deserialization.
    """

    @staticmethod
    def serialize(ins: Any, dst: Union[IO, FilePointer, None] = None, *,
                  fmt: Optional[str] = None, options: Optional[Options] = None,
                  close_io: Optional[bool] = None, **kwargs) -> Optional[str]:
        """
        Dump obj into target in the specific serialization format.

        :param ins: The object to be dumped.
        :param dst: Either a file-like object, or a file pointer-like object. If
          `None`, return the serialized bytes directly.
        :param fmt: Target serialization format, can be 'json', 'yaml', etc. If
          `None`, try to infer the format from file extension if there is.
        :param options: AutoDict options.
        :param close_io: A boolean value indicating if closing file before
          return or not. If `None`, default enabled if file was created by this
          method; otherwise, default as False.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: serialized string.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotSerializable: when some (nested) obj is not to-dictable
        :raises UnknownSerdeFormat: when no registered class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        io_wrap = FlexWrap(fp=dst, close_io=close_io)
        fmt = fmt or io_wrap.filepath.suffix

        try:
            formatter = SerdeFormat.instance_by(fmt)
            obj = AutoDict.to_dict(ins, options=options)
            return formatter.dump(obj, io_wrap, **kwargs)

        except ModuleNotFoundError as err:
            err.msg += f' - required by serialization format {fmt}.'
            raise err

        except UnknownSerdeFormat as err:
            if not fmt:
                err.msg = f'Cannot infer ser format, specify it explicitly.'
            raise err

        except UnableToDict as err:
            raise NotSerializable(err.args) from err

    @staticmethod
    def deserialize(src: Union[IO, FilePointer, None] = None, *,
                    body: Union[str, bytes, None] = None, cls: Type[T] = None,
                    fmt: Optional[str] = None,
                    options: Optional[Options] = None,
                    close_io: Optional[bool] = None, **kwargs) -> T:
        """
        Load obj in the specific deserialization format.

        :param src: Either a file-like object, or a file pointer-like object. If
          `None`, taken body as deserializing source.
        :param body: If src is `None`, this will be used as the source.
        :param cls: The class that is going to be instantiated against. If
          `None`, try to infer the class from the serialized data.
        :param options: AutoDict options.
        :param fmt: Target deserialization format, can be 'json', 'yaml', etc.
          If `None`, try to infer the format from file extension if there is.
        :param body: If fp is `None`, this will be used as the source.
        :param close_io: A boolean value indicating if closing file before
          return or not. If `None`, default enabled if file was created by this
          method; otherwise, default as False.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: the instance deserialized as the given class `cls`.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotDeserializable: when some (nested) obj is not from-dictable
        :raises UnknownSerdeFormat: when no registered class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        io_wrap = FlexWrap(fp=src, init=body, close_io=close_io)
        fmt = fmt or io_wrap.filepath.suffix

        try:
            formatter = SerdeFormat.instance_by(fmt)
            obj = formatter.load(io_wrap, **kwargs)
            ins = AutoDict.from_dict(obj, cls=cls, options=options)
            return ins

        except ModuleNotFoundError as err:
            err.msg += f' - required by deserialization format {fmt}'
            raise err

        except UnknownSerdeFormat as err:
            if not fmt:
                err.msg = f'Cannot infer de format, specify it explicitly.'
            raise err

        except UnableFromDict as err:
            raise NotDeserializable(err.args) from err
