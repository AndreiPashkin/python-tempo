# coding=utf-8
import pytest

from tempo.utils import Enum


class Implementation(Enum):
    """Tested implementations of the library."""
    PYTHON = 'python'
    POSTGRESQL = pytest.mark.xfailifnodb()('postgresql')
