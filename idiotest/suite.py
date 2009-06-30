# IdioTest - idiotest/suite.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
import os

def relpath(basepath, path):
    if path == basepath:
        return '.'
    if path.startswith(basepath) and path[len(basepath)] == os.path.sep:
        return path[len(basepath)+1:]
    raise Exception("Path %s not a subpath of %s" %
                    (repr(path), repr(basepath)))

class TestFile(object):
    def __init__(self, path):
        self.path = path

class TestSuite(object):
    def __init__(self, root):
        testfiles = {}
        testnames = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [dirname for dirname in dirnames
                           if not dirname.startswith('.')]
            if dirpath != root:
                base = relpath(root, dirpath).replace(os.path.sep, '.') + '.'
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
                    testfiles[name] = TestFile(path)
        self.testfiles = testfiles
        self.testnames = testnames
