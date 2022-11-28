"""A lightweight serde framework."""

from autodict import dictable, from_dictable, to_dictable

from autoserde.autoserde import AutoSerde, NotDeserializable, NotSerializable, \
    Serdeable
from autoserde.formats.base import SerdeFormat

__all__ = ['serdeable', 'serializable', 'deserializable', 'AutoSerde',
           'NotSerializable', 'NotDeserializable', 'Serdeable', 'SerdeFormat']

serdeable = dictable

serializable = to_dictable

deserializable = from_dictable
