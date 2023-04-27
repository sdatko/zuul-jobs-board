# Zuul Jobs Board

![](https://github.com/sdatko/zuul-jobs-board/workflows/tests/badge.svg)

Neatly presented statuses of periodic Zuul jobs.


## Overview

There are two components of `zjb` – the puller and the server.

The puller periodically fetches the builds and stores results in local cache.

The server displays cached results from the local database (sqlite).


## Installation

```
pip install git+https://github.com/sdatko/zuul-jobs-board.git
```


## Usage

The `zjb` utility is available after the project installation.

```
usage: zjb [-h] [-p] [-s]

Utility to run Zuul Jobs Board processes (puller, server or both).

options:
  -h, --help    show this help message and exit
  -p, --puller  run the puller process
  -s, --server  run the server process
```

An example configuration file `zjb.yml` is provided in this repository.


## Deployment

See files in `deployment/` for Ansible playbook to setup dedicated CentOS host.

It installs ZJB, along with Supervisor service and Nginx proxy for flexibility.

Adjust `inventory.ini`, files and vars, then execute `run.sh` script.


## Development

Dedicated tox environment called **run** can be used for development purposes.

E.g. `tox -e run -- zjb` to launch development version without installation.


## Tests

Call `tox` to run the default test suite in this repository.
