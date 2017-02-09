# envmgr

A cross-platform CLI client for [Environment Manager](https://github.com/trainline/environment-manager)

![envmgr example](/example.gif)

## Install
```
pip install envmgr-cli
```
_See [Configuration](#configuration) for further install instructions._

## Usage

_envmgr_ is designed to provide an intuitive, human readable interface around the lower level [Environment Manager Python Library](https://github.com/trainline/python-environment_manager/)

All `envmgr` commands are exposed behind a set of verbs (_get_ a status, _schedule_ some downtime, _wait_ for an ASG, etc). Verbs are always the first value provided to `envmgr` and there is only ever one verb per command.

#### docopt  

The cli interface is described in [docopt](http://docopt.org/]). The easiest way to discover and understand the different usage patterns available is to simply run 

```
envmgr --help
```

#### Output  

By default, `envmgr` commands will output a human friendly response useful for testing single commands at a time. To help scripting or chaining results together, all commands also accept a `--json` argument which will return the raw JSON response from Environment Manager:

```
>> envmgr schedule asg my-asg on in prod
Scheduled 1 instance in my-asg to: ON

>> envmgr schedule asg my-asg on in prod --json
{"ChangedInstances": ["i-0afe2276909859130"], "ChangedAutoScalingGroups": ["my-asg"]}
```


## Examples

_Note: The examples below omit options for `--json` described above, as well as `--host`, `--user` and `--pass` as these are globally available to all commands (see [configuration](#configuration))_

_Assume that `prod-1` is an environment, `AwesomeService` is a service and `my-asg` is an ASG, all of which are already registered in Environment Manager._


#### Get service health

```
envmgr get AwesomeService health in prod-1
```
Gets the health status of all instances of _AwesomeService_, in all slices.  

#### Get service active slice

```
envmgr get AwesomeService active slice in prod-1
```
Gets the the active slice information for the _AwesomeService_ service in _prod-1_ environment.


#### Get ASG status

```
envmgr get asg my-asg status in prod-1
```
Gets the status of the _my-asg_ ASG in the _prod-1_ environment. Status is calculated as an aggregate of all instances in the ASG.


#### Get deployment status

```
envmgr get deploy status a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994
```
Gets the current status of the deployment with ID _a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994_.


#### Wait for deployment

```
envmgr wait-for deploy a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994
```
Blocks and waits until the deployment with ID _a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994_ either succeeds or fails.


#### Wait for ASG

```
envmgr wait-for asg my-asg in prod-1
```
Blocks and waits until all instances in the ASG _my-asg_ are ready for deployment (In Service).


#### Wait until a service is healthy

```
envmgr wait-for healthy AwesomeService in prod-1
```
Blocks and waits until the service _AwesomeService_ is running with all healthchecks passing.


#### Schedule ASG state

```
envmgr schedule asg my-asg off in prod-1
```
Sets the schedule of the ASG _my-asg_ in _prod-1_ to be off permanently until further notice.


#### Publish a new build

```
envmgr publish build-22.zip as AwesomeService 1.2.9 
```
Publish the file _build-22.zip_ as version _1.2.9_ of _AwesomeService_.


#### Deploy a service

```
envmgr deploy AwesomeService 1.2.9 in prod-1
```
Deploy the published version _1.2.9_ of _AwesomeService_ into the _prod-1_ environment.


#### Toggle a service

```
envmgr toggle AwesomeService in prod-1
```
Toggle the upstreams for _AwesomeService_ in the _prod-1_ environment.


## Configuration


#### Authentication  

All calls to Environment Manager require authentication, which can be provided in 1 of 2 ways.

Either export your credentials as environment variables:

```
ENVMGR_USER=myusername
ENVMGR_PASS=mypa$$word
```
Or provide a `--user` and `--pass` value to each commad:

```
envmgr get MyService health in prod --user="sarah" --pass="pa$$word"
```

_Note: It's recommended to only use this method in CI environments._


#### Host Config

The hostname of your Environment Manager instance is configured similarly to your credentials:

Export your hostname as an environment variable:

```
ENVMGR_HOST=environmentmanager.corp.local
```

Or provide the hostname with each command:

```
envmgr get MyService health in prod --host=environmentmanager.acme.com
```

