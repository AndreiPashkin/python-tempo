# coding=utf-8
from tempo.unit import DAYS_OF_COMMON_YEAR, DAYS_OF_LEAP_YEAR


def test_days_of_common_year():
    """DAYS_OF_COMMON_YEAR constant consistency."""
    assert len(DAYS_OF_COMMON_YEAR) == 12
    assert sum(DAYS_OF_COMMON_YEAR) == 365
    assert DAYS_OF_COMMON_YEAR[1] == 28


def test_days_of_leap_year():
    """DAYS_OF_LEAP_YEAR constant consistency."""
    assert len(DAYS_OF_LEAP_YEAR) == 12
    assert sum(DAYS_OF_LEAP_YEAR) == 366
    assert DAYS_OF_LEAP_YEAR[1] == 29
