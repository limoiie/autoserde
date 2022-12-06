import os
import pathlib
import tempfile
from collections import namedtuple
from typing import List, Tuple, Union

import pytest
from autodict import Options

from autoserde import deserializable, serdeable, serializable
from autoserde.autoserde import AutoSerde, Serdeable
from autoserde.errors import NotDeserializable, NotSerializable
from conftest import Raises


@serdeable
class Normal:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, Normal) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@serdeable
class WithGeneric:
    list_value: List[int]
    tuple_value: Tuple[int, str]
    union_value: Union[int, str]

    def __init__(self, list_value, tuple_value, union_value):
        self.list_value = list_value
        self.tuple_value = tuple_value
        self.union_value = union_value

    def __eq__(self, other):
        return isinstance(other, WithGeneric) and \
            self.list_value == other.list_value and \
            self.tuple_value == other.tuple_value and \
            self.union_value == other.union_value


class Unregistered:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, Unregistered) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@serializable
class OnlySerializable:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, OnlyDeserializable) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@deserializable
class OnlyDeserializable:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, OnlyDeserializable) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@serdeable
class NestedSerdeable:
    a: Normal

    def __init__(self, a, count):
        self.a = a
        self.count = count

    def __eq__(self, other):
        return isinstance(other, NestedSerdeable) and \
            self.a == other.a and \
            self.count == other.count


@serdeable
class NestedUnSerdeable:
    a: Unregistered

    def __init__(self, a, count):
        self.a = a
        self.count = count

    def __eq__(self, other):
        return isinstance(other, NestedUnSerdeable) and \
            self.a == other.a and \
            self.count == other.count


class UnSerdeableNested:
    a: Normal

    def __init__(self, a, count):
        self.a = a
        self.count = count

    def __eq__(self, other):
        return isinstance(other, UnSerdeableNested) and \
            self.a == other.a and \
            self.count == other.count


class DeriveSerdeable(Serdeable):
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, DeriveSerdeable) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


class DeriveNestedSerdeable(Serdeable):
    c: DeriveSerdeable

    def __init__(self, c, count):
        self.c = c
        self.count = count

    def __eq__(self, other):
        return isinstance(other, DeriveNestedSerdeable) and \
            self.c == other.c and \
            self.count == other.count


GoodCase = namedtuple('GC', 'obj,fmt,serialized,opts,name')

BadSerCase = namedtuple('BSC', 'obj,fmt,raises,name')

BadDeCase = namedtuple('BDC', 'serialized,fmt,raises,name')


def case_name(case):
    return case.name


def annotator_good_cases() -> List[GoodCase]:
    return [
        GoodCase(
            name='embedded with class info',
            obj=Normal(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "Normal"}',
            opts=Options(with_cls=True),
        ),
        GoodCase(
            name='embedded with generic fields',
            obj=WithGeneric(list_value=[1, 2, 3], tuple_value=(4, '5'),
                            union_value='6'),
            fmt='json',
            serialized=r'{"list_value": [1, 2, 3], "tuple_value": [4, "5"], "union_value": "6"}',
            opts=Options(with_cls=False),
        ),
        GoodCase(
            name='without embedding class info',
            obj=Normal(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10}',
            opts=Options(with_cls=False),
        ),
        GoodCase(
            name='nested serializable embedded with class info',
            obj=NestedSerdeable(a=Normal(str_value='limo', int_value=10),
                                count=20),
            fmt='json',
            serialized=r'{"a": {"str_value": "limo", "int_value": 10, "@": "Normal"}, "count": 20, "@": "NestedSerdeable"}',
            opts=Options(with_cls=True),
        )
    ]


def annotator_bad_ser_cases() -> List[BadSerCase]:
    return [
        BadSerCase(
            name='not serializable',
            obj=Unregistered(str_value='limo', int_value=10),
            fmt='json',
            raises=Raises(
                exc=NotSerializable,
                kwargs=dict(match=r'.*Unregistered.*serializable.*')),
        ),
        BadSerCase(
            name='non-serializable partially deserializable',
            obj=OnlyDeserializable(str_value='limo', int_value=10),
            fmt='json',
            raises=Raises(exc=NotSerializable,
                          kwargs=dict(
                              match=r'.*OnlyDeserializable.*serializable.*')),
        ),
        BadSerCase(
            name='serializable has a non-serializable field',
            obj=NestedUnSerdeable(
                a=Unregistered(str_value='limo', int_value=10), count=20),
            fmt='json',
            raises=Raises(exc=NotSerializable,
                          kwargs=dict(match=r'.*Unregistered.*serializable.*')),
        ),
        BadSerCase(
            name='non-serializable has a serializable field',
            obj=UnSerdeableNested(a=Normal(str_value='limo', int_value=10),
                                  count=20),
            fmt='json',
            raises=Raises(exc=NotSerializable,
                          kwargs=dict(
                              match=r'.*UnSerdeableNested.*serializable.*')),
        ),
    ]


def annotator_bad_de_cases() -> List[BadDeCase]:
    return [
        BadDeCase(
            name='not deserializable',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "Unregistered"}',
            fmt='json',
            raises=Raises(exc=NotDeserializable,
                          kwargs=dict(
                              match=r'.*Unregistered.*deserializable.*'),
                          ),
        ),
        BadDeCase(
            name='non-deserializable partially serializable',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "Unregistered"}',
            fmt='json',
            raises=Raises(exc=NotDeserializable,
                          kwargs=dict(
                              match=r'.*Unregistered.*deserializable.*')),
        ),
        BadDeCase(
            name='deserializable has a non-deserializable field',
            serialized=r'{"a": {"str_value": "limo", "int_value": 10, "@": "Unregistered"}, "count": 20, "@": "NestedUnSerdeable"}',
            fmt='json',
            raises=Raises(exc=NotDeserializable,
                          kwargs=dict(
                              match=r'.*Unregistered.*deserializable.*')),
        ),
        BadDeCase(
            name='non-deserializable has a deserializable field',
            serialized=r'{"a": {"str_value": "limo", "int_value": 10, "@": "Normal"}, "count": 20, "@": "UnSerdeableNested"}',
            fmt='json',
            raises=Raises(exc=NotDeserializable,
                          kwargs=dict()),
        ),
    ]


def derive_good_cases() -> List[GoodCase]:
    return [
        GoodCase(
            name='embedded with class info',
            obj=DeriveSerdeable(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "DeriveSerdeable"}',
            opts=Options(with_cls=True),
        ),
        GoodCase(
            name='without embedding class info',
            obj=DeriveSerdeable(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10}',
            opts=Options(with_cls=False),
        ),
        GoodCase(
            name='nested serializable embedded with class info',
            obj=DeriveNestedSerdeable(
                c=DeriveSerdeable(str_value='limo', int_value=10), count=20),
            fmt='json',
            serialized=r'{"c": {"str_value": "limo", "int_value": 10, "@": "DeriveSerdeable"}, "count": 20, "@": "DeriveNestedSerdeable"}',
            opts=Options(with_cls=True),
        )
    ]


class TestAnnotate:
    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_string(self, case: GoodCase):
        serialized_a = AutoSerde.serialize(case.obj, fmt=case.fmt,
                                           options=case.opts)
        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_from_string(self, case: GoodCase):
        cls = type(case.obj) if not case.opts.with_cls else None
        a = AutoSerde.deserialize(body=case.serialized, cls=cls, fmt=case.fmt,
                                  options=case.opts)

        assert a == case.obj

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_file_like(self, tmp_file, case: GoodCase):
        AutoSerde.serialize(case.obj, tmp_file, fmt=case.fmt,
                            options=case.opts)

        tmp_file.seek(0)
        serialized_a = tmp_file.read()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_file_like(self, tmp_file, case: GoodCase):
        tmp_file.write(case.serialized)
        tmp_file.seek(0)

        cls = type(case.obj) if not case.opts.with_cls else None
        out_a = AutoSerde.deserialize(tmp_file, cls=cls, fmt=case.fmt,
                                      options=case.opts)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_file_like_by_infer_fmt(self, tmp_json_file, case):
        AutoSerde.serialize(case.obj, tmp_json_file, fmt=None,
                            options=case.opts)

        tmp_json_file.seek(0)
        serialized_a = tmp_json_file.read()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_file_like_by_infer_fmt(self, tmp_json_file, case):
        tmp_json_file.write(case.serialized)
        tmp_json_file.seek(0)

        cls = type(case.obj) if not case.opts.with_cls else None
        out_a = AutoSerde.deserialize(tmp_json_file, cls=cls, fmt=None,
                                      options=case.opts)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_path_like(self, tmp_filepath, case: GoodCase):
        AutoSerde.serialize(case.obj, tmp_filepath, fmt=case.fmt,
                            options=case.opts)
        serialized_a = tmp_filepath.read_text()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_path_like(self, tmp_filepath, case: GoodCase):
        tmp_filepath.write_text(case.serialized)

        cls = type(case.obj) if not case.opts.with_cls else None
        out_a = AutoSerde.deserialize(tmp_filepath, cls=cls, fmt=case.fmt,
                                      options=case.opts)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_path_like_by_infer_fmt(self, tmp_json_filepath, case):
        AutoSerde.serialize(case.obj, tmp_json_filepath, fmt=None,
                            options=case.opts)
        serialized_a = tmp_json_filepath.read_text()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_path_like_by_infer_fmt(self, tmp_json_filepath,
                                                   case: GoodCase):
        tmp_json_filepath.write_text(case.serialized)

        cls = type(case.obj) if not case.opts.with_cls else None
        out_a = AutoSerde.deserialize(tmp_json_filepath, cls=cls, fmt=None,
                                      options=case.opts)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_bad_ser_cases(), ids=case_name)
    def test_serialize_not_serializable(self, case: BadSerCase):
        with pytest.raises(case.raises.exc, **case.raises.kwargs):
            AutoSerde.serialize(case.obj, fmt=case.fmt)

    @pytest.mark.parametrize('case', annotator_bad_de_cases(), ids=case_name)
    def test_deserialize_not_deserializable(self, case: BadDeCase):
        with pytest.raises(case.raises.exc, **case.raises.kwargs):
            AutoSerde.deserialize(body=case.serialized, fmt=case.fmt)


class TestDerive:
    @pytest.mark.parametrize('case', derive_good_cases(), ids=case_name)
    def test_serialize_to_string(self, case: GoodCase):
        serialized_a = case.obj.serialize(fmt=case.fmt, options=case.opts)
        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', derive_good_cases(), ids=case_name)
    def test_deserialize_from_string(self, case: GoodCase):
        cls = type(case.obj)
        a = cls.deserialize(body=case.serialized, fmt=case.fmt,
                            options=case.opts)

        assert a == case.obj


@pytest.fixture(scope='function')
def tmp_json_filepath(tmp_path):
    path = tempfile.mktemp(dir=tmp_path, suffix='.json')
    yield pathlib.Path(path)
    os.path.exists(path) and os.remove(path)


@pytest.fixture(scope='function')
def tmp_filepath(tmp_path):
    path = tempfile.mktemp(dir=tmp_path)
    yield pathlib.Path(path)
    os.path.exists(path) and os.remove(path)


@pytest.fixture(scope='function')
def tmp_json_file(tmp_json_filepath):
    with open(tmp_json_filepath, 'w+') as file:
        yield file


@pytest.fixture(scope='function')
def tmp_file(tmp_filepath):
    with open(tmp_filepath, 'w+') as file:
        yield file
