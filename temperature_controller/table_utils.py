import dataclasses
import typing
from PyQt5.QtWidgets import QWidget


@dataclasses.dataclass
class Field:
    """
    Each field defines a column in the the dashboard table.
    """
    key: str
    display_name: str
    value: typing.Any = 0.0
    readonly: bool = True
    widget: typing.Optional[QWidget] = None
    staged_value: typing.Any = None


class DDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
