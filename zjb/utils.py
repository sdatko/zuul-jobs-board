#!/usr/bin/env python3

import re


def match(string: str, specifier: str) -> bool:
    '''Function checks if a given string is matched by a given specifier.

    The match is performed in the awk-inspired fashion:
    – if the specifier starts and ends with the forward slash (/), e.g. /foo/,
      then the content between slashes is treated as regular expression,
    – otherwise it is a value that should fully match the input string.

    Parameters
    ----------
    string : str
        The string that should be tested against specifier.
    specifier : str
        The expected value or regular expression to be matched against.

    Returns
    -------
    matched : bool
        True if given string matches the specifier, False otherwise.

    Examples
    --------
    >>> match('foobar', 'foobar')
    True
    >>> match('foobar', 'foo')
    False
    >>> match('foobar', '/foo/')
    True
    '''

    if specifier.startswith('/') and specifier.endswith('/'):
        regex = re.compile(specifier[1:-2])
        return bool(regex.search(string))
    else:
        regex = re.compile(specifier)
        return bool(regex.fullmatch(string))


def progress(current: int = 0, total: int = 100):
    length = 40
    boxes = int(current / total * length) * '#'
    togo = (length - len(boxes)) * '-'

    print(f'\r[{boxes}{togo}] {current}/{total}', end='')

    if current >= total:
        print()
