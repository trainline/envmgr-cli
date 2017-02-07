# envmgr

A cross-platform CLI client for [Environment Manager](https://github.com/trainline/environment-manager)


## Usage

All `envmgr` actions are exposed behind a set of verbs (_get_ a status, _schedule_ some downtime, _wait_ for an ASG to scale up.)


#### Output

By default, `envmgr` commands will output a human friendly response useful for testing single commands at a time. To help scripting or chaining results together, all commands also accept a `--json` argument which will return the raw JSON response from Environment Manager.

## Examples

Publishing a service:

```
envmgr publish build-022.zip as AwesomeService 1.0.4
```

Deploying a service:

```
envmgr deploy AwesomeService 1.0.4 in prod-1
```

Get the health of a service:

```
envmgr get AwesomeService health in prod-1
```

Get service slice information

```
envmgr get AwesomeService active slice in prod-1
```

Get ASG status

```
envmgr get my-asg status in prod-1
```

# envmgr

A cross-platform CLI client for [Environment Manager](https://github.com/trainline/environment-manager)


## Install
```
pip install envmgr
```


## Usage

`envmgr` is designed to provide an intuitive, human readable interface around the lower level [Environment Manager Python Library](https://github.com/trainline/python-environment_manager/)

All `envmgr` commands are exposed behind a set of verbs (_get_ a status, _schedule_ some downtime, _wait_ for an ASG to scale up, etc). Verbs are always the first value provided to `envmgr` and there is only ever one verb per command.

#### Authentication  

All calls to Environment Manager require authentication, which can be provided in 1 of 2 ways.

1. Export the following environment variables with your credentials:

	```
	ENVMGR_USER=myusername
	ENVMGR_PASS=mypa$$word
	```
2. Or provide a `--user` and `--pass` value with each command:

	```
    envmgr get MyService health in prod --user="sarah" --pass="pa$$word"
    ```

	_Note: It's recommended to only use this method in CI environments._


#### Host Config

The hostname of your Environment Manager instance is configured similarly to your credentials:

1. Export the hostname:

	```
	ENVMGR_HOST=environmentmanager.corp.local
	```
2. Or provide it with each command:
	```
    envmgr get MyService health in prod --host=environmentmanager.acme.com
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

Publishing a service:

```
envmgr publish build-022.zip as AwesomeService 1.0.4
```

Deploying a service:

```
envmgr deploy AwesomeService 1.0.4 in prod-1
```

Get the health of a service:

```
envmgr get AwesomeService health in prod-1
```

Get service slice information

```
envmgr get AwesomeService active slice in prod-1
```

Get ASG status

```
envmgr get my-asg status in prod-1
```

