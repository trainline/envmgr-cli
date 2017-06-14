# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

"""
envmgr

Usage:
    envmgr get <service> health in <env> 
        [<slice>] 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get <service> (active|inactive) slice in <env> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr check asg <name> exists in <env> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get asg <name> status in <env> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get asg <name> schedule in <env> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get asg <name> health in <env> 
        [(--json | --ci-mode)] 
        [--json] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get deploy status <deploy_id> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get <cluster> patch status in <env> 
        [--from-ami=<old_ami> --to-ami=<new_ami>] 
        [(--match=<asg>... | --ignore=<asg>... | --whitelist=<file> | --blacklist=<file>)] 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get instances out of date by <age> days
        [--env=<env>]
        [--cluster=<cluster>]
        [--account=<account>]
        [--sort=(age|ami_age|ami_name|env|type|cluster|role|state)]
        [--report] 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get upstream status for <slice> <service> in <env> 
        [--upstream=<upstream>]
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr wait-for deploy <deploy_id> 
        [--timeout=<timeout>]
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr wait-for healthy <service> in <env> 
        [<slice>]
        [--timeout=<timeout>]
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr wait-for asg <name> in <env> 
        [--timeout=<timeout>]
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr wait-for toggle to <slice> <service> in <env> 
        [--upstream=<upstream>]
        [--timeout=<timeout>]
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr set asg <name> schedule (on|off|default|--cron=<expression>) in <env> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr publish <file> as <service> <version> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr deploy <service> <version> in <env> 
        [<slice>] 
        [--role=<server_role>] 
        [--dry-run] 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr toggle <service> in <env> 
        [(--json | --ci-mode)] 
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr patch <cluster> in <env> 
        [--from-ami=<old_ami> --to-ami=<new_ami>] 
        [(--match=<asg>... | --ignore=<asg>... | --whitelist=<file> | --blacklist=<file>)] 
        [--kill] 
        [(--json | --ci-mode)]
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr cycle <cluster> asgs in <env>
        [(--match=<asg>... | --ignore=<asg>... | --whitelist=<file> | --blacklist=<file>)] 
        [--kill] 
        [(--json | --ci-mode)]
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr get <cluster> asg cycle status in <env>
        [(--match=<asg>... | --ignore=<asg>... | --whitelist=<file> | --blacklist=<file>)] 
        [--kill] 
        [(--json | --ci-mode)]
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr verify
        [(--json | --ci-mode)]
        [--host=<host_name>] 
        [--user=<user_name> --pass=<password>]
        [--verbose]
    envmgr --help
    envmgr --version

Options:
    -r --role=<server_role>         Server role for deploying services in multiple roles.
    -f --from-ami=<old_ami>         The AMI Name to update from.
    -t --to-ami=<new_ami>           The AMI Name to update to.
    -m --match=<asg>                Name of an ASG to match when patching (multiple allowed)
    -i --ignore=<asg>               Name of an ASG to ignore when patching (multiple allowed)
    -w --whitelist=<file>           Path to file containing line-separated list of ASG names to match when patching.
    -b --blacklist=<file>           Path to file containing line-separated list of ASG names to ignore when patching.
    -s --sort=<key>                 Sort the results by the given key
    -l --upstream=<upstream>        The name of the upstream to check
    -x --timeout=<timeout>          Maximum number of seconds permitted in a wait-for operation
    -o --report                     Save a report to the current directory
    -k --kill                       Kills a currently running patch operation.
    -d --dry-run                    Validate a deployment request without actually performing a deployment.
    -h --host=<host_name>           Environment Manager hostname to override environment variable value.
    -u --user=<user_name>           Username to override environment variable value.
    -p --pass=<password>            Password to override environment variable value.
    -j --json                       Output the raw json response from Environment Manager.
    -v --verbose                    Output verbose logging straight to stdout instead of logfile
    -c --ci-mode                    Only provide output that is safe for Contiuous Integration environments.
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

import os
import sys
import logging
import traceback

from inspect import getmembers, isclass
from appdirs import user_log_dir
from docopt import docopt
from . import __version__ as VERSION
from emcli.commands import AsgCommand, DeployCommand, PublishCommand, ServiceCommand, ToggleCommand, VerifyCommand, InstanceCommand, PatchCommand, CycleCommand
from emcli.commands.utils.file_utils import safe_create_dir_path

commands = {
        'asg':AsgCommand,
        'instances':InstanceCommand,
        'deploy':DeployCommand,
        'patch':PatchCommand,
        'cycle':CycleCommand,
        'publish':PublishCommand,
        'service':ServiceCommand,
        'toggle':ToggleCommand,
        'upstream':ToggleCommand,
        'verify':VerifyCommand
        }

def setup_logger(verbose):
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        log_dir = user_log_dir('envmgr', 'trainline')
        log_file = os.path.join(log_dir, 'envmgr.log')
        safe_create_dir_path(log_file)
        logging.basicConfig(filename=log_file, level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

def except_hook(exc_type, value, trace_back):
    print('\r{0}'.format(value))
    if not issubclass(exc_type, KeyboardInterrupt):
        text = "".join(traceback.format_exception(exc_type, value, trace_back))
        logging.error("Unhandled exception: %s", text)

sys.excepthook = except_hook

def main():
    """Main CLI entrypoint."""
    options = docopt(__doc__, version=VERSION)
    setup_logger(options.get('--verbose', False))
    priority_order = ["cycle", "asg", "instances", "deploy", "patch", "toggle", "upstream", "publish", "verify", "service"]
    cmd_opts = options.copy()

    if cmd_opts["<service>"] is not None:
        cmd_opts["service"] = True

    for cmd in priority_order:
        if cmd_opts[cmd]:
            logging.info('Running {0} command'.format(cmd))
            CommandClass = commands[cmd]
            command = CommandClass(options)
            command.run()
            return

    print("Unknown command")
