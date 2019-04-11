import logging

logger = logging.getLogger(__name__)

import sys
import re
import os
from collections import defaultdict

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import ppp, cpdb, rpdb
from pip_stripper.common import enforce_set_precedence


class ClassifierImport(object):
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, mgr):
        try:
            self.mgr = mgr

            self.config = self.mgr.config.get(self.__class__.__name__)

            self.buckets = []
            self.di_bucket = {}

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

            default_bucket_name = self.config["default_bucket"]
            self.default_bucket = self.di_bucket[default_bucket_name]

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def classify_filename(self, filename_import):
        try:
            for bucket in self.buckets:
                found = bucket.is_match(filename_import)
                if found:
                    return bucket

            return self.default_bucket

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def run(self):
        try:
            # raise NotImplementedError("%s.run(%s)" % (self, locals()))

            self.s_stdlib = self.mgr.s_stdlib

            for line in self.mgr.raw_imports:
                filebucket, packagename = self.parse(line)

                if packagename in self.s_stdlib:
                    if self.mgr.options.verbose:
                        logger.info("%s in std lib" % (packagename))
                    continue

                if packagename in self.s_untracked:
                    if self.mgr.options.verbose:
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
