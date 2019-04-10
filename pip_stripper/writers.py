import logging

logger = logging.getLogger(__name__)

import sys
import re
import os

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

from yaml import safe_load as yload, dump


class ScanWriter(object):
    """
    imports:
      dev:
      prod:
      tests:

    pips:
      dev:
      prod:
      tests:
      workstation:
      unclassified:

    aliases:
    stdlib:

    """

    def __init__(self, mgr):
        self.mgr = mgr
        self.fnp_yaml = mgr._get_fnp("scan")

    def write(self):
        try:
            if rpdb():
                pdb.set_trace()

            pips = self.mgr.pip_classifier.di_bucket.copy()

            for k, v in pips.items():
                pips[k] = sorted(v)

            warnings = self.mgr.pip_classifier.warnings

            di = self.di = dict(
                imports=self.mgr.import_classifier.packagetracker.classify(),
                pips=pips,
                aliases=self.mgr.aliases,
                warnings=warnings,
            )

            if self.mgr.options.verbose:
                di_debug = dict(
                    stdlib=sorted(self.mgr.s_stdlib),
                    all_imports=sorted(self.mgr.all_imports),
                    all_pips=sorted(self.mgr.all_pips),
                )
                di["zzz_debug"] = di_debug

            with open(self.fnp_yaml, "w", encoding="utf-8") as fo:
                dump(self.di, fo, default_flow_style=False)

            # raise NotImplementedError("write(%s)" % (locals()))
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
