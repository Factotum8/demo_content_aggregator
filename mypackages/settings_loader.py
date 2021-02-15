#!/usr/bin/env python3
# coding=utf-8
"""
There is a loading config helper
"""
import os
import functools
from collections import ChainMap

import yaml

__all__ = ('load_config', )


def remove_prefix(text, prefix):
    # on Python 3.9+ you can use text.removeprefix(prefix)
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def without_prefix(func):
    """
    Remove prefix and convert to lowercase
    """

    @functools.wraps(func)
    def wrapper(*, prefix, path_to_config):
        return {remove_prefix(k, prefix).lower(): v for k, v in func(path_to_config).items()}

    return wrapper


@without_prefix
def load_config(path_to_config=None):
    if path_to_config:
        with open(path_to_config) as f:
            return ChainMap(os.environ, yaml.safe_load(f))
    return ChainMap(os.environ)


if __name__ == '__main__':
    pass
