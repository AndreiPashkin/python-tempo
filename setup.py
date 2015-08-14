#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


def read_requirements(filename):
    """Returns requirements specs from file with given 'filename'
    as list."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file]


setup(
    name="python-tempo",
    version="0.0.1a",
    author="Andrew Pashkin",
    author_email="andrew.pashkin@gmx.co.uk",
    license="BSD",
    packages=find_packages(where='src', include=['tempo', 'tempo.*']),
    package_dir={'': 'src'},
    extras_require={
        'postgresql': read_requirements('postgresql-requirements.txt')
    },
    install_requires=read_requirements('requirements.txt'),
)
