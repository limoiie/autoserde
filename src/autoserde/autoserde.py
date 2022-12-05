from pathlib import Path
from typing import Any, Optional, Type, TypeVar

import autodict
from autodict import AutoDict
from autodict.errors import UnableFromDict, UnableToDict
from flexio import FlexTextIO
from flexio.flexio import FilePointer

from autoserde.errors import NotDeserializable, NotSerializable, \
    UnknownSerdeFormat
from autoserde.formats.base import SerdeFormat

T = TypeVar('T')


class Serdeable:
    """
    The base class for serdeable class.

    Derive :py:class:`Serdeable` will be automatically marked as dictable.
    """

    def __init_subclass__(cls, **kwargs):
        autodict.dictable(cls, **kwargs)

    def serialize(self, fp: Optional[FilePointer] = None, *,
                  fmt: Optional[str] = None, with_cls: bool = True,
                  close_fp: bool = False, **kwargs):
        """
        Dump obj into target in the specific serialization format.

        :param fp: A file-like or a filepath-like object. If `None`, return the
          serialized bytes directly.
        :param fmt: Target serialization format, can be 'json', 'yaml', etc. If
          `None`, try to infer the format from file extension if there is.
        :param with_cls: A boolean value indicating if embedding the class into
          the final serialization or not.
        :param close_fp: Close file before return or not. Default as `False`.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: serialized string.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotSerializable: when some (nested) obj is not to-dictable
        :raises UnknownSerdeFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        return AutoSerde.serialize(self, fp=fp, fmt=fmt, with_cls=with_cls,
                                   close_fp=close_fp, **kwargs)

    @classmethod
    def deserialize(cls, fp: Optional[FilePointer] = None, *,
                    body: Optional[str] = None, fmt: Optional[str] = None,
                    close_fp: bool = False, **kwargs):
        """
        Load obj in the specific deserialization format.

        :param fp: A file-like or a filepath-like object.
        :param body: If fp is `None`, this will be used as the source.
        :param fmt: Target deserialization format, can be 'json', 'yaml', etc.
          If `None`, try to infer the format from file extension if there is.
        :param close_fp: Close file before return or not. Default as `False`.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: the instance deserialized as the given class `cls`.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotDeserializable: when some (nested) obj is not from-dictable
        :raises UnknownSerdeFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        return AutoSerde.deserialize(fp, body=body, cls=cls, fmt=fmt,
                                     close_fp=close_fp, **kwargs)


class AutoSerde:
    """
    A lightweight framework of serialization and deserialization.
    """

    @staticmethod
    def serialize(ins: Any, fp: Optional[FilePointer] = None, *,
                  fmt: Optional[str] = None, with_cls: bool = True,
                  close_fp: Optional[bool] = None, **kwargs) -> Optional[str]:
        """
        Dump obj into target in the specific serialization format.

        :param ins: The object to be dumped.
        :param fp: A file-like or a filepath-like object. If `None`, return the
          serialized bytes directly.
        :param fmt: Target serialization format, can be 'json', 'yaml', etc. If
          `None`, try to infer the format from file extension if there is.
        :param with_cls: A boolean value indicating if embedding the class into
          the final serialization or not.
        :param close_fp: Close file before return or not. Default as `None`. If
          `None`, the fp will be closed only if it was created inner this call.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: serialized string.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotSerializable: when some (nested) obj is not to-dictable
        :raises UnknownSerdeFormat: when no registered class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        with FlexTextIO(fp, mode='wt+', close_io=close_fp) as io_:
            filename = Path(io_.name if isinstance(io_.name, str) else '')
            fmt = fmt or filename.suffix

            try:
                formatter = SerdeFormat.instance_by(fmt)
                obj = AutoDict.to_dict(ins, with_cls=with_cls)
                formatter.dump(obj, io_, **kwargs)

                if io_.in_mem:
                    io_.seek(0)
                    return io_.read()

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
    def deserialize(fp: Optional[FilePointer] = None, *,
                    body: Optional[str] = None, cls: Type[T] = None,
                    fmt: Optional[str] = None, close_fp: Optional[bool] = None,
                    **kwargs) -> T:
        """
        Load obj in the specific deserialization format.

        :param fp: A file-like or a filepath-like object. If in `bytes`, takes
          it as the raw serialization sequence directly.
        :param cls: The class that is going to be instantiated against. If
          `None`, try to infer the class from the serialized data.
        :param fmt: Target deserialization format, can be 'json', 'yaml', etc.
          If `None`, try to infer the format from file extension if there is.
        :param body: If fp is `None`, this will be used as the source.
        :param close_fp: Close file before return or not. Default as `False`.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: the instance deserialized as the given class `cls`.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotDeserializable: when some (nested) obj is not from-dictable
        :raises UnknownSerdeFormat: when no registered class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        with FlexTextIO(fp, mode='rt', init=body, close_io=close_fp) as io_:
            filename = Path(io_.name if isinstance(io_.name, str) else '')
            fmt = fmt or filename.suffix

            try:
                formatter = SerdeFormat.instance_by(fmt)
                obj = formatter.load(io_, **kwargs)
                ins = AutoDict.from_dict(obj, cls=cls)
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
