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

    def write(self, *args, **kwargs):
        try:
            raise NotImplementedError("write(%s)" % (locals()))
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
