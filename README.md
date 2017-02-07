# envmgr

A cross-platform CLI client for [Environment Manager](https://github.com/trainline/environment-manager)

## Install
```
pip install envmgr
```

## Usage

_envmgr_ is designed to provide an intuitive, human readable interface around the lower level [Environment Manager Python Library](https://github.com/trainline/python-environment_manager/)

All `envmgr` commands are exposed behind a set of verbs (_get_ a status, _schedule_ some downtime, _wait_ for an ASG, etc). Verbs are always the first value provided to `envmgr` and there is only ever one verb per command.

### docopt  

The cli interface is described in [docopt](http://docopt.org/]). The easiest way to discover and understand the different usage patterns available is to simply run 

```
envmgr --help
```

### Output  

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


### Get service health

```
envmgr get AwesomeService health in prod-1
```

### Get service active slice

```
envmgr get AwesomeService active slice in prod-1
```

### Get ASG status

```
envmgr get asg my-asg status in prod-1
```

### Get deployment status

```
envmgr get deploy status a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994
```

### Wait for deployment

```
envmgr wait-for deploy a2fbb0c0-ed4c-11e6-85b1-2b6d1cb68994
```

### Wait for ASG

```
envmgr wait-for asg my-asg in prod-1
```

### Schedule ASG state

```
envmgr schedule asg my-asg off in prod-1
```

### Publish a new build

```
envmgr publish build-22.zip as AwesomeService 1.2.9 
```

### Deploy a service

```
envmgr deploy AwesomeService 1.2.9 in prod-1
```


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


