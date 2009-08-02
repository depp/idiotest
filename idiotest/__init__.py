# IdioTest - idiotest/__init__.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest test utility.

This has the main function for running an IdioTest suite of tests.
"""
__all__ = ['run', 'fail', 'suite', 'proc', 'console', 'sglob']
import idiotest.suite
import idiotest.fail
import idiotest.proc
import idiotest.console
import idiotest.sglob
import sys
import os
import optparse

def run(root='.'):
    parser = optparse.OptionParser()
    parser.add_option("-w", "--wrap", dest="wrap",
                      help="wrap commands with CMD", metavar="CMD")
    (options, args) = parser.parse_args()
    env = {
        'fail': idiotest.fail.fail,
        'check_output': idiotest.proc.check_output,
        'get_output': idiotest.proc.get_output,
        }
    if args:
        filter = idiotest.sglob.SGlob(args)
    else:
        filter = None
    real_root = os.path.join(sys.path[0], root)
    real_root = os.path.normpath(real_root)
    suite = idiotest.suite.TestSuite(real_root, env)
    suite.scan()
    idiotest.console.run_tests(suite, filter)
