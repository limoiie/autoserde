from collections import namedtuple

import pytest

from autoserde import SerdeFormat
from autoserde.errors import UnknownSerdeFormat
from autoserde.formats import JsonFormat, YamlFormat
from autoserde.formats.base import FlexWrap

testcase = namedtuple('C', 'ext,exc,expect_type,name')


def generate_testcases():
    return [
        testcase(
            name='extension without prefix dot',
            ext='json',
            exc=None,
            expect_type=JsonFormat,
        ),
        testcase(
            name='extension',
            ext='.json',
            exc=None,
            expect_type=JsonFormat,
        ),
        testcase(
            name='extension 0 without prefix dot in multiple',
            ext='yaml',
            exc=None,
            expect_type=YamlFormat,
        ),
        testcase(
            name='extension 1 without prefix dot in multiple',
            ext='yml',
            exc=None,
            expect_type=YamlFormat,
        ),
        testcase(
            name='extension 0 in multiple',
            ext='.yaml',
            exc=None,
            expect_type=YamlFormat,
        ),
        testcase(
            name='extension 1 in multiple',
            ext='.yml',
            exc=None,
            expect_type=YamlFormat,
        ),
        testcase(
            name='unknown extension',
            ext='unknown',
            exc=UnknownSerdeFormat,
            expect_type=None,
        ),
    ]


def case_name(case):
    return case.name


@pytest.mark.parametrize('case', generate_testcases(), ids=case_name)
def test_instance_by(case: testcase):
    if case.exc is None:
        fmt = SerdeFormat.instance_by(case.ext)
        assert isinstance(fmt, case.expect_type)

    else:
        with pytest.raises(case.exc):
            SerdeFormat.instance_by(case.ext)


Case = namedtuple('Case', 'fmt,obj')

obj = {
    'string': 'string',
    'float': 1.,
    'integer': 20,
    'array': [1, 2, 3],
    'null': None,
}

cases = {
    'bson': Case(fmt='bson', obj=obj),
    'yaml': Case(fmt='yaml', obj=obj),
    'msgpack': Case(fmt='msgpack', obj=obj),
}


@pytest.mark.parametrize('case', cases.values(), ids=cases.keys())
def test_transform(case: Case):
    fmt = SerdeFormat.instance_by(case.fmt)

    wrap = FlexWrap()
    fmt.dump(case.obj, wrap)

    serialization = wrap.read_all()
    print(f'{fmt}: len={len(serialization)}')
    output = fmt.load(FlexWrap(init=serialization))
    assert output == case.obj
