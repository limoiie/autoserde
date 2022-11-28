import io
import os
import pathlib
from typing import Any, IO, Optional, Type, TypeVar

import autodict
from autodict import AutoDict, UnableFromDict, UnableToDict

from autoserde.formats.base import SerdeFormat

T = TypeVar('T')


class NotSerializable(Exception):
    def __init__(self, cls):
        super(Exception, self).__init__(
            f'{cls}, please mark it as serializable'
        )


class NotDeserializable(Exception):
    def __init__(self, cls):
        super(Exception, self).__init__(
            f'{cls}, please mark it as deserializable'
        )


class Serdeable:
    """
    The base class for serdeable class.

    Derive :py:class:`Serdeable` will be automatically marked as dictable.
    """

    def __init_subclass__(cls, **kwargs):
        autodict.dictable(cls, **kwargs)

    def serialize(self, fp: Optional[IO[str] or os.PathLike or str] = None,
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
        :raises UnknownFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        return AutoSerde.serialize(self, fp=fp, fmt=fmt, with_cls=with_cls,
                                   close_fp=close_fp, **kwargs)

    @classmethod
    def deserialize(cls, fp: IO[str] or os.PathLike or str or bytes,
                    fmt: Optional[str] = None, close_fp: bool = False,
                    **kwargs):
        """
        Load obj in the specific deserialization format.

        :param fp: A file-like or a filepath-like object. If in `bytes`, takes
          it as the raw serialization sequence directly.
        :param fmt: Target deserialization format, can be 'json', 'yaml', etc.
          If `None`, try to infer the format from file extension if there is.
        :param close_fp: Close file before return or not. Default as `False`.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: the instance deserialized as the given class `cls`.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotDeserializable: when some (nested) obj is not from-dictable
        :raises UnknownFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        return AutoSerde.deserialize(fp, cls=cls, fmt=fmt, close_fp=close_fp,
                                     **kwargs)


class AutoSerde:
    """
    A lightweight framework of serialization and deserialization.
    """

    @staticmethod
    def serialize(obj: Any, fp: Optional[IO[str] or os.PathLike or str] = None,
                  fmt: Optional[str] = None, with_cls: bool = True,
                  close_fp: bool = False, **kwargs):
        """
        Dump obj into target in the specific serialization format.

        :param obj: The object to be dumped.
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
        :raises UnknownFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        filename = None

        if fp is None:
            fp = io.StringIO()
            close_fp = True

        elif isinstance(fp, (os.PathLike, str)):
            filename = pathlib.Path(fp)
            fp = open(filename, 'w+')
            close_fp = True

        elif hasattr(fp, 'name'):
            filename = pathlib.Path(fp.name)

        fmt = fmt or (filename and filename.suffix.lstrip('.'))
        if fmt is None:
            raise ValueError(
                f'Cannot infer ser format, specify it explicitly.')

        try:
            d = AutoDict.to_dict(obj, with_cls=with_cls)
            formatter = SerdeFormat.instance_by(fmt)
            formatter.dump(d, fp, **kwargs)

            if isinstance(fp, io.StringIO):
                fp.seek(0)
                return fp.read()

        except ModuleNotFoundError as err:
            err.msg += f' - required by serialization format {fmt}'
            raise err

        except UnableToDict as err:
            raise NotSerializable(err.args) from err

        finally:
            if close_fp:
                fp.close()

    @staticmethod
    def deserialize(fp: IO[str] or os.PathLike or str,
                    cls: Type[T] = None, fmt: Optional[str] = None,
                    close_fp: bool = False, **kwargs) -> T:
        """
        Load obj in the specific deserialization format.

        :param fp: A file-like or a filepath-like object. If in `bytes`, takes
          it as the raw serialization sequence directly.
        :param cls: The class that is going to be instantiated against. If
          `None`, try to infer the class from the serialized data.
        :param fmt: Target deserialization format, can be 'json', 'yaml', etc.
          If `None`, try to infer the format from file extension if there is.
        :param close_fp: Close file before return or not. Default as `False`.
        :param kwargs: optional keyword args passing to underlying format lib.
        :return: the instance deserialized as the given class `cls`.
        :raises ModuleNotFoundError: when failed to import missing format lib
        :raises NotDeserializable: when some (nested) obj is not from-dictable
        :raises UnknownFormat: when no registered format class for the format
        :raises ValueError: when no format provided and failed to infer it
        """
        filename = None

        if isinstance(fp, (str,)) and not os.path.exists(fp):
            fp = io.StringIO(fp)
            close_fp = False

        elif isinstance(fp, (os.PathLike, str)):
            filename = pathlib.Path(fp)
            fp = open(filename, 'rb')
            close_fp = True

        elif hasattr(fp, 'name'):
            filename = pathlib.Path(fp.name)

        fmt = fmt or (filename and filename.suffix.lstrip('.'))
        if fmt is None:
            raise ValueError(
                f'Cannot infer de format, specify it explicitly.')

        try:
            formatter = SerdeFormat.instance_by(fmt)
            obj = AutoDict.from_dict(formatter.load(fp, **kwargs), cls=cls)
            return obj

        except ModuleNotFoundError as err:
            err.msg += f' - required by deserialization format {fmt}'
            raise err

        except UnableFromDict as err:
            raise NotDeserializable(err.args) from err

        finally:
            if close_fp:
                fp.close()
