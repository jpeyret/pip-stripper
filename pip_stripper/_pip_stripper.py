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
import subprocess

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import set_cpdb, set_rpdb, ppp, debugObject, cpdb, fill_template, rpdb, sub_template

from yaml import safe_load as yload, dump



if __name__ == "__main__":
    set_cpdb(cpdb, remove=True)


class Main(object):
    """ manages batch"""

    di_opt = {}

    def __repr__(self):
        return self.__class__.__name__


    def __init__(self, options):

        try:
            self.options = options

            pwd = os.getcwd()
            self.workdir = self.options.workdir or pwd

            self.config = None

            fnp_config = self.options.config
            if self.options.init:
                fnp_config = self._initialize(fnp_config)

            if not fnp_config:
                for dn in [self.workdir, pwd]:
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

            #
            self.vars = dict()

            self.vars["scandir"] = self.options.workdir

            di_tmp = self.config.get("")

            sectionname = "filenames"
            section = self.config["vars"][sectionname]

            for k, v in section.items():
                self.vars.update(**{"%s_%s" % (sectionname, k): v})

            if rpdb(): pdb.set_trace()



  #               vars:
  # filenames:
  #   scan: "tmp.pip-stripper.imports.rpt"



        except (ValueError,) as e:
            raise
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise




    def process(self):
        try:
            if self.options.scan:
                scanner = Scanner(self)
                scanner.run()


        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    DN = os.path.dirname(__file__)
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


    def _initialize(self, fnp_config):

        

        try:
            fnp_config = os.path.join(self.workdir, self.FN_CONFIG)

            config = dict(coucou=1)

            #load the template file
            fnp_template = os.path.join(self.DN, "templates/pip-stripper.yaml")
            with open(fnp_template) as fi:
                tmpl = fi.read()

            seed = fill_template(tmpl, self)


            with open(fnp_config, "w") as fo:
                fo.write(seed)

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

class Scanner(object):
    def __init__(self, mgr):
        self.mgr = mgr
        self.vars = mgr.vars
        self.worker = mgr.workdir

        self.config = self.mgr.config.get(self.__class__.__name__)
        self.tasknames = self.config["tasknames"]

    # tasknames = ["grep_1", "grep_2" ]

    def run(self):
        for taskname in self.tasknames:
            config = self.mgr.config.get("Command")["tasks"][taskname]

            command = Command(self.mgr, taskname, config)
            command.run()


class Command(object):
    def __init__(self, mgr, taskname, config, append=False):
        self.mgr = mgr
        self.taskname = taskname
        self.append = append

        self.config = config


    def run(self):
        try:
            t_cmd = self.config["cmdline"]#.replace(r"\\","\\")
            #.replace(r"\\",r"\")

            t_fnp = os.path.join(self.mgr.workdir, self.config["filename"])


            cmd = sub_template(t_cmd, self, self.mgr.vars)

            #cmd = "egrep 'import' --include=*.py --exclude='*/migrations/*' --exclude-dir=node_modules -r -n /Users/jluc/kds2/issues2/067.pip-stripper/001.start/py"
            #cmd = "egrep ^\\s*from\\s.+\\simport\\s --include=*.py  -r -n /Users/jluc/kds2/issues2/067.pip-stripper/001.start/py"

            fnp_o = sub_template(t_fnp, self, self.mgr.vars)

            li_cmdline = cmd.split()

            # proc = subprocess.Popen(li_cmd, stdout=subprocess.PIPE)
            # # 50.golive.07.p2.datloader - this is a bytes, object, should be a string...
            # li_line = proc.stdout.readlines()

            with open(fnp_o, "w") as fo:
                proc = subprocess.Popen(cmd.split(), stdout=fo)
            #     res = subprocess.check_output(li_cmdline, stderr=fo)
            #     print(res)

            #     # li_line = proc.stdout.readlines()

            # pdb.set_trace()


            # raise NotImplementedError("%s.run(%s)" % (self, locals()))
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise



if __name__ == "__main__":

    set_cpdb(cpdb, remove=True)

    parser = Main.getOptParser()
    options = parser.parse_args()
    mgr = Main(options)
    mgr.process()

