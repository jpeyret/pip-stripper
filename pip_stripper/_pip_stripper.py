# -*- coding: utf-8 -*-

"""Main module."""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""doc for _main.py - """
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import sys
import argparse
import re
import os

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import set_cpdb, set_rpdb, ppp, debugObject, cpdb

from yaml import safe_load as yload


if __name__ == "__main__":
    set_cpdb(cpdb, remove=True)


class Main(object):
    """ manages batch"""

    di_opt = {}

    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, options):

        self.options = options

        pwd = os.getcwd()
        workdir = self.options.workdir or pwd

        self.config = None

        fnp_config = self.options.config
        if not fnp_config:
            for dn in [workdir, pwd]:
                fnp_config = os.path.join(dn, self.FN_CONFIG)
                try:
                    with open(fnp_config) as fi:
                        self.config = yload(fi)
                        break
                except (IOError,) as e:
                    pass
            else:
                raise ValueError("missing configuration file")

        else:
            with open(fnp_config) as fi:
                self.config = yload(fi)





        ppp(self)





    def process(self):
        try:
            logger.info("process")
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    FN_CONFIG = "pip-stripper.yaml"

    @classmethod
    def getOptParser(cls):

        parser = argparse.ArgumentParser()

        dest="config"
        parser.add_argument(
            "--" + dest,
            action="store",
            help="%s - will look for %s in --workdir, current directory " % (dest, cls.FN_CONFIG)
            )

        dest="scan"
        default=True
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_false",
            help="%s scan python files and classify packages [%s]" % (dest, default)
            )
        
        dest="build"
        default=False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s [%s]" % (dest, default)
            )

        dest="init"
        parser.add_argument(
            "--" + dest,
            action="store_true",
            help="%s initialize the config file if it doesn't exist" % (dest)
            )

        dest="workdir"
        parser.add_argument(
            "--" + dest,
            action="store",
            help="%s [defaults to config's value or current directory]" % (dest)
            )
        
        dest="verbose"
        default=False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s [%s]" % (dest, default)
            )

        
        # use snippet.optadd to expand choices.
        return parser


if __name__ == "__main__":

    set_cpdb(cpdb, remove=True)

    parser = Main.getOptParser()
    options = parser.parse_args()
    mgr = Main(options)
    mgr.process()

