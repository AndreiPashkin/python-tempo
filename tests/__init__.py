# coding=utf-8
from tempo.utils import Enum


class Implementation(Enum):
    """Tested implementations of the library."""
    PYTHON = 'python'
    POSTGRESQL = 'postgresql'
