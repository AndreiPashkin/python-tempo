#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


setup(
    name="pytempo",
    version="0.0.1a",
    author="Andrew Pashkin",
    author_email="andrew.pashkin@gmx.co.uk",
    license="BSD",
    packages=find_packages(include=['tempo', 'tempo.*']),
    package_data={
        'tempo.django': ['static/tempo/*.css', 'static/tempo/*.js']
    },
    install_requires=[line.strip() for line in open("requirements.txt")],
    dependency_links=[line.strip() for line in open("dependency-links.txt")],
)
