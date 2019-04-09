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

            self.di = dict(
                imports=self.mgr.import_classifier.packagetracker.classify(),
                pips=dict(dev="dev", prod="prod", tests="tests"),
                aliases=[],
                stdlib=[],
            )

            with open(self.fnp_yaml, "w", encoding="utf-8") as fo:
                dump(self.di, fo, default_flow_style=False)

            # raise NotImplementedError("write(%s)" % (locals()))
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
