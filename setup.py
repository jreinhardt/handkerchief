#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open
from os import path, listdir

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='handkerchief',
    version=0.3,
    packages=find_packages(),
    include_package_data=True,
    description='simple offline issue reader for GitHub Issues',
    long_description=long_description,
    install_requires=['Jinja2','requests'],
    author="Johannes Reinhardt",
    author_email="jreinhardt@ist-dein-freund.de",
    license="MIT",
    keywords=["github","issues","offline"],
    url="https://github.com/jreinhardt/handkerchief",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7"
        "Programming Language :: Python :: 3.4"
    ],
    entry_points={
        'console_scripts': ['handkerchief = handkerchief.handkerchief:main']
    }
)

