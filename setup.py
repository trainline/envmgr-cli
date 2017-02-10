""" Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information. """

from setuptools import Command, find_packages, setup
from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from envmgr import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):

    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('is it running')
        errno = call(['py.test', '--cov=envmgr', '--cov-report=term-missing'])
        #raise SystemExit(errno)


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
        'requests',
        'simplejson',
        'environment_manager==0.0.9'
    ],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov']
    },
    entry_points = {
        'console_scripts': [
            'envmgr=envmgr.cli:main',
        ],
    },
    cmdclass = {'test':RunTests},
)

