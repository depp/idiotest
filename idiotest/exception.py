# IdioTest - idiotest/fail.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest failure functions.

This has the "TestFailure" exception as well as a convenient fail()
function.
"""
ENV = ['fail', 'skip', 'fail_module', 'skip_module']
import StringIO

class TestException(Exception):
    def __init__(self, reason):
        self.reason = reason
        self.msg = StringIO.StringIO()
    def write(self, text):
        if isinstance(text, str):
            text = unicode(text)
        self.msg.write(text)
    def get(self):
        if self.reason is not None:
            return u'%s\n%s' % (unicode(self.reason), self.msg.getvalue())
        else:
            return self.msg.getvalue()

class TestFailure(TestException):
    skip = False
    module = False

class TestSkip(TestException):
    skip = True
    module = False

class ModuleFailure(TestException):
    skip = False
    module = True

class ModuleSkip(TestException):
    skip = True
    module = True

def fail(reason=None):
    """Causes the current test to fail."""
    raise TestFailure(reason)

def skip(reason=None):
    """Causes the current test to skip."""
    raise TestSkip(reason)

def fail_module(reason=None):
    """Causes the module as a whole to fail.

    If the module is still loading, then no tests are executed.  If
    the module has already loaded, all remaining tests are skipped.
    """
    raise ModuleFailure(reason)

def skip_module(reason=None):
    """Causes the module as a whole to skip.

    If the module is still loading, then no tests are executed.  If
    the module has already loaded, all remaining tests are skipped.
    """
    raise ModuleSkip(reason)

