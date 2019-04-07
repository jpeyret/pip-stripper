#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pip_stripper` package."""

import os
import unittest
import pdb
import sys

from pip_stripper._pip_stripper import Main
from traceback import print_exc as xp

from yaml import safe_load as yload

def build_args(**kwargs):
    pass

import pdb

def cpdb(**kwds):
    if cpdb.enabled == "once":
        cpdb.enabled = False
        return True
    return cpdb.enabled
cpdb.enabled = False

dn_work = os.path.dirname(__file__)
print("dn_work:%s" % (dn_work))

from pip_stripper._baseutils import set_cpdb, ppp, debugObject

class Base(unittest.TestCase):
    testdir = None

    def write(self, msg):
        """use this to test stderr"""
        self.stderr = msg

    def setUp(self):
        """Set up test fixtures, if any."""
        self.oldpwd = os.getcwd()

        if self.testdir:
            self.testdir = os.path.join(dn_work, self.testdir)

        os.chdir(self.testdir or dn_work)
        self.parser = Main.getOptParser()
        self.stderr = ""


    def tearDown(self):
        """Tear down test fixtures, if any."""
        os.chdir(self.oldpwd)

class Test_Bad_options(Base):
    """Tests for `pip_stripper` package."""

    def test_000_badarg(self):

        try:
            with self.assertRaises(SystemExit):
                stderr = sys.stderr 
                sys.stderr = self
                options = self.parser.parse_args(["-x"])
            sys.stderr = stderr
            self.assertTrue("unrecognized" in self.stderr)
        except (Exception,SystemExit) as e:
            if cpdb(): 
                pdb.set_trace()
            raise

    def test_001_noconfig(self):
        try:
            options = self.parser.parse_args([])
            mgr = Main(options)
            self.fail("should have complained about missing configuration")

        except (ValueError,) as e:
            self.assertTrue("configuration file" in str(e))
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    def test_002_badconfig(self):
        try:
            options = self.parser.parse_args(["--config", "notexist.yaml"])
            mgr = Main(options)
            self.fail("expected IOError")
        except (IOError,) as e:
            pass
        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

class TestPip_Init(Base):

    testdir = "tst.init"

    def test_001_init(self):
        try:
            options = self.parser.parse_args(["--init"])       
            mgr = Main(options)

            fnp = os.path.join(mgr.workdir, mgr.FN_CONFIG)
            with open(fnp) as fi:
                config = yload(fi)
            



        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise


if __name__ == '__main__':
    # pdb.set_trace()
    set_cpdb(cpdb, remove=True)
    # pdb.set_trace()

    unittest.main()