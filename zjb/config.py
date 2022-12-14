#!/usr/bin/env python3

import errno
import os
import sys

import yaml


def find_config_file() -> str:
    candidate = os.path.join(os.getcwd(), f'{__package__}.yml')
    if os.path.exists(candidate):
        return candidate

    candidate = os.path.join(os.path.expanduser('~'), f'.{__package__}.yml')
    if os.path.exists(candidate):
        return candidate

    candidate = f'{__package__}.yml'
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), candidate)


def load_config_file() -> dict:
    CONFIG_FILE = find_config_file()

    with open(CONFIG_FILE, 'r') as file:
        try:
            return yaml.load(file, Loader=yaml.FullLoader) or {}

        except yaml.YAMLError as exc:
            print('Error in configuration file:', exc)
            sys.exit(1)


CONFIG = load_config_file()

app_port = CONFIG.get('app_port')
db_file = CONFIG.get('db_file')

api_url = CONFIG.get('api_url')
api_tenant = CONFIG.get('api_tenant')

groups = CONFIG.get('groups')
views = CONFIG.get('views')
