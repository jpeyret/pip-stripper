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
from collections import defaultdict

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

from yaml import safe_load as yload, dump


if __name__ == "__main__":
    set_cpdb(cpdb, remove=True)


class Main(object):
    """ manages batch"""

    di_opt = {}

    def __repr__(self):
        return self.__class__.__name__

    def _get_fnp(self, subject):
        try:
            if subject == "log":
                fn = "pip-stripper.log"
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

            self.scanwriter = ScanWriter(self)

            self.matcher = Matcher()

        except (ValueError,) as e:
            raise
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def process(self):
        try:
            if self.options.scan:
                self.scanner = Scanner(self)
                self.scanner.run()
                self.import_classifier = ClassifierImport(self)
                self.import_classifier.run()

                for name in self.import_classifier.packagetracker.di_packagename:
                    self.matcher.imp.feed(name)

                pips = self.pip_classifier = ClassifierPip(self)

                pips.load()
                for set_ in pips.di_bucket.values():
                    [self.matcher.pip.feed(name) for name in set_]

                self.matcher.do_match()

                self.aliases = self.matcher.di_pip_imp.copy()
                self.aliases.update(**self.config.get("hardcoded_aliases", {}))

                pips.run(self.import_classifier.packagetracker)

                # for name in self.li_pip:

                self.scanwriter.write()

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    DN = os.path.dirname(__file__)
    FN_CONFIG = "pip-stripper.yaml"

    _s_stdlib = None

    @property
    def s_stdlib(self):

        if self._s_stdlib is None:

            self._s_stdlib = liststdlib()
            self._s_stdlib |= set(self.config.get("extra_stdlib", []))

        return self._s_stdlib

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

        dest = "scan"
        default = True
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_false",
            help="%s scan python files and classify packages [%s]" % (dest, default),
        )

        dest = "build"
        default = False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s [%s]" % (dest, default),
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

        # use snippet.optadd to expand choices.
        return parser

    def _initialize(self, fnp_config):

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


class DirectoryPartitionerBucket:
    def __init__(self, name):
        self.name = name
        self.li_pattern = []

    def __repr__(self):
        return "Bucket(%s)" % (self.name)

    def add(self, pattern):
        self.li_pattern.append(re.compile(pattern))

    def is_match(self, filename):
        try:
            for patre in self.li_pattern:
                hit = patre.search(filename)
                if hit:
                    return True
            return False
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class ClassifierImport(object):
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, mgr):
        try:
            self.mgr = mgr

            self.config = self.mgr.config.get(self.__class__.__name__)

            self.buckets = []
            self.di_bucket = {}

            self.fnp_importscan = self.mgr._get_fnp("imports")

            self.s_untracked = set(self.mgr.config.get("untracked", []))

            bucketnames_tracker = self.config["buckets"]["precedence"]

            self.packagetracker = PackageBucketTracker(self, bucketnames_tracker)

            self.workdir = self.mgr.workdir

            self.patre_splitline = re.compile(self.config["pattern_splitline"])

            for key, li_pattern in self.config["regex_dirs"].items():
                bucket = DirectoryPartitionerBucket(key)
                for pattern in li_pattern:
                    bucket.add(pattern)
                self.di_bucket[key] = bucket
                self.buckets.append(bucket)

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def classify_filename(self, filename_import) -> DirectoryPartitionerBucket:
        try:
            for bucket in self.buckets:
                found = bucket.is_match(filename_import)
                if found:
                    return bucket

            raise ValueError("no bucket match for %s" % (filename_import))

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def run(self):
        try:
            # raise NotImplementedError("%s.run(%s)" % (self, locals()))

            self.s_stdlib = self.mgr.s_stdlib

            with open(self.fnp_importscan) as fi:
                for line in fi.readlines():
                    filebucket, packagename = self.parse(line)
                    # if rpdb():
                    #     print("filebucket:%s, packagename:%s" % (filebucket, packagename))
                    #     pdb.set_trace()

                    if packagename in self.s_stdlib:
                        logger.info("%s in std lib" % (packagename))
                        continue

                    if packagename in self.s_untracked:
                        logger.info("%s in std lib" % (packagename))
                        continue

                    self.packagetracker.add_import(packagename, filebucket.bucket.name)

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def parse(self, line_in):

        """
        
        """
        # /Users/jluc/kds2/py2/bemyerp/lib/_baseutils.py:6:from functools import partial, wraps
        try:
            line = line_in.replace(self.workdir, "").rstrip()

            filename, import_ = self.patre_splitline.split(line)

            packagename = self.parse_import(import_)

            pythonfile = PythonFile.get(self, self, filename)

            return pythonfile, packagename

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def parse_import(self, import_: str) -> str:
        try:
            import_ = import_.strip()

            if import_.startswith("from ") or import_.startswith("import "):
                _packagename = import_.split()[1]
                packagename = _packagename.split(".")[0]
                return packagename

            raise NotImplementedError("parse_import(%s)" % (locals()))

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


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


class PackageBucketTracker:
    def __init__(self, mgr, bucketnames):
        """
            this is a precedence mechanism
            if bucketnames : prod, dev
            then a packagename gets move from dev to prod
            if it was in dev but then gets used in prod

        """
        self.mgr = mgr
        self.bucketnames = bucketnames.copy()
        self.di_packagename = {}

        self.di_bucketindex = {}
        for ix, bucketname in enumerate(self.bucketnames):
            self.di_bucketindex[bucketname] = ix

    def get_package(self, packagename):
        return self.di_packagename.get(packagename)

    def add_import(self, packagename, bucketname):
        try:
            bucketname_prev = self.di_packagename.get(packagename)
            if not bucketname_prev:
                # first time, just put it in
                self.di_packagename[packagename] = bucketname
                return

            if bucketname == bucketname_prev:
                # same as before, nothing to do
                return

            index_new = self.di_bucketindex[bucketname]
            index_old = self.di_bucketindex[bucketname_prev]

            if index_new < index_old:
                # higher precendence for new (ex:  prod beats dev)
                self.di_packagename[packagename] = bucketname

            if rpdb():
                pdb.set_trace()
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def classify(self):
        di_result = defaultdict(list)

        for packagename, bucketname in self.di_packagename.items():
            di_result[bucketname].append(packagename)

        return dict(**di_result)

    def report(self):
        classification = self.classify()
        lines = []

        di_buckets = {}
        di = dict(package_imports=di_buckets)

        for bucketname in self.bucketnames:
            lines.append("%s:" % (bucketname))
            li = classification[bucketname]
            li.sort()
            # for import_ in li:
            #     lines.append("  %s" % (import_))
            di_buckets[bucketname] = li

            lines_extend(self.mgr, lines, bucketname, li)

        if self.mgr.fo:
            dump(di, self.mgr.fo, default_flow_style=False)
            self.mgr.fo.write("\n")

        print("\n".join(lines))


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
            t_cmd = self.config["cmdline"]  # .replace(r"\\","\\")
            t_fnp = os.path.join(self.mgr.workdir, self.config["filename"])

            fnp_log = "subprocess.log"

            cmd = sub_template(t_cmd, self, self.mgr.vars)

            fnp_o = sub_template(t_fnp, self, self.mgr.vars)

            li_cmdline = cmd.split()

            mode = "a" if self.append else "w"

            fnp_stderr = self.mgr._get_fnp("log")
            with open(fnp_stderr, "a") as ferr:

                ferr.write("cmd: %s\nstderr begin:\n" % (cmd))

                with open(fnp_o, mode) as fo:
                    proc = subprocess.check_call(
                        cmd.split(),
                        stdout=fo,
                        stderr=ferr,
                        cwd=self.mgr.workdir,
                        encoding="utf-8",
                    )
                ferr.write("stderr end\n\n")

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class PythonFile:

    di_filename = {}

    def __repr__(self):
        return "%s in %s" % (self.filename, self.bucket)

    def __init__(self, filename, bucket):
        self.filename = filename
        self.bucket = bucket
        self.imports = []

    def add(self, import_):
        try:
            raise NotImplementedError()
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    @classmethod
    def get(cls, mgr, directorypartitioner, filename):
        try:

            res = cls.di_filename.get(filename)
            if res:
                return res

            bucket = directorypartitioner.classify_filename(filename)
            res = cls.di_filename[filename] = cls(filename, bucket)
            return res

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


if __name__ == "__main__":

    set_cpdb(cpdb, remove=True)

    parser = Main.getOptParser()
    options = parser.parse_args()
    mgr = Main(options)
    mgr.process()
