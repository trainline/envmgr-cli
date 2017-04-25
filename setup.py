""" Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information. """

import sys

from setuptools import find_packages, setup
from codecs import open
from os.path import abspath, dirname, join
from emcli import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest-runner', 'nose'] if needs_pytest else []

setup(
    name = 'envmgr-cli',
    version = __version__,
    description = 'Environment Manager CLI tool.',
    long_description = long_description,
    url = 'https://github.com/trainline/envmgr-cli',
    author = 'Trainline Platform Development',
    author_email = 'platform.development@thetrainline.com',
    license = 'Apache 2.0',
    packages = find_packages(exclude=['tests*']),
    install_requires = [
        'docopt',
        'simplejson',
        'tabulate',
        'future',
        'semver',
        'appdirs',
        'progressbar2',
        'envmgr-lib==0.2.1'
    ],
    setup_requires = pytest_runner,
    tests_require = [
        'pytest',
        'mock',
        'nose',
        'nose-parameterized',
        'responses'
    ],
    entry_points = {
        'console_scripts': [
            'envmgr=emcli.cli:main',
        ],
    },
)

