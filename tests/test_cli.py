
""" CLI entry point tests """

from subprocess import PIPE, Popen as popen
from unittest import TestCase
from envmgr import __version__ as VERSION

from envmgr import cli

# @patch('environment_manager.EMApi')

class TestCLI(TestCase):

    """
    def test_returns_version_info(self):
        output = popen(['envmgr', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output.strip(), VERSION)
    """

    def test_service_health(self):
        cli.main()
        self.assertEqual(1,2)
