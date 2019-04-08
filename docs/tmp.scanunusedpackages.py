#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""doc for scanunusedpackages.py - """
import logging
logger = logging.getLogger(__name__)

from typing import Tuple

import sys
import argparse
import re
import os

from traceback import print_exc as xp
import pdb

from yaml import safe_load as yload, dump

from bemyerp.lib.utils import set_cpdb, set_rpdb, ppp, debugObject


import bemyerp.pssystem.constants as constants
#import bemyerp.lib.batchhelper as batchhelper

from bemyerp.lib.utils import set_cpdb, set_rpdb, set_breakpoints3, first

from bemyerp.lib.breakpoints import (
    DisabledBreakpoints,
)

breakpoints = DisabledBreakpoints()

from collections import defaultdict

def cpdb(**kwds):
    if cpdb.enabled == "once":
        cpdb.enabled = False
        return True
    return cpdb.enabled


cpdb.enabled = False


def rpdb():
    return rpdb.enabled


rpdb.enabled = False


if __name__ == "__main__":
    set_cpdb(cpdb, remove=True)
    set_rpdb(rpdb, remove=True)

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
            if cpdb(): pdb.set_trace()
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
                #first time, just put it in
                self.di_packagename[packagename] = bucketname
                return

            if bucketname == bucketname_prev:
                #same as before, nothing to do
                return

            index_new = self.di_bucketindex[bucketname]
            index_old = self.di_bucketindex[bucketname_prev]

            if index_new < index_old:
                #higher precendence for new (ex:  prod beats dev)
                self.di_packagename[packagename] = bucketname
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    def classify(self):
        di_result = defaultdict(list)

        for packagename, bucketname in self.di_packagename.items():
            di_result[bucketname].append(packagename)

        return di_result

    def report(self):
        classification = self.classify()
        lines = []

        di_buckets = {}
        di = dict(
            package_imports = di_buckets
            )


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


class DirectoryPartitioner:

    key = "partition_dirs"

    def __init__(self, mgr, config):
        try:
            self.mgr = mgr
            self.buckets = []
            self.di_bucket = {}

            for key, li_pattern in config.items():
                bucket = DirectoryPartitionerBucket(key)
                for pattern in li_pattern:
                    bucket.add(pattern)
                self.di_bucket[key] = bucket
                self.buckets.append(bucket)                

            ppp(config)
            ppp(self)
            # pdb.set_trace()
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    def classify_filename(self, filename : str) -> DirectoryPartitionerBucket:
        try:
            for bucket in self.buckets:
                found = bucket.is_match(filename)
                if found:
                    return bucket

            raise ValueError("no bucket match for %s" % (filename))

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
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
            if cpdb(): pdb.set_trace()
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
            if cpdb(): pdb.set_trace()
            raise

class PipDepHelper:

    patre_splitline = re.compile("==")

    def __init__(self, mgr, config, data):
        try:
            self.mgr = mgr
            self.config = config
            self.data = data
            self.s_workstation = set(config.get("workstation",[]))
            self.s_prod = set(config.get("prod",[]))
            self.s_unknown = set()

            import bemyerp.websec.dev_settings
            self.s_devsettings = set(v.split(".")[0] for v in bemyerp.websec.dev_settings.INSTALLED_APPS)

            import bemyerp.websec.prod_settings
            self.s_prodsettings = set(v.split(".")[0] for v in bemyerp.websec.prod_settings.INSTALLED_APPS)

            self.s_tests = set(config.get("workstation",[]))

            self.s_devsettings = self.s_devsettings | self.s_tests - self.s_prodsettings

            self.di_bucket = defaultdict(set)

            # pdb.set_trace()
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise        


    def process(self, packagetracker):

        try:
            self.s_directinstall = set()
            for line in self.data.split("\n"):
                if line.startswith(" "):
                    continue
                if not line.strip():
                    continue

                packagename, version = self.patre_splitline.split(line)

                self.s_directinstall.add(packagename)

            di_packagename2pip = self.mgr.di_packagename2pip

            for packagename_ in self.s_directinstall:
                packagename = packagename_.replace("-","_")
                if packagename.startswith("django_"):
                    packagename = packagename.replace("django_","")

                if packagename_ != packagename:
                    di_packagename2pip[packagename_] = packagename

                # if packagetracker.get_package(packagename):
                bucketname = packagetracker.get_package(packagename)
                if bucketname:
                    self.di_bucket[bucketname].add(packagename)
                    continue                    

                if packagename in self.s_prod:
                    self.di_bucket["prod"].add(packagename)                    
                    continue                    

                if packagename in self.s_prodsettings:
                    self.s_prodsettings.remove(packagename)
                    self.di_bucket["prod"].add(packagename)
                    continue                    

                if packagename in self.s_workstation:
                    continue

                if packagename in self.s_devsettings:
                    continue


                self.s_unknown.add(packagename)

            self.di_bucket["prod"] =  self.di_bucket["prod"] | self.s_prodsettings

            self.s_unknown = self.s_unknown - self.di_bucket["prod"] - self.di_bucket["dev"]

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    def report(self):
        try:

            lines = ["\npip installed:"]

            fo=self.mgr.fo

            di2 = dict(
                # _settings_prod=sorted(self.s_prodsettings),
                _settings_dev=sorted(self.s_devsettings),
                _local=dict(
                    workstation=sorted(self.s_workstation),
                    unknown=sorted(self.s_unknown),
                    )
                )
            di2.update(**{k:sorted(v) for k,v in self.di_bucket.items()})

            di1 = dict(
                pip = di2
                )

            dump(di1, stream=fo, default_flow_style=False)


            print("\n".join(lines))
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

def lines_extend(mgr, lines, header, set_, tmpl="  %s", fo=None, indent=0):
    # pdb.set_trace()

    try:

        header_print = header
        if not header_print.endswith(":"):
            header_print += ":"

        lines.append(header)
        li = sorted(list(set_))
        lines.extend([tmpl % v for v in li])

        if fo:
            di = {header:li}

            dump(di, stream=fo, default_flow_style=False)
            fo.write("\n")

    except (Exception,) as e:
        if cpdb(): pdb.set_trace()
        raise


class MainManager:#(batchhelper.BatchManager):
    """ manages batch"""

    di_opt = {}

    config = options = None

    def __repr__(self):
        return self.__class__.__name__

    def debug(self, *args):
        ppp(self.config)
        ppp(self.options)
        print(*args)


    def __init__(self, options):
        try:
            self.options = options

            if self.options.verbose:
                constants.verbose = True

            self.options.outputdir = self.options.outputdir or self.options.workdir

            self.patre_splitline = re.compile(":\d+:")

            if constants.verbose:
                msg = debugObject(self, "\n\n MainManager.__init__:end")
                msg += debugObject(self.options, "\noptions")
                logger.info(msg)

            with open(self.options.config) as fi:
                self.config = yload(fi)

            self.codedir = self.config.get("codedir")
            if not self.codedir.endswith(os.path.sep):
                self.codedir += os.path.sep

            configpartitions = self.config.get(DirectoryPartitioner.key)
            self.directorypartitioner = DirectoryPartitioner(self, configpartitions)

            self.di_packagename2pip = {}

            # PackageBucketTracker:
            #   precedence:
            #     - "prod"
            #     - "dev"
            bucketnames_tracker = self.config.get("PackageBucketTracker")["precedence"]

            self.packagetracker = PackageBucketTracker(self, bucketnames_tracker)

            self.fnp_o = os.path.join(self.options.outputdir, "package_report.yaml")

            fnp = os.path.join(self.options.workdir, "packages.stdlib.rpt")
            with open(fnp) as fi:
                self.s_stdlib = set([line.strip() for line in fi.readlines()])

            #not sure why they are not found in stdlib...
            extra_stdlib = self.config.get("extra_stdlib",[])
            [self.s_stdlib.add(m_) for m_ in extra_stdlib]

            # Untracked:
            #   - "bemyerp"
            untracked = self.config.get("Untracked",[])
            self.s_untracked = set(untracked)

            fnp = os.path.join(self.options.workdir, "pipdeptree.rpt")
            with open(fnp) as fi:
                data = fi.read()

            self.pipdephelper = PipDepHelper(self, self.config.get("PipDepHelper"), data)

            
        except (Exception,) as e:
            self.debug()
            if cpdb(): 
                pdb.set_trace()
            raise

    def parse_import(self, import_ : str) -> str: 
        try:
            import_ = import_.strip()

            if import_.startswith("from ") or import_.startswith("import "):
                _packagename = import_.split()[1]
                packagename = _packagename.split(".")[0]
                return packagename


            raise NotImplementedError("parse_import(%s)" % (locals()))

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    
    def parse(self, line_in : str) -> Tuple :

        """
        
        """
        #/Users/jluc/kds2/py2/bemyerp/lib/_baseutils.py:6:from functools import partial, wraps
        try:
            line = line_in.replace(self.codedir, "").rstrip()

            filename, import_ = self.patre_splitline.split(line)

            packagename = self.parse_import(import_)

            pythonfile = PythonFile.get(self, self.directorypartitioner, filename)

            return pythonfile, packagename


        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise
    


    def process(self):
        try:

            logger.info(self.s_stdlib)
            filebucket = packagename = None

            fnp = os.path.join(self.options.workdir, "allimports.rpt")
            with open(fnp) as fi:
                for line in fi.readlines():
                    filebucket, packagename = self.parse(line)

                    if packagename in self.s_stdlib:
                        logger.info("%s in std lib" % (packagename))
                        continue

                    if packagename in self.s_untracked:
                        logger.info("%s in std lib" % (packagename))
                        continue

                    self.packagetracker.add_import(packagename, filebucket.bucket.name)

            bucket_imports = self.packagetracker.classify()

            self.pipdephelper.process(self.packagetracker)


            # raise NotImplementedError("%s.process(%s)" % (self, locals()))

        except (Exception,) as e:
            self.debug(filebucket, packagename)
            if cpdb(): 
                pdb.set_trace()
            raise

    def report(self):
        with open(self.fnp_o, "w", encoding="utf-8") as self.fo:

            try:

                lines = []

                lines_extend(self, lines, "stdlib", self.s_stdlib, fo=self.fo)

                self.packagetracker.report()

                self.pipdephelper.report()

                dump(
                    dict(aliases=self.di_packagename2pip
                        ),
                    stream=self.fo,
                    default_flow_style=False
                    )

            except (Exception,) as e:
                if cpdb(): pdb.set_trace()
                raise

    @classmethod
    def getOptParser(cls):

        parser = argparse.ArgumentParser()

        dest="verbose"
        default=False
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store_true",
            help="%s [%s]" % (dest, default)
            )
        
        dest="config"
        default = os.path.join(os.path.dirname(__file__), "scanunusedpackages.yaml")
        parser.add_argument(
            "--" + dest,
            default=default,
            action="store",
            help="%s [%s]" % (dest, default)
            )

        dest="workdir"
        parser.add_argument(
            dest,
            action="store",
            help="%s - where are the input files?" % (dest)
            )

        dest="outputdir"
        parser.add_argument(
            "--" + dest,
            action="store",
            help="%s - defaults to workdir" % (dest)
            )
                        

        # use snippet.optadd to expand choices.
        return parser


if __name__ == "__main__":

    set_cpdb(cpdb, remove=True)
    set_rpdb(rpdb, remove=True)

    parser = MainManager.getOptParser()
    options = parser.parse_args()
    mgr = MainManager(options)
    mgr.process()
    mgr.report()

