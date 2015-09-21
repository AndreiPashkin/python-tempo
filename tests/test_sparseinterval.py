# coding=utf-8
import pytest

from tempo.sparseinterval import SparseInterval


@pytest.mark.parametrize('ranges1, ranges2, expected', [
    ([(1, 5), (10, 15)], [(50, 55), (60, 65)],
     [(1, 5), (10, 15), (50, 55), (60, 65)]),
    ([(1, 10), (15, 30)], [(5, 15), (20, 60)],
     [(1, 60)]),
    ([(1, 10), (15, 30)], [(5, 25)],
     [(1, 30)]),
    ([(5, 5)], [(10, 15)],
     [(10, 15)]),
    ([], [(10, 15)],
     [(10, 15)]),
])
def test_union(ranges1, ranges2, expected):
    """Union cases."""
    interval1 = SparseInterval(*ranges1)
    interval2 = SparseInterval(*ranges2)

    actual = interval1.union(interval2)
    expected = SparseInterval(*expected)

    assert actual == expected


@pytest.mark.parametrize('ranges1, ranges2, expected', [
    ([(1, 20), (40, 60)], [(15, 25), (30, 50)],
     [(15, 20), (40, 50)]),
    ([(1, 20), (40, 60)], [(10, 50)],
     [(10, 20), (40, 50)]),
    ([(1, 20), (40, 60)], [(70, 80), (90, 100)],
     []),
    ([(1, 20), (40, 60)], [],
     []),
    ([(1, 20), (40, 60)], [(5, 5)],
     []),
])
def test_intersection(ranges1, ranges2, expected):
    """Intersection cases."""
    interval1 = SparseInterval(*ranges1)
    interval2 = SparseInterval(*ranges2)

    actual = interval1.intersection(interval2)
    expected = SparseInterval(*expected)

    assert actual == expected


@pytest.mark.parametrize('ranges1, ranges2, expected', [
    ([(1, 20), (40, 60)], [(15, 25), (30, 50)],
     [(1, 15), (50, 60)]),
    ([(1, 20), (40, 60)], [(10, 50)],
     [(1, 10), (50, 60)]),
    ([(1, 20), (40, 60)], [(25, 30), (65, 70)],
     [(1, 20), (40, 60)]),
    ([(1, 20), (40, 60)], [],
     [(1, 20), (40, 60)]),
    ([(1, 20), (40, 60)], [(5, 5)],
     [(1, 20), (40, 60)]),
])
def test_difference(ranges1, ranges2, expected):
    """Difference cases."""
    interval1 = SparseInterval(*ranges1)
    interval2 = SparseInterval(*ranges2)

    actual = interval1.difference(interval2)
    expected = SparseInterval(*expected)

    assert actual == expected
