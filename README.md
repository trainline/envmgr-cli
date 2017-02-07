# envmgr

A cross-platform CLI client for [Environment Manager](https://github.com/trainline/environment-manager  )


## Usage


// Todo


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

