"""
envmgr

Usage:
  envmgr accounts
  envmgr asg schedule <name> (on|off|default|--cron=<expression>) in <env>
  envmgr asg wait-for <name> in <env>
  envmgr get <service> health in <env> [<slice>]
  envmgr get <service> (active|inactive) slice in <env>
  envmgr publish <service> <version> <file>
  envmgr -h | --help
  envmgr --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.

Examples:
  envmgr accounts

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/trainline/envmgr-cli
"""

import sys

from inspect import getmembers, isclass
from docopt import docopt
from . import __version__ as VERSION

def except_hook(exec_type, value, trace_back):
    print(value)

# sys.excepthook = except_hook

def main():
    """Main CLI entrypoint."""
    import envmgr.commands
    options = docopt(__doc__, version=VERSION)

    for (k, v) in options.items(): 
        if hasattr(envmgr.commands, k) and v:
            module = getattr(envmgr.commands, k)
            envmgr.commands = getmembers(module, isclass)
            command = [command[1] for command in envmgr.commands if command[0] != 'BaseCommand'][0]
            command = command(options)
            command.run()

