import dataclasses
from typing import Any, Tuple, Union


@dataclasses.dataclass
class Raises:
    exc: Union[Any, Tuple[Any, ...]]
    kwargs: dict = dataclasses.field(default_factory=dict)
