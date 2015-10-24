#!/usr/bin/env python
# coding=utf-8
"""Writes installation SQL script to stdout."""
from os.path import abspath, join, dirname
import sys


def install():
    with open(join(dirname(abspath(__file__)), 'install.sql')) as f:
        sys.stdout.write(f.read())


if __name__ == '__main__':
    install()
