# IdioTest - idiotest/__init__.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest test utility.

This has the main function for running an IdioTest suite of tests.
"""
__all__ = ['run', 'fail', 'suite', 'proc']
import idiotest.suite
import idiotest.fail
import idiotest.proc

env = {
    'fail': idiotest.fail.fail,
    'check_output': idiotest.proc.check_output,
    'get_output': idiotest.proc.get_output,
}

def run(root='.'):
    suite = idiotest.suite.TestSuite(root, env)
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
            except idiotest.fail.TestFailure, ex:
                print "  === FAILED ==="
                print '  ' + ex.reason
                for line in ex.message.getvalue().splitlines():
                    print '  ' + line
            else:
                print "  ok"
