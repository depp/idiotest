# IdioTest - idiotest/__init__.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
__all__ = ['run']
import idiotest.suite

def run(root='.'):
    suite = idiotest.suite.TestSuite(root)
    for test in suite.testnames:
        print(test)
