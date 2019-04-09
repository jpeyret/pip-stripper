#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pip_stripper` package."""

import os
import unittest
import pdb
import sys
import shutil
from glob import glob

from pip_stripper._pip_stripper import Main, __file__ as _mainfile
from pip_stripper.matching import Matcher
from traceback import print_exc as xp

from yaml import safe_load as yload

import tempfile

undefined = object()


def build_args(**kwargs):
    pass


import pdb


def cpdb(**kwds):
    if cpdb.enabled == "once":
        cpdb.enabled = False
        return True
    return cpdb.enabled


cpdb.enabled = False


def rpdb(**kwds):
    return rpdb.enabled


rpdb.enabled = False


dn_test = os.path.dirname(__file__)

from pip_stripper._baseutils import set_cpdb, ppp, debugObject, set_rpdb


class Base(unittest.TestCase):
    testdir = None

    def write(self, msg):
        """use this to test stderr"""
        self.stderr = msg

    def setUp(self):
        """Set up test fixtures, if any."""
        self.oldpwd = os.getcwd()

        if self.testdir:
            os.chdir(self.testdir)
        self.parser = Main.getOptParser()
        self.stderr = ""

    def tearDown(self):
        """Tear down test fixtures, if any."""
        os.chdir(self.oldpwd)


class Test_Bad_options(Base):
    """Tests for `pip_stripper` package."""

    testdir = dn_test

    def test_000_badarg(self):

        try:
            with self.assertRaises(SystemExit):
                stderr = sys.stderr
                sys.stderr = self
                options = self.parser.parse_args(["-x"])
            sys.stderr = stderr
            self.assertTrue("unrecognized" in self.stderr)
        except (Exception, SystemExit) as e:
            if cpdb():
                pdb.set_trace()
            raise

    @unittest.skipUnless(1 or False, "Need to fix")
    def test_001_noconfig(self):
        try:
            options = self.parser.parse_args([])
            mgr = Main(options)
            self.fail("should have complained about missing configuration")

        except (ValueError,) as e:
            self.assertTrue("configuration file" in str(e))
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def test_002_badconfig(self):
        try:
            options = self.parser.parse_args(["--config", "notexist.yaml"])
            mgr = Main(options)
            self.fail("expected IOError")
        except (IOError,) as e:
            pass
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class WriterMixin(object):

    baseprefix = "tmp.pip_stripper"
    prefix = ""
    _testdir = None

    @property
    def testdir(self):
        if self._testdir is None:
            prefix = self.baseprefix + (".%s" % (self.prefix) if self.prefix else "")
            self._testdir = tempfile.mkdtemp(prefix=prefix)

        return self._testdir

    def seed(self):
        try:

            dn_src = os.path.join(dn_test, self.dn_seed)
            dn_tgt = os.path.join(self.testdir, "py")

            if not os.path.exists(dn_tgt):
                shutil.copytree(dn_src, dn_tgt)
            mask = os.path.join(self.testdir, "*")

            print(glob(mask))
            return dn_tgt

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class TestPip_Init(WriterMixin, Base):
    def test_001_init(self):
        try:
            print("self.testdir:%s" % (self.testdir))
            options = self.parser.parse_args(["--init"])
            mgr = Main(options)

            fnp = os.path.join(mgr.workdir, mgr.FN_CONFIG)
            with open(fnp) as fi:
                config = yload(fi)
            ppp(config)

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class TestPip_Scan(WriterMixin, Base):

    dn_seed = "tst.seedworkdir01/py"

    testdir = "/Users/jluc/kds2/issues2/067.pip-stripper/001.start"

    def setUp(self):
        super(TestPip_Scan, self).setUp()
        self.workdir = self.seed()

    def test_001_scan(self):
        try:
            options = self.parser.parse_args(["--init", "--workdir", self.workdir])
            mgr = Main(options)
            if rpdb():
                pdb.set_trace()
            mgr.process()

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class TestMatchingBase(unittest.TestCase):

    li_pip = ["cx-Oracle", "requests", "python-dateutil", "xxx"]
    li_imp = ["dateutil", "cx_Oracle", "requests", "yyy"]

    exp = {
        "cx-Oracle": "cx_Oracle",
        "requests": "requests",
        "python-dateutil": "dateutil",
    }

    def __repr__(self):
        return self.__class__.__name__

    def test(self):
        try:
            self.matcher = Matcher()
            for name in self.li_pip:
                self.matcher.pip.feed(name)
            for name in self.li_imp:
                self.matcher.imp.feed(name)

            self.matcher.do_match()

            self.assertEqual(self.exp, self.matcher.di_pip_imp)

        except (Exception,) as e:
            ppp(self.matcher, "%s.matcher" % (self))
            ppp(self.matcher.pip, "pip")
            ppp(self.matcher.imp, "imp")
            if cpdb():
                pdb.set_trace()
            raise


class TestMatchingJinja(TestMatchingBase):

    li_pip = ["Jinja2"]
    li_imp = ["jinja2"]

    exp = {"Jinja2": "jinja2"}


if __name__ == "__main__":
    # pdb.set_trace()
    set_cpdb(cpdb, remove=True)
    set_rpdb(rpdb, remove=True)

    unittest.main()
