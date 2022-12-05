class SerdeError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class NotSerializable(SerdeError):
    def __init__(self, cls):
        super().__init__(
            f'{cls}, please mark it as `:py:func:autoserde.serializable`'
        )


class NotDeserializable(SerdeError):
    def __init__(self, cls):
        super().__init__(
            f'{cls}, please mark it as `:py:func:autoserde.deserializable`'
        )


class UnknownSerdeFormat(SerdeError):
    def __init__(self, fmt):
        super().__init__(
            f'no Format registered in `:py:class:autoserde.SerdeFormat` for'
            f'format {fmt}.'
        )
