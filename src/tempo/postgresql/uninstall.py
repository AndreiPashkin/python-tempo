#!/usr/bin/env python
# coding=utf-8
"""Writes uninstallation SQL script to stdout."""
from os.path import abspath, join, dirname
import sys


def uninstall():
    with open(join(dirname(abspath(__file__)), 'uninstall.sql')) as f:
        sys.stdout.write(f.read())


if __name__ == '__main__':
    uninstall()
