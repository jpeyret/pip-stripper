import logging

logger = logging.getLogger(__name__)

import sys
import os
from yaml import safe_load as yload

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import ppp, cpdb, rpdb, sub_template
from pip_stripper.common import enforce_set_precedence


class Builder(object):
    def __init__(self, mgr):
        self.mgr = mgr
        self.fnp_input_classifier = self.mgr._get_fnp("scan")

        self.fnp_input_freeze = self.mgr._get_fnp("freeze")

        self.config = self.mgr.config.get(self.__class__.__name__)

    def process(self):
        try:

            t_fn = self.config["t_filename_out"]
            for req, di in self.config("req_mapper").items():
                fn_o = sub_template(t_fn, dict(req=req))
                fnp_o = os.path.join(self.mgr.workdir, fn_o)

                for bucketname in di["buckets"]:

                    pass

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
