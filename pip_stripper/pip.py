import logging

logger = logging.getLogger(__name__)

import sys
import re
import os

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import ppp, cpdb, rpdb
from pip_stripper.common import enforce_set_precedence


class ClassifierPip(object):
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, mgr):
        try:
            self.mgr = mgr
            self.config = self.mgr.config.get(self.__class__.__name__)
            self.s_directinstall = set()

            self.patre_splitline = re.compile(self.config["pattern_splitline"])

            self.di_bucket_association = self.config["buckets"]
            self.di_bucket = {}
            for k, v in self.di_bucket_association.items():
                self.di_bucket[k] = set()
                s_ = self.di_bucket_association[k] = set(v)
                try:
                    s_.remove("pass")
                except (KeyError,) as e:
                    pass

            self.bucket_precedence = self.config["bucket_precedence"]

            # remove entries in lower precedence positions that
            # exist higher up
            li = []
            for bucketname in self.bucket_precedence:
                li.append(self.di_bucket_association[bucketname])
            enforce_set_precedence(li)

            self.warnings = self.config["warnings"]

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def parse_requirement_line(self, line):
        try:
            packagename, version = self.patre_splitline.split(line)
            return packagename
        except ValueError:
            raise

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def load(self):
        try:
            fnp = self.mgr._get_fnp("pipdeptree")
            with open(fnp) as fi:
                data = fi.read()

            for line in data.split("\n"):
                if line.startswith(" "):
                    continue
                if not line.strip():
                    continue

                # really should skip stdlibs here...

                packagename, version = self.patre_splitline.split(line)

                self.s_directinstall.add(packagename)
            return self.s_directinstall

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def run(self, packagetracker):

        try:

            di_packagename2pip = self.mgr.imp2pip
            all_imports = self.mgr.all_imports

            self.s_missing_imports = all_imports.copy()

            packagename = packagename_ = None
            pip2imp = self.mgr.pip2imp

            for pipname in self.mgr.all_pips:

                if pipname == "pyquery":
                    if rpdb():
                        pdb.set_trace()

                packagename = pip2imp.get(pipname, pipname)

                found = False
                for bucketname in self.bucket_precedence:
                    if pipname in self.di_bucket_association[bucketname]:
                        self.di_bucket[bucketname].add(pipname)
                        found = True
                        try:
                            self.s_missing_imports.remove(packagename)
                        except (KeyError,) as e:
                            pass
                        break

                if found:
                    continue

                # if packagetracker.get_package(packagename):
                bucketname = packagetracker.get_package(packagename)
                if bucketname:
                    self.di_bucket[bucketname].add(pipname)
                    try:
                        self.s_missing_imports.remove(packagename)
                    except (KeyError,) as e:
                        pass
                    continue

                self.di_bucket["unknown"].add(pipname)

            # self.di_bucket["prod"] = self.di_bucket["prod"] | self.s_prodsettings

            # self.s_unknown = (
            #     self.s_unknown - self.di_bucket["prod"] - self.di_bucket["dev"]
            # )
            for import_ in self.s_missing_imports:
                self.warnings.append("missing import:%s" % (import_))

        except (Exception,) as e:
            if cpdb():
                ppp(dict(packagename=packagename, packagename_=packagename_))
                pdb.set_trace()
            raise
