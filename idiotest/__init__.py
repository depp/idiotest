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
import idiotest.console
import sys
import os

env = {
    'fail': idiotest.fail.fail,
    'check_output': idiotest.proc.check_output,
    'get_output': idiotest.proc.get_output,
}

def run(root='.'):
    real_root = os.path.join(sys.path[0], root)
    real_root = os.path.normpath(real_root)
    suite = idiotest.suite.TestSuite(real_root, env)
    suite.scan()
    idiotest.console.run_tests(suite)
