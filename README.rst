envmgr |pypi| |travis| |appveyor| |dockerautomated| |dockerpulls|
=================================================================

A cross-platform CLI client for `Environment
Manager <https://github.com/trainline/environment-manager>`__

.. figure:: https://github.com/trainline/envmgr-cli/raw/master/example.gif
   :alt: envmgr example


Install
-------

::

    pip install envmgr-cli


See `Configuration`_ for further install instructions.


Usage
-----

*envmgr* is designed to provide an intuitive, human readable interface
around the lower level `Environment Manager Python
Library <https://github.com/trainline/python-environment_manager/>`__

All ``envmgr`` commands are exposed behind a set of verbs (*get* a
status, *schedule* some downtime, *wait* for an ASG, etc). Verbs are
always the first value provided to ``envmgr`` and there is only ever one
verb per command.

docopt
^^^^^^

The cli interface is described in `docopt <http://docopt.org/%5D>`__.
The easiest way to discover and understand the different usage patterns
available is to simply run

::

    envmgr --help

Output
^^^^^^

By default, ``envmgr`` commands will output a human friendly response
useful for testing single commands at a time. To help scripting or
chaining results together, all commands also accept a ``--json``
argument which will return the raw JSON response from Environment
Manager:

::

    >> envmgr schedule asg my-asg on in prod
    Scheduled 1 instance in my-asg to: ON

    >> envmgr schedule asg my-asg on in prod --json
    {"ChangedInstances": ["i-0afe2276909859130"], "ChangedAutoScalingGroups": ["my-asg"]}

Examples
--------

*In the examples below, assume that 'prod-1' is an environment, 'AwesomeService' is a
service and 'my-asg' is an ASG, all of which are already registered in
Environment Manager.*

.. code-block:: bash

    # Get the health status of all instances of AwesomeService, in all slices:
    envmgr get AwesomeService health in prod-1

    # Get the the active slice information for the AwesomeService service in prod-1 environment:
    envmgr get AwesomeService active slice in prod-1

    # Get the status of the my-asg ASG in the prod-1 environment. Status is calculated as an aggregate of all instances in the ASG:
    envmgr get asg my-asg status in prod-1

    # Get the schedule value set on the my-asg ASG in the prod-1 environment. Note this will tell you what the schedule is configured to - not the current state according to the schedule:
    envmgr get asg my-asg schedule in prod-1

    # Get the current status of the deployment with ID a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994:
    envmgr get deploy status a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994

    # Block and wait until the deployment with ID a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994 either succeeds or fails:
    envmgr wait-for deploy a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994

    # Block and wait until all instances in the ASG my-asg are ready fordeployment (In Service):
    envmgr wait-for asg my-asg in prod-1

    # Block and wait until the service AwesomeService is running with all healthchecks passing:
    envmgr wait-for healthy AwesomeService in prod-1

    # Set the schedule of the ASG my-asg in prod-1 to be off permanently until further notice:
    envmgr schedule asg my-asg off in prod-1

    # Publish the file build-22.zip as version 1.2.9 of AwesomeService:
    envmgr publish build-22.zip as AwesomeService 1.2.9

    # Deploy the published version 1.2.9 of AwesomeService into the prod-1 environment:
    envmgr deploy AwesomeService 1.2.9 in prod-1

    # Toggle the upstreams for AwesomeService in the prod-1 environment:
    envmgr toggle AwesomeService in prod-1

    # Get the Windows patch status for servers belonging to A-Team in prod-1:
    envmgr get A-team patch status in prod-1



Configuration
-------------

Authentication
^^^^^^^^^^^^^^

All calls to Environment Manager require authentication, which can be
provided in 1 of 2 ways.

Either export your credentials as environment variables:

::

    ENVMGR_USER=myusername
    ENVMGR_PASS=mypa$$word

Or provide a ``--user`` and ``--pass`` value to each commad:

::

    envmgr get MyService health in prod --user="sarah" --pass="pa$$word"

*Note: It's recommended to only use this method in CI environments.*

Host Config
^^^^^^^^^^^

The hostname of your Environment Manager instance is configured
similarly to your credentials:

Export your hostname as an environment variable:

::

    ENVMGR_HOST=environmentmanager.acme.com

Or provide the hostname with each command:

::

    envmgr get MyService health in prod --host=environmentmanager.acme.com


Development
-----------
To install all test dependencies and run all tests, simply run:

::

    python setup.py test [--adopts -v]


For convenience this is also available via the included `makefile`:

::

    make test


Docker
------

If you want, you can use our automated container builds

Usage
^^^^^

::

    docker run -it --rm \
    -e ENVMGR_USER=user
    -e ENVMGR_PASS=password
    -e ENVMGR_HOST=foo.bar
    trainline/envmgr-cli:latest envmgr {YOUR_ARGS}


Example
^^^^^^^

::

    ~$ docker run -it --rm trainline/envmgr-cli envmgr --version
    1.9.1


Build
^^^^^

::

    docker build -t {YOUR_NAME}/envmgr-cli .


.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/w50g5yb1fh4qh3rq/branch/master?svg=true
    :target: https://ci.appveyor.com/project/duncanhall/envmgr-cli/branch/master

.. |travis| image:: https://travis-ci.org/trainline/envmgr-cli.svg?branch=master
    :target: https://travis-ci.org/trainline/envmgr-cli

.. |pypi| image:: https://img.shields.io/badge/python-2.7%2C%203.4%2C%203.5%2C%203.6-blue.svg
    :target: https://pypi.python.org/pypi/envmgr-cli

.. |dockerautomated| image:: https://img.shields.io/docker/automated/trainline/envmgr-cli.svg
    :target: https://hub.docker.com/r/trainline/envmgr-cli

.. |dockerpulls| image:: https://img.shields.io/docker/pulls/trainline/envmgr-cli.svg
    :target: https://hub.docker.com/r/trainline/envmgr-cli
