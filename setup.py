#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development :: Libraries',
    'Topic :: Database',
    'Topic :: Utilities',
]


def read_requirements(filename):
    """Returns requirements specs from file with given 'filename'
    as list."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file]


setup(
    name="python-tempo",
    version="0.1.0dev0",
    author="Andrew Pashkin",
    author_email="andrew.pashkin@gmx.co.uk",
    license="BSD",
    url='https://github.com/AndrewPashkin/python-tempo/',
    classifiers=CLASSIFIERS,
    packages=find_packages(where='src', include=['tempo', 'tempo.*']),
    package_dir={'': 'src'},
    extras_require={
        'postgresql': read_requirements('postgresql-requirements.txt')
    },
    install_requires=read_requirements('requirements.txt'),
    package_data= {
        'tempo.postgresql': ['*.sql']
    },
    entry_points={
        'console_scripts': [
            'tempo-postgresql-install = tempo.postgresql.install:install',
            'tempo-postgresql-uninstall = tempo.postgresql.uninstall:uninstall'
        ]
    }
)
