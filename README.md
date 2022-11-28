# AutoSerde

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
student_serialized = AutoSerde.serialize(student, fp='/path/to/x.json')
student_deserialized = AutoSerde.deserialize(fp='/path/to/x.json', cls=Student)
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
    student_serialized = AutoSerde.serialize(student, fp=file)
    student_deserialized = AutoSerde.deserialize(fp=file, cls=Student)
```
