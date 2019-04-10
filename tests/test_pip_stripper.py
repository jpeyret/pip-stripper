#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pip_stripper` package."""

import os
import unittest
import pdb
import sys
import shutil
from glob import glob

from pip_stripper._pip_stripper import Main, __file__ as _mainfile, Command
from pip_stripper.matching import Matcher
from pip_stripper.common import enforce_set_precedence
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

FN_IMPORTS_GREP = "tmp.pip-stripper.imports.rpt"
FN_SCAN = "pip-stripper.scan.yaml"
BASEPREFIX = "tmp.pip_stripper"


class Base(unittest.TestCase):
    testdir = None

    def write(self, msg):
        """use this to test stderr"""
        self.stderr = msg

    def set_testdirbase(self):
        try:
            Base.testdir_base = testdir_base = os.getenv("pip_stripper_testdir")
            if testdir_base:

                if not os.path.exists(testdir_base):
                    os.makedirs(testdir_base)
            else:
                Base.testdir_base = tempfile.mkdtemp(prefix=prefix)
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def setUp(self):
        """Set up test fixtures, if any."""

        self.testdir_base = (
            getattr(self, "testdir_base", None) or self.set_testdirbase()
        )

        self.oldpwd = os.getcwd()

        if self.testdir:
            os.chdir(self.testdir)
        self.parser = Main.getOptParser()
        self.stderr = ""

    def tearDown(self):
        """Tear down test fixtures, if any."""
        os.chdir(self.oldpwd)

    def get_label(self):
        sself = "%s" % (self)
        method_, class_ = sself.split()
        class_ = class_.split(".")[1][:-1]

        return "%s.%s" % (class_, method_)


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

    baseprefix = BASEPREFIX
    prefix = ""
    _testdir = None

    @property
    def testdir(self):
        if self._testdir is None:
            # pdb.set_trace()
            testdir = os.path.join(Base.testdir_base, self.get_label())
            if not os.path.exists(testdir):
                os.makedirs(testdir)

            self.__class__._testdir = testdir

        return self._testdir

    def seed(self):
        try:

            dn_src = os.path.join(dn_test, self.dn_seed)
            dn_tgt = os.path.join(self.testdir, "py")

            if not os.path.exists(dn_tgt):
                shutil.copytree(dn_src, dn_tgt)
            # mask = os.path.join(self.testdir, "*")

            # print(glob(mask))
            return dn_tgt

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def has_run(self, fn_marker=None):
        try:
            fn_marker = fn_marker or self.fn_marker
            fnp_marker = os.path.join(self.testdir, fn_marker)
            return os.path.exists(fnp_marker)

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def get_file(self, fn, mode="r"):
        try:
            fnp = os.path.join(self.mgr.workdir, fn)
            return open(fnp, mode)
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class BaseCommand(WriterMixin, Base):
    def setUp(self):
        try:
            super(BaseCommand, self).setUp()
            options = self.parser.parse_args(["--init", "--workdir", self.testdir])

            self.mgr = Main(options)
            self.config = self.mgr.config["Command"]["tasks"][self.taskname]
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def test_run(self):
        try:
            command = Command(self.mgr, self.taskname, self.config)
            command.run()
            from time import sleep

            sleep(3)
            fnp = self.mgr._get_fnp(self.taskname)
            with open(fnp) as fi:
                data = fi.read()
                self.assertTrue(data, "%s was empty" % (fnp))

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class TestCommandFreeze(BaseCommand):
    taskname = "freeze"


class TestCommandPipDepTree(BaseCommand):
    taskname = "pipdeptree"


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


class BasePip_Scan(WriterMixin, Base):
    pass

    # this is used to run scan only once
    fn_marker = FN_SCAN

    def setUp(self):
        super(BasePip_Scan, self).setUp()
        self.workdir = self.seed()

    def get_options(self):
        return self.parser.parse_args(["--init", "--workdir", self.workdir])

    def test_001_scan(self):
        try:
            options = self.get_options()
            self.mgr = Main(options)
            if rpdb():
                pdb.set_trace()
            self.mgr.process()

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def test_002_greps(self):
        try:
            if not self.has_run():
                self.test_001_scan()

            with self.get_file(FN_IMPORTS_GREP) as fi:
                data = fi.read()

            for import_ in self.exp_imports:
                self.assertTrue(
                    import_ in data, "missing %s from %s" % (import_, FN_IMPORTS_GREP)
                )

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise


class TestPip_Scan(BasePip_Scan):

    dn_seed = "tst.seedworkdir01/py"

    # celery is a from-only, django is an import-only
    exp_imports = ["jinja2", "django", "celery"]


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


class TestSetPrecedence(Base):
    def test_001_std(self):
        try:
            prod = set("prod")
            tests = set("tests")
            dev = set("dev")

            exp = dict(prod=set("prod"), tests=set("tes"), dev=set("v"))

            enforce_set_precedence(prod, tests, dev)

            got = dict(prod=prod, tests=tests, dev=dev)

        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    def test_002_only_dev(self):
        try:
            prod = set("")
            tests = set("")
            dev = set("dev")

            exp = dict(prod=set(""), tests=set(""), dev=set("dev"))

            enforce_set_precedence(prod, tests, dev)

            got = dict(prod=prod, tests=tests, dev=dev)

        except (Exception,) as e:
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
