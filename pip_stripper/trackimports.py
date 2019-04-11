import logging

logger = logging.getLogger(__name__)

import sys
import re
import os

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
