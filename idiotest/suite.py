# IdioTest - idiotest/suite.py
# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest test suite.

A test suite scans a directory for test files and organizes them into
a single object.  This also contains code for importing test code and
running it.  A callback object is required for running tests.

A "callback object" is an object which receives results from running
tests.  It must implement the following methods:

    module_begin(module)
    module_pass(module)
    module_skip(module, reason)
    module_fail(module, reason)
    test_begin(test)
    test_pass(test)
    test_skip(test, reason)
    test_fail(test, reason)

For each module and test, the 'begin' function will be called and then
either 'pass', 'skip', or 'fail' will be called.  Note that
'module_pass' will ordinarily be called even if any or all of the
tests in the module fail.

The 'begin' function should return True if the module or test should
be run and False if it should be skipped.  If the module or test is
skipped, the 'skip' function will be called immediately.
"""
import os
import sys
import idiotest.exception
import traceback

TestException = idiotest.exception.TestException

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
    def __init__(self, module, name, test, fail=False):
        self.module = module
        self.name = name
        self.test = test
        self.fail = fail

    @property
    def fullname(self):
        return '%s.%s' % (self.module.name, self.name)

    def run(self, obj):
        """Run test and pass result to the callback object. """
        if not obj.test_begin(self):
            obj.test_skip(self, None)
            return
        try:
            self.test()
        except TestException, ex:
            if ex.module:
                raise
            if ex.skip:
                obj.test_skip(self, ex.get())
            else:
                obj.test_fail(self, ex.get())
        except KeyboardInterrupt:
            raise
        except:
            reason = traceback.format_exc()
            obj.test_fail(self, reason)
        else:
            obj.test_pass(self)

def getname(obj):
    """Get the default name for a test."""
    try:
        return obj.__name__
    except AttributeError:
        return repr(obj)

class Module(object):
    """A single file in a test suite.

    Each file can contain multiple tests.
    """

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def load(self, env):
        """Load a module and return the tests.

        Exceptions for failing or skipping the module will pass
        through here, you should call 'run' instead, which handles
        them.
        """
        testnames = set()
        tests = []
        def mktest(name, obj, **kw):
            if name in testnames:
                raise Exception('Duplicate test name: %r' % (name,))
            if not callable(obj):
                raise Exception('Test %r not callable' % (name,))
            testnames.add(name)
            tests.append(Test(self, name, obj, **kw))
            return obj
        def test(*arg, **kw):
            """Register a test.

            Can be called directly or used as a decorator.  Examples:

                test(name, obj, **kw)   # obj is callable
                @test                   # decorates a callable
                @test(**kw)             # decorates a callable
                @test(name, **kw)       # decorates a callable
            """
            if not arg:
                def deco0(obj):
                    return mktest(getname(obj), obj, **kw)
                return deco0
            elif len(arg) == 1:
                param = arg[0]
                if isinstance(param, basestring):
                    def deco1(obj):
                        return mktest(param, obj, **kw)
                    return deco1
                elif callable(param):
                    return mktest(getname(param), param, **kw)
                else:
                    raise TypeError(
                        "'test' requires either a name or callable")
            elif len(arg) == 2:
                name, obj = arg
                if not isinstance(name, basestring):
                    raise TypeError("'test' name must be a string")
                if not callable(obj):
                    raise TypeError("test must be callable")
                return mktest(name, obj, **kw)
            else:
                raise ValueError(
                    "'test' expects two or fewer positional arguments")
        env = dict(env)
        env['test'] = test
        execfile(self.path, env, env)
        return tests

    def context(self):
        """Return the execution context for this module.

        The context should be used in a 'with' statement and the tests
        can be executed inside the 'with' statement.
        """
        return Context(self)

    def run(self, obj, env):
        """Run tests in the module, passing the results to obj."""
        if not obj.module_begin(self):
            obj.module_skip(self, None)
            return
        with self.context():
            try:
                for test in self.load(env):
                    test.run(obj)
            except TestException as ex:
                if not ex.module:
                    raise
                if ex.skip:
                    obj.module_skip(self, ex.get())
                else:
                    obj.module_fail(self, ex.get())
            except KeyboardInterrupt:
                raise
            except:
                reason = traceback.format_exc()
                obj.module_fail(self, reason)
            else:
                obj.module_pass(self)

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
            absdirpath = os.path.abspath(dirpath)
            for f in filenames:
                if f.startswith('.') or not f.endswith('.py'):
                    continue
                abspath = os.path.join(absdirpath, f)
                name = basename + f[:-3]
                modules.append(Module(name, abspath))
        modules.sort(key=lambda m: m.name)
        self.modules = modules
        if not modules:
            raise Exception('No test modules were found.')

    def run(self, obj, env):
        """Run all tests in the suite, passing the results to obj."""
        for module in self.modules:
            module.run(obj, env)
