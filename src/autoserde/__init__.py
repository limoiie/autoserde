"""A lightweight serde framework."""

__all__ = ['serdeable', 'serializable', 'deserializable', 'AutoSerde',
           'Options', 'Serdeable', 'SerdeFormat']

try:
    import importlib.metadata as _importlib_metadata
except ModuleNotFoundError:
    # noinspection PyUnresolvedReferences
    import importlib_metadata as _importlib_metadata

try:
    __version__ = _importlib_metadata.version("autoserde")
except _importlib_metadata.PackageNotFoundError:
    __version__ = "unknown version"

from autodict import Options, dictable, from_dictable, to_dictable

from .autoserde import AutoSerde, Serdeable
from .formats.base import SerdeFormat

serdeable = dictable

serializable = to_dictable

deserializable = from_dictable
