# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


NAME = 'sculpt'
DESCRIPTION = 'Library for imperative definition of object transformations and validation.'
VERSION = '0.0.1'
AUTHOR = 'Stas Kazhavets'
EMAIL = 'staskozhevets@gmail.com'


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages(include=('sculpt', 'sculpt.*')),
    install_requires=[
        'PyYAML>=3.12',
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
