#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


setup(
    name="pytempo",
    version="0.0.1a",
    author="Andrew Pashkin",
    author_email="andrew.pashkin@gmx.co.uk",
    license="BSD",
    packages=find_packages(where='src', include=['tempo', 'tempo.*']),
    package_dir={'': 'src'},
    install_requires=[line.strip() for line in open("requirements.txt")],
)
