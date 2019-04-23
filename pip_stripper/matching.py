import logging

logger = logging.getLogger(__name__)

import os
import pkg_resources

import pdb

from traceback import print_exc as xp


def cpdb(**kwds):
    return False


cpdb.enabled = False

from pip_stripper._baseutils import ppp


class MatcherOld(object):
    """OK, strictly speaking the new way in Matcher and PipSide
       ,by looking up the top_level.txt in egg_info, is better
       but it misses some edge cases:
            - egg_info is missing if the package wasn't installed
            - there might be multiple names for the package...

       so might use MatcherOld
       codebase to try to recover then.
    """

    def __init__(self):

        self.pip = Side(self, "pip", _variations_pip)
        self.imp = Side(self, "imp", _variations_imp)

        self.s_pip_wo_packageinfo = set()

        self.di_pip_imp = dict()

    @classmethod
    def match_all(cls, mgr):
        try:
            inst_start = getattr(mgr, "matcher", None)
            inst = inst_start or cls()
            for imp in mgr.all_imports:
                inst.imp.feed(imp)
            for pip in mgr.all_pips:
                if pip.strip().startswith("#"):
                    continue

                inst.pip.feed(pip)

            inst.do_match()
            if not inst_start:
                mgr.matcher = inst
            return inst.di_pip_imp

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def do_match(self):
        try:

            self.matches = self.pip.s_alias & self.imp.s_alias

            for match in self.matches:
                pip = self.pip.di_alias[match]
                imp = self.imp.di_alias[match]

                self.di_pip_imp[pip] = imp

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class Matcher(MatcherOld):
    """this matcher doesn't do much as all the heavy lifting is 
    left to the PipSide feed
    """

    def do_match(self, *args, **kwargs):
        """PipSide.feed is supposed to do all the work"""

        try:
            return
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def __init__(self):

        self.di_pip_imp = dict()
        self.pip = PipSide(self, "pip", _variations_pip)
        self.imp = Side(self, "imp", _variations_imp)
        self.s_pip_wo_packageinfo = set()
        self._debug = {}


class Side(object):
    def __repr__(self):
        return self.subject

    def __init__(self, mgr, subject, li_varfunc):
        self.mgr = mgr
        self.subject = subject
        self.di_name = {}
        self.li_varfunc = li_varfunc
        self.s_alias = set()

        self.di_alias = {}

        self.di_duplicates = {}

    def get_aliases(self, name):
        try:

            def alias(name, func):
                try:
                    return func(name)
                except (Exception,) as e:
                    return None

            name = name.lower()
            res = set([i for i in [alias(name, f) for f in self.li_varfunc] if i])
            return res

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def feed(self, name):
        try:
            entry = self.di_name[name] = name

            aliases = self.get_aliases(name)

            # check for duplicates:
            dup = self.s_alias & aliases
            if dup:
                msg = "%s. alias duplicates:%s " % (self, dup)
                logger.debug(msg)

            self.s_alias |= aliases

            self.di_alias.update(**{k: entry for k in aliases})

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class PipSide(Side):
    """the class who does most of the work figuring out aliases
       this is done by pkg_resources.get_distribution, followed
       by reading `top_level.txt`

    """

    def feed(self, name_in):
        """
        credit for pkg_resources code belongs to 
        https://stackoverflow.com/a/54853084
        """

        try:

            name = name_in.replace("-", "_")

            try:
                metadata_dir = pkg_resources.get_distribution(name).egg_info
            except (pkg_resources.DistributionNotFound,) as e:
                msg = "%s:%s" % (name_in, e)
                logger.warning(msg)
                self.mgr.s_pip_wo_packageinfo.add(name_in)
                # self.mgr.di_pip_imp[name_in] = None
                self.mgr._debug[name_in] = msg
                return

            fnp = os.path.join(metadata_dir, "top_level.txt")

            try:
                with open(fnp) as fi:
                    packagenames = fi.readlines()
            except (IOError,) as e:
                msg = "%s:IOError reading top_level.txt" % (name_in)
                logger.warning(msg)
                self.mgr.s_pip_wo_packageinfo.add(name_in)
                # self.mgr.di_pip_imp[name_in] = None
                self.mgr._debug[name_in] = msg
                return

            packagenames = [pn.strip() for pn in packagenames if pn.strip()]

            len_packagenames = len(packagenames)

            if len_packagenames == 1:
                self.mgr.di_pip_imp[name_in] = packagenames[0]
            else:

                if name in packagenames:

                    # catches things like bcrypt => ['_bcrypt', 'bcrypt']
                    self.mgr.di_pip_imp[name_in] = name
                else:
                    msg = "%s:too many packagenames in %s" % (name_in, packagenames)
                    logger.warning(msg)
                    self.mgr.s_pip_wo_packageinfo.add(name_in)
                    # self.mgr.di_pip_imp[name_in] = None
                    self.mgr._debug[name_in] = msg
                    return

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


_variations = [str]

_variations_pip = _variations + [lambda x: x.split("-")[1]]

_variations_imp = _variations + [lambda x: x.split("_")[1]]
