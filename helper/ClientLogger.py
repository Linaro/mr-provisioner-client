#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Verbosity levels
    https://pypi.org/project/verboselogs/#overview-of-logging-levels

    Useful levels:
    DEBUG  10       -vv
    INFO  20        -v

    The following two we don't want to filter:
    WARNING  30
    ERROR  40
    CRITICAL  50
"""

import logging
import coloredlogs

class ClientLogger(object):
    def __init__(self, name, parser, verbosity):
        self.logger = logging.getLogger(name)

        # Default level is WARNING (no output other than warnings and errors)
        start = 30
        silent = min(verbosity*10, 20)
        coloredlogs.install(level=start-silent, logger=self.logger)
        self.parser = parser

    def fatal(self, err):
        self.logger.fatal(err, exc_info=True)

    def error(self, err, print_help=False):
        self.logger.error(err)
        if print_help:
            print('\n\n')
            self.parser.print_help()

    def warning(self, warning):
        self.logger.warning(warning)

    def info(self, info):
        self.logger.info(info)

    def debug(self, trace):
        self.logger.debug(trace)

    def silent(self):
        return self.logger.getEffectiveLevel() > logging.INFO
