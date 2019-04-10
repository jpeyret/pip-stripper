import logging

logger = logging.getLogger(__name__)

from traceback import print_exc as xp
import pdb

from pip_stripper._baseutils import cpdb, rpdb, ppp


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
