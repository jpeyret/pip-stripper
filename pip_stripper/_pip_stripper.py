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
import distutils.sysconfig as sysconfig

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

def liststdlib(fnp_out, toponly=True, mgr=None):
    """
    pretty grungy code, will need a rework
    """

    extra_stdlib = []
    if mgr:
        extra_stdlib=mgr.config.get("extra_stdlib",[])

    if toponly:
        listed = set(extra_stdlib)

    std_lib = sysconfig.get_python_lib(standard_lib=True)
    for top, dirs, files in os.walk(std_lib):
        for nm in files:
            if nm != '__init__.py' and nm[-3:] == '.py':
                found = os.path.join(top, nm)[len(std_lib)+1:-3].replace('\\','.')

                if toponly:
                    found = found.split("/")[0]
                    if found in listed:
                        continue
                    listed.add(found)

    with open(fnp_out, "w") as fo:
        for line in sorted(listed):
            fo.write("%s\n" % (line))


class Scanner(object):
    def __init__(self, mgr):
        self.mgr = mgr
        self.vars = mgr.vars
        self.worker = mgr.workdir

        self.config = self.mgr.config.get(self.__class__.__name__)
        self.tasknames = self.config["tasknames"]


    def run(self):
        try:
            for taskname in self.tasknames:
                config = self.mgr.config.get("Command")["tasks"][taskname]

                command = Command(self.mgr, taskname, config)
                command.run()

            fnp_out = os.path.join(self.mgr.workdir, self.mgr.config["vars"]["filenames"]["liststdlib"])
            liststdlib(fnp_out, toponly=True, mgr=self.mgr)
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

class Command(object):
    def __init__(self, mgr, taskname, config, append=False):
        self.mgr = mgr
        self.taskname = taskname
        self.append = append

        self.config = config
        self.stderr = ""

    def write(self, msg):
        self.stderr += "%s\n" 

    def run(self):
        try:
            t_cmd = self.config["cmdline"]#.replace(r"\\","\\")
            t_fnp = os.path.join(self.mgr.workdir, self.config["filename"])

            cmd = sub_template(t_cmd, self, self.mgr.vars)

            fnp_o = sub_template(t_fnp, self, self.mgr.vars)

            li_cmdline = cmd.split()


            mode = "a" if self.append else "w"

            with open(fnp_o, mode) as fo:
                proc = subprocess.Popen(cmd.split(), stdout=fo, stderr=subprocess.DEVNULL, cwd=self.mgr.workdir, encoding="utf-8")

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise



if __name__ == "__main__":

    set_cpdb(cpdb, remove=True)

    parser = Main.getOptParser()
    options = parser.parse_args()
    mgr = Main(options)
    mgr.process()

