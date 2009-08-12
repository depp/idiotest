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

def run(root='.', exec_paths=None):
    parser = optparse.OptionParser()
    parser.add_option("-w", "--wrap", dest="wrap",
                      help="wrap commands with CMD", metavar="CMD")
    parser.add_option("-e", "--err", dest="err",
                      help="send stderr to terminal",
                      action="store_true", default=False)
    (options, args) = parser.parse_args()
    if options.wrap:
        runner = idiotest.proc.ProcWrapper(options.wrap, exec_paths)
    else:
        runner = idiotest.proc.ProcRunner(exec_paths)
    runner.geterr = not options.err
    env = {
        'fail': idiotest.fail.fail,
        'check_output': runner.check_output,
        'get_output': runner.get_output,
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
