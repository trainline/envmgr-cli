"""
envmgr

Usage:
  envmgr asg schedule <name> (on|off|default|--cron=<expression>) in <env> [--json]
  envmgr asg get <name> status in <env> [--json]
  envmgr asg wait-for <name> in <env> [--json]
  envmgr get <service> health in <env> [<slice>] [--json]
  envmgr get <service> (active|inactive) slice in <env> [--json]
  envmgr publish <service> <version> <file>
  envmgr deploy <service> <version> in <env> [<slice>] [--role=<server_role>] [--dry-run] [--json]
  envmgr -h | --help
  envmgr --version

Options:
  -d --dry-run      Validate a deployment request without actually performing a deployment
  -j --json         Output the raw json response from Environment Manager
  -h --help         Show this screen.
  --version         Show version.

Examples:
  envmgr asg schedule my-asg on in prod-1
  envmgr asg wait-for my-asg in prod-1
  envmgr get MyService health in stage-2

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
    priority_order = ["asg", "get", "deploy", "publish"]

    for cmd in priority_order:
        if options[cmd]:
            module = getattr(envmgr.commands, cmd)
            envmgr.commands = getmembers(module, isclass)
            command = [command[1] for command in envmgr.commands if command[0] != 'BaseCommand'][0]
            command = command(options)
            command.run()
            return
