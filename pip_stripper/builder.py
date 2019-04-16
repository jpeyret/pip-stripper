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
        self.config = self.mgr.config.get(self.__class__.__name__)

    def process(self):
        try:

            with open(self.fnp_input_classifier) as fi:
                di_classifier = yload(fi)

            di_bucket = di_classifier["pips"]["buckets"]

            di_freeze = di_classifier["pips"]["freeze"]

            t_fn = self.config["t_filename_out"]
            print("build phase - generating requirements at:")
            for req, di in self.config["req_mapper"].items():
                fn_o = sub_template(t_fn, dict(req=req))
                fnp_o = os.path.join(self.mgr.workdir, fn_o)

                requirements = []

                for bucketname in di["buckets"]:
                    for pipname in di_bucket[bucketname]:
                        freeze_line = di_freeze[pipname]
                        requirements.append(freeze_line)

                requirements.sort()

                with open(fnp_o, "w") as fo:
                    for line in requirements:
                        fo.write("%s\n" % (line))

                print("  %s" % (fnp_o))

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
