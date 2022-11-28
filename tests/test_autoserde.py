import os
import tempfile
from collections import namedtuple
from typing import List

import pytest

from autoserde import AutoSerde, NotDeserializable, NotSerializable, Serdeable, \
    deserializable, serdeable, serializable


@serdeable
class A:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, A) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


class A2:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, A2) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@serializable
class A3:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, A4) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@deserializable
class A4:
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, A4) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


@serdeable
class B:
    a: A

    def __init__(self, a, count):
        self.a = a
        self.count = count

    def __eq__(self, other):
        return isinstance(other, B) and \
            self.a == other.a and \
            self.count == other.count


@serdeable
class B2:
    a: A2

    def __init__(self, a, count):
        self.a = a
        self.count = count

    def __eq__(self, other):
        return isinstance(other, B2) and \
            self.a == other.a and \
            self.count == other.count


class B3:
    a: A

    def __init__(self, a, count):
        self.a = a
        self.count = count

    def __eq__(self, other):
        return isinstance(other, B3) and \
            self.a == other.a and \
            self.count == other.count


class C(Serdeable):
    def __init__(self, str_value, int_value):
        self.str_value = str_value
        self.int_value = int_value

    def __eq__(self, other):
        return isinstance(other, C) and \
            self.str_value == other.str_value and \
            self.int_value == other.int_value


class D(Serdeable):
    c: C

    def __init__(self, c, count):
        self.c = c
        self.count = count

    def __eq__(self, other):
        return isinstance(other, D) and \
            self.c == other.c and \
            self.count == other.count


good_case = namedtuple('GC', 'obj,fmt,serialized,with_cls,name')

bad_ser_case = namedtuple('BSC', 'obj,fmt,exc,raises,name')

bad_de_case = namedtuple('BDC', 'serialized,fmt,exc,raises,name')


def case_name(case):
    return case.name


def annotator_good_cases() -> List[good_case]:
    return [
        good_case(
            name='embedded with class info',
            obj=A(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "A"}',
            with_cls=True,
        ),
        good_case(
            name='without embedding class info',
            obj=A(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10}',
            with_cls=False,
        ),
        good_case(
            name='nested serializable embedded with class info',
            obj=B(a=A(str_value='limo', int_value=10), count=20),
            fmt='json',
            serialized=r'{"a": {"str_value": "limo", "int_value": 10, "@": "A"}, "count": 20, "@": "B"}',
            with_cls=True,
        )
    ]


def annotator_bad_ser_cases() -> List[bad_ser_case]:
    return [
        bad_ser_case(
            name='not serializable',
            obj=A2(str_value='limo', int_value=10),
            fmt='json',
            exc=NotSerializable,
            raises=dict(match=r'.*A2.*serializable.*'),
        ),
        bad_ser_case(
            name='non-serializable partially deserializable',
            obj=A4(str_value='limo', int_value=10),
            fmt='json',
            exc=NotSerializable,
            raises=dict(match=r'.*A4.*serializable.*'),
        ),
        bad_ser_case(
            name='serializable has a non-serializable field',
            obj=B2(a=A2(str_value='limo', int_value=10), count=20),
            fmt='json',
            exc=NotSerializable,
            raises=dict(match=r'.*A2.*serializable.*'),
        ),
        bad_ser_case(
            name='non-serializable has a serializable field',
            obj=B3(a=A(str_value='limo', int_value=10), count=20),
            fmt='json',
            exc=NotSerializable,
            raises=dict(match=r'.*B3.*serializable.*'),
        ),
    ]


def annotator_bad_de_cases() -> List[bad_de_case]:
    return [
        bad_de_case(
            name='not deserializable',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "A2"}',
            fmt='json',
            exc=NotDeserializable,
            raises=dict(match=r'.*A2.*deserializable.*'),
        ),
        bad_de_case(
            name='non-deserializable partially serializable',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "A2"}',
            fmt='json',
            exc=NotDeserializable,
            raises=dict(match=r'.*A2.*deserializable.*'),
        ),
        bad_de_case(
            name='deserializable has a non-deserializable field',
            serialized=r'{"a": {"str_value": "limo", "int_value": 10, "@": "A2"}, "count": 20, "@": "B2"}',
            fmt='json',
            exc=NotDeserializable,
            raises=dict(match=r'.*A2.*deserializable.*'),
        ),
        bad_de_case(
            name='non-deserializable has a deserializable field',
            serialized=r'{"a": {"str_value": "limo", "int_value": 10, "@": "A"}, "count": 20, "@": "B3"}',
            fmt='json',
            exc=NotDeserializable,
            raises=dict(),
        ),
    ]


def derive_good_cases() -> List[good_case]:
    return [
        good_case(
            name='embedded with class info',
            obj=C(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10, "@": "C"}',
            with_cls=True,
        ),
        good_case(
            name='without embedding class info',
            obj=C(str_value='limo', int_value=10),
            fmt='json',
            serialized=r'{"str_value": "limo", "int_value": 10}',
            with_cls=False,
        ),
        good_case(
            name='nested serializable embedded with class info',
            obj=D(c=C(str_value='limo', int_value=10), count=20),
            fmt='json',
            serialized=r'{"c": {"str_value": "limo", "int_value": 10, "@": "C"}, "count": 20, "@": "D"}',
            with_cls=True,
        )
    ]


class TestAnnotate:
    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_string(self, case: good_case):
        serialized_a = AutoSerde.serialize(case.obj, fmt=case.fmt,
                                           with_cls=case.with_cls)
        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_from_string(self, case: good_case):
        cls = type(case.obj) if not case.with_cls else None
        a = AutoSerde.deserialize(case.serialized, cls=cls, fmt=case.fmt)

        assert a == case.obj

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_file_like(self, tmp_file, case: good_case):
        AutoSerde.serialize(case.obj, tmp_file, fmt=case.fmt,
                            with_cls=case.with_cls)

        tmp_file.seek(0)
        serialized_a = tmp_file.read()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_file_like(self, tmp_file, case: good_case):
        tmp_file.write(case.serialized)
        tmp_file.seek(0)

        cls = type(case.obj) if not case.with_cls else None
        out_a = AutoSerde.deserialize(tmp_file, cls=cls, fmt=case.fmt)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_file_like_by_infer_fmt(self, tmp_json_file, case):
        AutoSerde.serialize(case.obj, tmp_json_file, fmt=None,
                            with_cls=case.with_cls)

        tmp_json_file.seek(0)
        serialized_a = tmp_json_file.read()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_file_like_by_infer_fmt(self, tmp_json_file, case):
        tmp_json_file.write(case.serialized)
        tmp_json_file.seek(0)

        cls = type(case.obj) if not case.with_cls else None
        out_a = AutoSerde.deserialize(tmp_json_file, cls=cls, fmt=None)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_path_like(self, tmp_filepath, case: good_case):
        AutoSerde.serialize(case.obj, tmp_filepath, fmt=case.fmt,
                            with_cls=case.with_cls)

        with open(tmp_filepath, 'r') as file:
            serialized_a = file.read()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_path_like(self, tmp_filepath, case: good_case):
        with open(tmp_filepath, 'w+') as tmp:
            tmp.write(case.serialized)

        cls = type(case.obj) if not case.with_cls else None
        out_a = AutoSerde.deserialize(tmp_filepath, cls=cls, fmt=case.fmt)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_serialize_to_path_like_by_infer_fmt(self, tmp_json_filepath, case):
        AutoSerde.serialize(case.obj, tmp_json_filepath, fmt=None,
                            with_cls=case.with_cls)

        with open(tmp_json_filepath, 'r') as file:
            serialized_a = file.read()

        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', annotator_good_cases(), ids=case_name)
    def test_deserialize_to_path_like_by_infer_fmt(self, tmp_json_filepath,
                                                   case: good_case):
        with open(tmp_json_filepath, 'w+') as tmp:
            tmp.write(case.serialized)

        cls = type(case.obj) if not case.with_cls else None
        out_a = AutoSerde.deserialize(tmp_json_filepath, cls=cls, fmt=None)

        assert case.obj == out_a

    @pytest.mark.parametrize('case', annotator_bad_ser_cases(), ids=case_name)
    def test_serialize_not_serializable(self, case: bad_ser_case):
        with pytest.raises(case.exc, **case.raises):
            AutoSerde.serialize(case.obj, fmt=case.fmt)

    @pytest.mark.parametrize('case', annotator_bad_de_cases(), ids=case_name)
    def test_deserialize_not_deserializable(self, case: bad_de_case):
        with pytest.raises(case.exc, **case.raises):
            AutoSerde.deserialize(case.serialized, fmt=case.fmt)


class TestDerive:
    @pytest.mark.parametrize('case', derive_good_cases(), ids=case_name)
    def test_serialize_to_string(self, case: good_case):
        serialized_a = case.obj.serialize(fmt=case.fmt, with_cls=case.with_cls)
        assert serialized_a == case.serialized

    @pytest.mark.parametrize('case', derive_good_cases(), ids=case_name)
    def test_deserialize_from_string(self, case: good_case):
        cls = type(case.obj)
        a = cls.deserialize(case.serialized, fmt=case.fmt)

        assert a == case.obj


@pytest.fixture(scope='function')
def tmp_json_filepath(tmp_path):
    path = tempfile.mktemp(dir=tmp_path, suffix='.json')
    yield path
    os.path.exists(path) and os.remove(path)


@pytest.fixture(scope='function')
def tmp_filepath(tmp_path):
    path = tempfile.mktemp(dir=tmp_path)
    yield path
    os.path.exists(path) and os.remove(path)


@pytest.fixture(scope='function')
def tmp_json_file(tmp_json_filepath):
    with open(tmp_json_filepath, 'w+') as file:
        yield file


@pytest.fixture(scope='function')
def tmp_file(tmp_filepath):
    with open(tmp_filepath, 'w+') as file:
        yield file
