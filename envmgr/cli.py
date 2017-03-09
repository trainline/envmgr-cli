# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

"""
envmgr

Usage:
    envmgr get <service> health in <env> 
        [<slice>] 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr get <service> (active|inactive) slice in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr get asg <name> status in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr get asg <name> health in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr get asg <name> schedule in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr get deploy status <deploy_id> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr get <cluster> patch status in <env> 
        [--from-ami=<old_ami> --to-ami=<new_ami>] 
        [(--match=<asg>... | --ignore=<asg>... | --whitelist=<file> | --blacklist=<file>)] 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr wait-for deploy <deploy_id> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr wait-for healthy <service> in <env> 
        [<slice>] 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr wait-for asg <name> in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr schedule asg <name> (on|off|default|--cron=<expression>) in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr publish <file> as <service> <version> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr deploy <service> <version> in <env> 
        [<slice>] 
        [--role=<server_role>] 
        [--dry-run] 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr toggle <service> in <env> 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr patch <cluster> in <env> 
        [--from-ami=<old_ami> --to-ami=<new_ami>] 
        [(--match=<asg>... | --ignore=<asg>... | --whitelist=<file> | --blacklist=<file>)] 
        [--kill] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
    envmgr verify
    envmgr -h | --help
    envmgr --version

Options:
    -r --role=<server_role>         Server role for deploying services in multiple roles.
    -f --from-ami=<old_ami>         The AMI Name to update from.
    -t --to-ami=<new_ami>           The AMI Name to update to.
    -m --match=<asg>                Name of an ASG to match when patching (multiple allowed)
    -i --ignore=<asg>               Name of an ASG to ignore when patching (multiple allowed)
    -w --whitelist=<file>           Path to file containing line-separated list of ASG names to match when patching.
    -b --blacklist=<file>           Path to file containing line-separated list of ASG names to ignore when patching.
    -k --kill                       Kills a currently running patch operation.
    -d --dry-run                    Validate a deployment request without actually performing a deployment.
    -h --host=<host_name>           Environment Manager hostname to override environment variable value.
    -u --user=<user_name>           Username to override environment variable value.
    -p --pass=<password>            Password to overide environment variable value.
    -j --json                       Output the raw json response from Environment Manager.
    --help                          Show this screen.
    --version                       Show version.

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
from envmgr.commands import ASG, Deploy, Patch, Publish, Service, Toggle, Verify

commands = {
    'asg':ASG,
    'deploy':Deploy,
    'patch':Patch,
    'publish':Publish,
    'service':Service,
    'toggle':Toggle,
    'verify':Verify
}

def except_hook(exec_type, value, trace_back):
    print(value)

sys.excepthook = except_hook

def main():
    """Main CLI entrypoint."""
    options = docopt(__doc__, version=VERSION)
    priority_order = ["asg", "deploy", "patch", "toggle", "publish", "verify", "service"]
    cmd_opts = options.copy()
    
    if cmd_opts["<service>"] is not None:
        cmd_opts["service"] = True

    for cmd in priority_order:
        if cmd_opts[cmd]:
            CommandClass = commands[cmd]
            command = CommandClass(options)
            command.run()
            return

    print("Unknown command")
