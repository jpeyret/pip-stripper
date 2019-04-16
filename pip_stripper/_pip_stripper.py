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

from pip_stripper._baseutils import (
    set_cpdb,
    set_rpdb,
    ppp,
    debugObject,
    cpdb,
    fill_template,
    rpdb,
    sub_template,
)

from pip_stripper.writers import ScanWriter
from pip_stripper.matching import Matcher
from pip_stripper.pip import ClassifierPip
from pip_stripper.trackimports import ClassifierImport
from pip_stripper.common import Command
from pip_stripper.builder import Builder

from yaml import safe_load as yload, dump


if __name__ == "__main__":
    set_cpdb(cpdb, remove=True)


dn_script = os.path.dirname(__file__)
if not dn_script:
    fnp_script = os.path.join(dn_cwd_start, sys.argv[0])
    dn_script = os.path.dirname(fnp_script)


class Main(object):
    """ manages batch"""

    di_opt = {}

    def __repr__(self):
        return self.__class__.__name__

    def _get_fnp(self, subject):
        try:
            if subject == "templatedir":
                return os.path.join(dn_script, "templates")
            else:
                fn = self.config["vars"]["filenames"][subject]
            return os.path.join(self.workdir, fn)
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

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
                    msg = "missing configuration file.  perhaps you wanted to use the --init option to create one?"
                    print(msg)
                    sys.exit(1)

            else:
                with open(fnp_config) as fi:
                    self.config = yload(fi)

            self.scan = not self.options.noscan

            #
            self.vars = dict()

            self.vars["scandir"] = self.workdir

            sectionname = "filenames"
            section = self.config["vars"][sectionname]

            for k, v in section.items():
                self.vars.update(**{"%s_%s" % (sectionname, k): v})

            self.import_classifier = ClassifierImport(self)

            self.scanwriter = ScanWriter(self)

            self.matcher = Matcher()

            self.builder = Builder(self)

        except (ValueError,) as e:
            raise
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def process(self):
        try:
            if self.scan:
                self.scanner = Scanner(self)
                self.scanner.run()
                self.import_classifier.run()

                for name in self.import_classifier.packagetracker.di_packagename:
                    self.matcher.imp.feed(name)

                pips = self.pip_classifier = ClassifierPip(self)

                for set_ in pips.di_bucket.values():
                    [self.matcher.pip.feed(name) for name in set_]

                pips.run(self.import_classifier.packagetracker)

                # for name in self.li_pip:

                self.scanwriter.write()

            if self.options.build:
                self.builder.process()

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    DN = os.path.dirname(__file__)
    FN_CONFIG = "pip-stripper.yaml"

    _s_stdlib = None

    @property
    def s_stdlib(self):
        """load the std lib import names"""

        if self._s_stdlib is None:
            self._s_stdlib = liststdlib()
            self._s_stdlib |= set(self.config.get("extra_stdlib", []))

        return self._s_stdlib

    _aliases = _imp2pip = None

    @property
    def imp2pip(self):
        """uses the aliases to look up import name to pip name """
        if self._imp2pip is None:

            self._imp2pip = {v: k for k, v in self.aliases.items()}

        return self._imp2pip

    @property
    def aliases(self):
        if self._aliases is None:
            self._aliases = Matcher.match_all(self)

            # self._aliases = self.matcher.di_pip_imp.copy()
            self._aliases.update(**self.config.get("hardcoded_aliases", {}))

        return self._aliases

    pip2imp = aliases

    _raw_imports = None

    @property
    def raw_imports(self):
        if self._raw_imports is None:
            fnp = self._get_fnp("imports")
            with open(fnp) as fi:
                self._raw_imports = fi.readlines()
        return self._raw_imports

    _all_imports = None

    @property
    def all_imports(self):
        """loads the grep-ed import scans on demand"""

        if self._all_imports is None:
            self._all_imports = set(
                self.import_classifier.packagetracker.di_packagename
            )

        return self._all_imports

    _all_freezes = None
    _all_pips = None

    @property
    def all_freezes(self):
        if self._all_freezes is None:
            # this triggers the pips which what populates
            # the freezes...
            self.all_pips
        return self._all_freezes

    @property
    def all_pips(self):
        """loads the pip freeze output on demand"""

        if self._all_pips is None:
            self._all_pips = set()
            self._all_freezes = {}
            fnp = self._get_fnp("freeze")
            with open(fnp) as fi:
                for line in fi.readlines():
                    try:
                        packagename = self.pip_classifier.parse_requirement_line(line)
                    except (ValueError,) as e:
                        logger.warning("could not parse packagename on %s" % (line))
                        continue
                    self._all_pips.add(packagename)
                    self._all_freezes[packagename] = line.strip()

        return self._all_pips

    @classmethod
    def getOptParser(cls):

        parser = argparse.ArgumentParser()

        dest = "config"
        parser.add_argument(
            "--" + dest,
            action="store",
            help="%s - will look for %s in --workdir, current directory "
            % (dest, cls.FN_CONFIG),
        )

        dest = "noscan"
        default = False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s don't scan to classify packages --build will re-use existing pip-stripper.scan.yaml. [%s]. "
            % (dest, default),
        )

        dest = "build"
        default = False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s - read pip-stripper.scan.yaml to create requirements.prod/dev.txt [%s]"
            % (dest, default),
        )

        dest = "init"
        parser.add_argument(
            "--" + dest,
            action="store_true",
            help="%s initialize the config file if it doesn't exist" % (dest),
        )

        dest = "workdir"
        parser.add_argument(
            "--" + dest,
            action="store",
            help="%s [defaults to config's value or current directory]" % (dest),
        )

        dest = "verbose"
        default = False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s [%s]" % (dest, default),
        )

        return parser

    def _initialize(self, fnp_config):
        """--init option handling"""

        try:
            fnp_config = os.path.join(self.workdir, self.FN_CONFIG)

            config = dict(coucou=1)

            # load the template file
            fnp_template = os.path.join(self.DN, "templates/pip-stripper.yaml")
            with open(fnp_template) as fi:
                tmpl = fi.read()

            seed = fill_template(tmpl, self)

            with open(fnp_config, "w") as fo:
                fo.write(seed)

            print("pip-stripper configuration generated @ %s" % (fnp_config))

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


def liststdlib():
    """
    pretty grungy code, will need a rework
    """
    listed = set()

    std_lib = sysconfig.get_python_lib(standard_lib=True)
    for top, dirs, files in os.walk(std_lib):
        for nm in files:
            if nm != "__init__.py" and nm[-3:] == ".py":
                found = os.path.join(top, nm)[len(std_lib) + 1 : -3].replace("\\", ".")

                found = found.split("/")[0]
                listed.add(found)

    return listed


class Scanner(object):
    def __init__(self, mgr):
        self.mgr = mgr
        self.config = self.mgr.config.get(self.__class__.__name__)
        self.tasknames = self.config["tasknames"]

    def run(self):
        try:
            for taskname in self.tasknames:
                config = self.mgr.config.get("Command")["tasks"][taskname]

                command = Command(self.mgr, taskname, config)
                command.run()

            fnp_out = os.path.join(
                self.mgr.workdir, self.mgr.config["vars"]["filenames"]["liststdlib"]
            )
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


def main(args=None):
    """the console_scripts entry point"""

    if args is None:
        args = sys.argv[1:]

    parser = Main.getOptParser()
    options = parser.parse_args(args)

    mgr = Main(options)
    mgr.process()


if __name__ == "__main__":

    # conditional pdb.trace()-ing with --cpdb on command line
    set_cpdb(cpdb, remove=True)

    main()
