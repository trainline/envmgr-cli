# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.12.3] 02-11-2017

### Fixed
- Corrected CLI version info and updated changelog.

## [1.12.2] 02-11-2017

### Changed
- Added `jq` into Docker image.

## [1.12.1] 20-09-2017

### Changed
- `envmgr patch {cluster} in {environment} -m {asg_name}` can now patch Linux AMIs.

### Fixed
- Requesting a JSON response from `toggle` command no longer causes an error.

## [1.11.0] 2017-09-12

### Fixed
- Zero exit code when `wait-for ...` commands time out.

[Unreleased]: https://github.com/trainline/envmgr-cli/compare/1.12.1...HEAD
[1.12.1]: https://github.com/trainline/envmgr-cli/compare/1.11.0...1.12.1
[1.11.0]: https://github.com/trainline/envmgr-cli/compare/1.10.0...1.11.0
