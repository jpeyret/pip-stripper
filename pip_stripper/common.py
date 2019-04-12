import logging

logger = logging.getLogger(__name__)

import os
import subprocess

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import (
    ppp,
    debugObject,
    cpdb,
    fill_template,
    rpdb,
    sub_template,
)


def enforce_set_precedence(*sets):
    """
    given sets s1, s2, s3,  in that order
    s1 takes precedence over s2 and s3
    s2 takes precedence over s3

    -  any member already in s1 is removed from s2
    -  any member already in s1 or s2 is removed from s3
    """

    for ix, set in enumerate(sets):
        prunee = sets[ix]
        for prec_idx in range(0, ix):
            prunee -= sets[prec_idx]


class Command(object):
    def __init__(self, mgr, taskname, config):
        self.mgr = mgr
        self.taskname = taskname

        self.config = config
        self.append = self.config.get("append", False)
        self.stderr = ""

        self.mode = "a" if self.append else "w"

    def __repr__(self):
        return self.taskname

    def _subprocess(self, cmd, fnp_o, self_=None):
        try:

            fnp_stderr = self.mgr._get_fnp("log")
            with open(fnp_stderr, "a") as ferr:

                ferr.write("cmd: %s\nstderr begin:\n" % (cmd))

                with open(fnp_o, self.mode) as fo:
                    proc = subprocess.check_call(
                        cmd.split(), stdout=fo, stderr=ferr, cwd=self.mgr.workdir
                    )
                ferr.write("stderr end\n\n")

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    _subprocess_actual = _subprocess

    def run(self):
        try:
            t_cmd = self.config["cmdline"]  # .replace(r"\\","\\")
            t_fnp = os.path.join(self.mgr.workdir, self.config["filename"])

            fnp_log = "subprocess.log"

            cmd = sub_template(t_cmd, self, self.mgr.vars)

            fnp_o = sub_template(t_fnp, self, self.mgr.vars)
            self._subprocess(cmd=cmd, fnp_o=fnp_o, self_=self)

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise
