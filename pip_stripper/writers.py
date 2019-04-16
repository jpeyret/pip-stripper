import logging

logger = logging.getLogger(__name__)

import sys
import re
import os

from traceback import print_exc as xp
import pdb

from pip_stripper.yaml_commenter import Commenter

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
    
    

    writes the results of cross-checking configuration file, grep-ed imports and
    pip freeze to pip-stripper.scan.yaml

    

    """

    def __init__(self, mgr):
        self.mgr = mgr
        self.fnp_yaml = mgr._get_fnp("scan")

        self.fnp_yaml_comments = os.path.join(
            self.mgr._get_fnp("templatedir"), "yaml_comments.yaml"
        )

    def write(self):
        try:

            pips_buckets = self.mgr.pip_classifier.di_bucket.copy()

            li_items = list(pips_buckets.items())

            for k, v in li_items:
                pips_buckets[k] = sorted(v)

                comment_key = k[:-1] + "_"
                comment_lookup = "comment_lookup_%s" % (k)

                pips_buckets[comment_key] = comment_lookup

            pips = dict(buckets=pips_buckets, freeze=self.mgr.all_freezes)

            warnings = self.mgr.pip_classifier.warnings

            di = self.di = dict(
                import_="comment_lookup_imports",
                imports=self.mgr.import_classifier.packagetracker.classify(),
                pips=pips,
                aliase_="comment_lookup_aliases",
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

            fnp_tmp = self.mgr._get_fnp("tmp")
            with open(fnp_tmp, "w", encoding="utf-8") as fo:
                dump(self.di, fo, default_flow_style=False)

            commenter = Commenter(self.fnp_yaml_comments)

            commenter.comment(fnp_tmp, self.fnp_yaml)

            print("pipstripper scan written to %s" % (self.fnp_yaml))

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
