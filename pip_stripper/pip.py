import logging

logger = logging.getLogger(__name__)

import sys
import re
import os

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import ppp, cpdb


class ClassifierPip(object):
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, mgr):
        try:
            self.mgr = mgr
            self.config = self.mgr.config.get(self.__class__.__name__)
            self.s_directinstall = set()

            self.patre_splitline = re.compile(self.config["pattern_splitline"])

            self.di_bucket = self.config["buckets"]
            for k, v in self.di_bucket.items():
                s_ = self.di_bucket[k] = set(v)
                try:
                    s_.remove("pass")
                except (KeyError,) as e:
                    pass

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def load(self):
        try:
            fnp = self.mgr._get_fnp("pipdeptree")
            with open(fnp) as fi:
                self.data = fi.read()

            for line in self.data.split("\n"):
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

            di_packagename2pip = self.mgr.di_packagename2pip

            for packagename_ in self.s_directinstall:
                packagename = packagename_.replace("-", "_")
                if packagename.startswith("django_"):
                    packagename = packagename.replace("django_", "")

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

            self.di_bucket["prod"] = self.di_bucket["prod"] | self.s_prodsettings

            self.s_unknown = (
                self.s_unknown - self.di_bucket["prod"] - self.di_bucket["dev"]
            )

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
