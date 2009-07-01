# IdioTest - idiotest/__init__.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest test utility.

This has the main function for running an IdioTest suite of tests.
"""
__all__ = ['run']
import idiotest.suite

def run(root='.'):
    suite = idiotest.suite.TestSuite(root, {})
    suite.scan()
    for filename in suite.names:
        print filename
        file = suite.files[filename]
        file.load()
        for testname in file.names:
            test = file.tests[testname]
            print testname
            try:
                test.run()
            except Exception, ex:
                print "FAILED: %s" % str(ex)
            else:
                print "ok"
