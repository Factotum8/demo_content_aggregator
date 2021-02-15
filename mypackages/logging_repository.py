#!/usr/bin/env python3
# coding=utf-8
"""
Toolkit for get ip address, logging, extra dict
"""
import sys
import socket
import logging
from pathlib import Path

import logstash

__all__ = ("get_host_ip", "LoggingRepository")


def get_host_ip(dst=None, port=None):
    """
    Get own ip address
    """
    dst = dst or '8.8.8.8'
    port = port or 80
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((dst, port))
            return s.getsockname()[0]

    except Exception:
        return 'unknown' if dst == '8.8.8.8' else get_host_ip()


class LoggingRepository:

    def __init__(self, extra: dict, ping_host=None, ping_port=None, config: dict = None):
        self._extra = {'host': get_host_ip(ping_host, ping_port), **extra}
        if config:
            self.log = LoggingRepository.get_log_handler(config)
        else:
            logging.basicConfig(
                format=u'%(asctime)s#%(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s',
                level=logging.INFO
            )
            self.log = logging

    @classmethod
    def get_log_handler(cls, config: dict):
        """
        This method initializes log object.
        First handler always write to console.
        Second handler may write to file or elastic stack
        :param config:
        :return: log object
        """
        try:
            handlers = []
            log = None

            if config['log_handler'] == 'file':
                # create the logging file handler
                try:
                    Path(config['path_to_log']).resolve().parents[1].mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    pass

                log = logging.getLogger(f"{__name__}-python-file-logger")

                log_handler_ = logging.FileHandler(
                    filename=config['path_to_log'], encoding=None, delay=False
                )
                format_str = u'%(asctime)s#%(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s'
                format_obj = logging.Formatter(format_str)
                log_handler_.setFormatter(format_obj)
                handlers.append(log_handler_)

            elif config['log_handler'] in ('stash', 'logstash'):
                # create the logging logstash handler
                log = logging.getLogger(f'{__name__}-python-logstash-logger')
                log_handler = logstash.TCPLogstashHandler(host=config['logging_logstash_host'],
                                                          port=config['logging_logstash_port'],
                                                          version=1)
                handlers.append(log_handler)

            # always write to console
            log = log or logging.getLogger(f'{__name__}-python-stdout-logger')
            log_handler = logging.StreamHandler(sys.stdout)
            format_str = u'%(asctime)s#%(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s'
            format_obj = logging.Formatter(format_str)
            log_handler.setFormatter(format_obj)
            handlers.append(log_handler)

            # example self.log.setLevel(logging.WARNING)
            log.setLevel(config['logging_level'].upper())

            list(map(log.addHandler, handlers))  # Added all handlers to logger

            return log

        except KeyError as e:
            raise KeyError(f"Specify necessary environment variable {e}")

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, val: dict):
        self._extra = val

    def mixin_extra(self, expansions: dict) -> dict:
        """
        Return union extra and expansions dict
        :param expansions: dict
        :return: dict
        """
        return {**self._extra, **expansions}  # expansions overwrites


if __name__ == '__main__':
    pass
