# coding=utf-8
"""General utilities."""
from six import iteritems


class Enum(object):
    @classmethod
    def values(cls):
        for attribute, value in iteritems(cls.__dict__):
            if attribute.startswith('_'):
                continue
            yield value
