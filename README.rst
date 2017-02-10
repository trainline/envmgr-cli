envmgr
======

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

Get service health
^^^^^^^^^^^^^^^^^^

::

    envmgr get AwesomeService health in prod-1

Gets the health status of all instances of *AwesomeService*, in all
slices.

Get service active slice
^^^^^^^^^^^^^^^^^^^^^^^^

::

    envmgr get AwesomeService active slice in prod-1

Gets the the active slice information for the *AwesomeService* service
in *prod-1* environment.

Get ASG status
^^^^^^^^^^^^^^

::

    envmgr get asg my-asg status in prod-1

Gets the status of the *my-asg* ASG in the *prod-1* environment. Status
is calculated as an aggregate of all instances in the ASG.

Get ASG schedule
^^^^^^^^^^^^^^

::

    envmgr get asg my-asg schedule in prod-1

Gets the schedule value set on the  *my-asg* ASG in the *prod-1* environment. Note this will tell you what the schedule is configured to - not the current state according to the schedule.

Get deployment status
^^^^^^^^^^^^^^^^^^^^^

::

    envmgr get deploy status a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994

Gets the current status of the deployment with ID
*a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994*.

Wait for deployment
^^^^^^^^^^^^^^^^^^^

::

    envmgr wait-for deploy a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994

Blocks and waits until the deployment with ID
*a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994* either succeeds or fails.

Wait for ASG
^^^^^^^^^^^^

::

    envmgr wait-for asg my-asg in prod-1

Blocks and waits until all instances in the ASG *my-asg* are ready for
deployment (In Service).

Wait until a service is healthy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    envmgr wait-for healthy AwesomeService in prod-1

Blocks and waits until the service *AwesomeService* is running with all
healthchecks passing.

Schedule ASG state
^^^^^^^^^^^^^^^^^^

::

    envmgr schedule asg my-asg off in prod-1

Sets the schedule of the ASG *my-asg* in *prod-1* to be off permanently
until further notice.

Publish a new build
^^^^^^^^^^^^^^^^^^^

::

    envmgr publish build-22.zip as AwesomeService 1.2.9 

Publish the file *build-22.zip* as version *1.2.9* of *AwesomeService*.

Deploy a service
^^^^^^^^^^^^^^^^

::

    envmgr deploy AwesomeService 1.2.9 in prod-1

Deploy the published version *1.2.9* of *AwesomeService* into the
*prod-1* environment.

Toggle a service
^^^^^^^^^^^^^^^^

::

    envmgr toggle AwesomeService in prod-1

Toggle the upstreams for *AwesomeService* in the *prod-1* environment.

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

    ENVMGR_HOST=environmentmanager.corp.local

Or provide the hostname with each command:

::

    envmgr get MyService health in prod --host=environmentmanager.acme.com
