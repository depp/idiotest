# IdioTest - idiotest/run.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest command-line interface."""
import idiotest.suite
import idiotest.env
import idiotest.console
import idiotest.sglob
import sys
import os
import optparse

def run(root='.', exec_paths=()):
    """Run the test suite, reading options from the command line.

    The root of the test suite is the directory specified by 'root',
    and the 'exec_paths' parameter specifies a list of directories to
    search for executables.
    """
    parser = optparse.OptionParser()
    parser.add_option("-w", "--wrap", dest="wrap",
                      help="wrap commands with CMD", metavar="CMD")
    parser.add_option("-e", "--err", dest="err",
                      help="send stderr to terminal",
                      action="store_true", default=False)
    parser.add_option("--exec-path", dest='exec_paths',
                      help="add PATH to search path for executables",
                      action="append", default=[])
    (options, args) = parser.parse_args()
    options.exec_paths.extend(exec_paths)
    env = idiotest.env.make_env(options)
    if args:
        filter = idiotest.sglob.SGlob(args)
    else:
        filter = None
    suite = idiotest.suite.Suite(root)
    suite.scan()
    idiotest.console.run_suite(suite, env, filter)
