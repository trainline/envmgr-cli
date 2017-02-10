""" Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information. """

from setuptools import find_packages, setup
from codecs import open
from os.path import abspath, dirname, join
from envmgr import __version__

this_dir = abspath(dirname(__file__))

with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

setup(
    name = 'envmgr-cli',
    version = __version__,
    description = 'Environment Manager CLI tool.',
    long_description = long_description,
    url = 'https://github.com/trainline/envmgr-cli',
    author = 'Trainline Platform Development',
    author_email = 'platform.development@thetrainline.com',
    license = 'Apache 2.0',
    packages = find_packages(),
    install_requires = [
        'docopt',
        'requests',
        'simplejson',
        'environment_manager==0.0.9'
    ],
    entry_points = {
        'console_scripts': [
            'envmgr=envmgr.cli:main',
        ],
    },
)

