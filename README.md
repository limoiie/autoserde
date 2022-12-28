# AutoSerde

[![AutoSerde unit tests](https://github.com/limoiie/autoserde/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/limoiie/autoserde/actions?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b5df12ffde7f4d37a8773a3004d22cc5)](https://www.codacy.com/gh/limoiie/autoserde/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=limoiie/autoserde&amp;utm_campaign=Badge_Grade)

A lightweight non-invasive framework for serialization/deserialization.

AutoSerde relies on [AutoDict](https://github.com/limoiie/autodict.git) to
transform between custom objects and pure builtin objects, and utilizes other
3rd serialization lib (i.e. pyyaml, etc) to transform between builtin
objects and serializations.

## Get started

### Install from the source code

Run following in a shell:

```shell
python -m pip install git+https://github.com/limoiie/autoserde.git
```

### Introduction

A simple example may be like:

```python
from autoserde import serdeable, AutoSerde


@serdeable
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age


student = Student(name='limo', age=90)
student_serialized = AutoSerde.serialize(student, with_cls=False)
assert student_serialized == r'''{"name":"limo",""}'''
```

## Usages

### Mark as serdeable in annotator style

```python
from autoserde import serdeable


@serdeable
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

### Mark as serdeable in derive style

```python
from autoserde import Serdeable


class Student(Serdeable):
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

### Serialize as string

```python
from autoserde import serdeable, AutoSerde


@serdeable
class Student:
    def __init__(self, name, age):
        self.name, self.age = name, age
    ...


student = Student(name='limo', age=90)
student_serialized = AutoSerde.serialize(student, fmt='json')
```

### Serialize/Deserialize to/from path-like

```python
from autoserde import serdeable, AutoSerde


@serdeable
class Student:
    def __init__(self, name, age):
        self.name, self.age = name, age

    ...


student = Student(name='limo', age=90)
student_serialized = AutoSerde.serialize(student, dst='/path/to/x.json')
student_deserialized = AutoSerde.deserialize(src='/path/to/x.json', cls=Student)
```

### Serialize/Deserialize into/from file-like

```python
from autoserde import serdeable, AutoSerde


@serdeable
class Student:
    def __init__(self, name, age):
        self.name, self.age = name, age

    ...


student = Student(name='limo', age=90)
with open('/path/to/x.json', 'w+') as file:
    student_serialized = AutoSerde.serialize(student, dst=file)
    student_deserialized = AutoSerde.deserialize(src=file, cls=Student)
```

### A complex mixin example

```python
import dataclasses
from typing import List

from autoserde import Serdeable, serdeable


@serdeable
@dataclasses.dataclass
class Student:
    name: str
    age: int


@dataclasses.dataclass
class Department(Serdeable):
    students: List[Student]
    location: str


department = Department([
    Student(name='limo', age=90)
], 'The Earth')

fmt = 'json'
department_serialized = department.serialize(fmt=fmt, with_cls=False)
print(department_serialized)
# Output: {"students": [{"name": "limo", "age": 90}], "location": "The Earth"}

department_deserialized = Department.deserialize(body=department_serialized,
                                                 fmt=fmt)
assert department == department_deserialized
```
