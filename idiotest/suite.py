# IdioTest - idiotest/suite.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest test suite.

A test suite scans a directory for test files and organizes them into
a single object.  This also contains code for importing test code and
running it.
"""
import os

def relpath(basepath, path):
    if path == basepath:
        return '.'
    if path.startswith(basepath + os.path.sep):
        return path[len(basepath) + len(os.path.sep):]
    raise Exception("Path %s not a subpath of %s" %
                    (repr(path), repr(basepath)))

class Test(object):
    """A single test.
    
    Each test is executed with the current working directory set to
    the parent directory of the file containing the test.  Tests are
    assumed to be callable objects which do not take any arguments.
    """
    def __init__(self, cwd, obj):
        self.cwd = cwd
        self.obj = obj
    def run(self):
        oldcwd = os.getcwd()
        try:
            os.chdir(self.cwd)
            self.obj()
        finally:
            os.chdir(oldcwd)

class TestFile(object):
    """A single file in a test suite.
    
    Each file can contain multiple tests.  All globals in a file which
    are callable and whose names don't start with an underscore are
    assumed to be individual tests.
    """
    def __init__(self, path, env):
        self.path = path
        self.env = env
    def load(self):
        env = dict(self.env)
        execfile(self.path, env, env)
        tests = {}
        names = []
        cwd = os.path.split(self.path)[0]
        for name, obj in env.items():
            if (name not in self.env and not name.startswith('_')
                and hasattr(obj, '__call__')):
                tests[name] = Test(cwd, obj)
                names.append(name)
        names.sort()
        self.tests = tests
        self.names = names

class TestSuite(object):
    """An entire suite of tests, spread across multiple files.
    
    TestSuite(root, env): Create a new test suite, where root is the
    path of the root directory containing all the tests, and env is a
    dictionary for globals that each of the test files will be
    executed in.
    """
    def __init__(self, root, env):
        self.root = root
        self.env = env
    def scan(self):
        """Scan the root directory for test files.

        """
        testfiles = {}
        testnames = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [dirname for dirname in dirnames
                           if not dirname.startswith('.')]
            if dirpath != self.root:
                base = relpath(self.root, dirpath) \
                    .replace(os.path.sep, '.') + '.'
            else:
                base = ''
            for filename in filenames:
                if filename.endswith('.py') and not filename.startswith('.'):
                    path = os.path.join(dirpath, filename)
                    path = os.path.normpath(path)
                    if path == 'test.py':
                        # This is probably the driver script
                        continue
                    name = base + filename[:-3]
                    testnames.append(name)
                    testfiles[name] = TestFile(path, self.env)
        self.files = testfiles
        self.names = testnames
