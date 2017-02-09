"""
envmgr

Usage:
    envmgr get <service> health in <env> [<slice>] [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr get <service> (active|inactive) slice in <env> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr get asg <name> status in <env> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr get deploy status <deploy_id> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr wait-for deploy <deploy_id> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr wait-for healthy <service> in <env> [<slice>] [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr wait-for asg <name> in <env> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr schedule asg <name> (on|off|default|--cron=<expression>) in <env> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr publish <file> as <service> <version> [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr deploy <service> <version> in <env> [<slice>] [--role=<server_role>] [--dry-run] [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr toggle <service> in <env> [--json] [--host=<host_name>] [--user=<user_name> --pass=<password>]
    envmgr -h | --help
    envmgr --version

Options:
    -d --dry-run                Validate a deployment request without actually performing a deployment.
    -r --role=<server_role>     Server role for deploying services in multiple roles.
    -j --json                   Output the raw json response from Environment Manager.
    -h --host=<host_name>       Environment Manager hostname to override environment variable value.
    -u --user=<user_name>       Username to override environment variable value.
    -p --pass=<password>        Password to overide environment variable value.
    --help                      Show this screen.
    --version                   Show version.

Examples:
    envmgr get MyService health in prod-1
    envmgr get MyService active slice in prod-1
    envmgr get asg my-asg status in prod-1
    envmgr schedule asg my-asg on in prod-1
    envmgr wait-for asg my-asg in prod-1

Help:
    For help using this tool, please open an issue on the Github repository:
    https://github.com/trainline/envmgr-cli

    For information on Environment Manager, see the official documentation:
    https://trainline.github.io/environment-manager/
"""

import sys

from inspect import getmembers, isclass
from docopt import docopt
from . import __version__ as VERSION

def except_hook(exec_type, value, trace_back):
    print(value)

sys.excepthook = except_hook

def main():
    """Main CLI entrypoint."""
    import envmgr.commands
    
    options = docopt(__doc__, version=VERSION)
    priority_order = ["asg", "deploy", "toggle", "publish", "service"]
    
    cmd_opts = options.copy()
    if cmd_opts["<service>"] is not None:
        cmd_opts["service"] = True

    for cmd in priority_order:
        if cmd_opts[cmd]:
            module = getattr(envmgr.commands, cmd)
            envmgr.commands = getmembers(module, isclass)
            command = [command[1] for command in envmgr.commands if command[0] != 'BaseCommand'][0]
            command = command(options)
            command.run()
            return

    print("Unknown command")
