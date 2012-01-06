# IdioTest - idiotest/suite.py
# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest test suite.

A test suite scans a directory for test files and organizes them into
a single object.  This also contains code for importing test code and
running it.
"""
import os
import sys
import idiotest.fail
import traceback

SUCCESS = 'SUCCESS'
SKIP = 'SKIP'
FAIL = 'FAIL'

def relpath(basepath, path):
    if path == basepath:
        return '.'
    if path.startswith(basepath + os.path.sep):
        return path[len(basepath) + len(os.path.sep):]
    raise Exception("Path %s not a subpath of %s" %
                    (repr(path), repr(basepath)))

class Test(object):
    """A single test."""
    def __init__(self, module, name, obj):
        self.module = module
        self.name = name
        self.obj = obj

    @property
    def fullname(self):
        return '%s.%s' % (self.module.name, self.name)

    def run(self):
        """Run test and return (status, reason).

        The status is one of SUCCESS, SKIP, or FAIL.  The reason will
        be None unless status is FAIL (you don't need a reason to
        succeed).
        """
        try:
            self.obj()
            return SUCCESS, None
        except idiotest.fail.TestFailure, ex:
            reason = '%s\n%s' % (ex.reason, ex.msg.getvalue())
            return FAIL, reason
        except KeyboardInterrupt:
            raise
        except:
            reason = traceback.format_exc()
            return FAIL, reason

class Module(object):
    """A single file in a test suite.

    Each file can contain multiple tests.
    """

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def load(self, env):
        """Load a module and return the tests.

        The 'env' specifies the global environment for loading the
        test module.  It is not modified.
        """
        testnames = set()
        tests = []
        def mktest(name, obj):
            if name in testnames:
                raise Exception('Duplicate test name: %r' % (name,))
            if not callable(obj):
                raise Exception('Test %r not callable' % (name,))
            testnames.add(name)
            tests.append(Test(self, name, obj))
            return obj
        def testdeco(param):
            """The 'test' decorator."""
            def namedeco(obj):
                return mktest(param, obj)
            if isinstance(param, basestring):
                return namedeco
            elif callable(param):
                try:
                    name = param.__name__
                except AttributeError:
                    name = repr(param)
                return mktest(name, param)
            raise Exception("invalid use of 'test' decorator")
        env = dict(env)
        env['test'] = testdeco
        execfile(self.path, env, env)
        return tests

    def context(self):
        """Return the execution context for this module.

        The context should be used in a 'with' statement and the tests
        can be executed inside the 'with' statement.
        """
        return Context(self)

class Context(object):
    def __init__(self, module):
        self.module = module
        self.cwd = os.getcwd()
    def __enter__(self):
        os.chdir(os.path.dirname(self.module.path))
    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.cwd)

class Suite(object):
    """An entire suite of tests, spread across multiple files."""

    """
    TestSuite(root, env): Create a new test suite, where root is the
    path of the root directory containing all the tests, and env is a
    dictionary for globals that each of the test files will be
    executed in.
    """

    def __init__(self, root):
        """Create a suite of tests in the directory 'root'."""
        self.root = root

    def scan(self):
        """Scan the root directory for test files."""
        modules = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [x for x in dirnames if not x.startswith('.')]
            if dirpath != self.root:
                basename = (relpath(self.root, dirpath)
                            .replace(os.path.sep, '.') + '.')
            else:
                basename = ''
            for f in filenames:
                if f.startswith('.') or not f.endswith('.py'):
                    continue
                path = os.path.join(dirpath, f)
                name = basename + f[:-3]
                modules.append(Module(name, path))
        modules.sort(key=lambda m: m.name)
        self.modules = modules
